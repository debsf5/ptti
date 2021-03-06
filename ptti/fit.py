import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from ptti.config import config_load, save_human
from ptti.model import runModel
from ptti.seirct_ode import SEIRCTODEMem
import urllib.request
import gzip
import logging
import argparse
import sys
import os
import csv
import time

log = logging.getLogger(__name__)

def _getter(p):
   def _f(cfg):
      return cfg["parameters"][p]
   return _f
def _setter(p):
   def _f(cfg, v):
      cfg["parameters"][p] = v
   return _f
def _igetter(i, p):
   def _f(cfg):
      return cfg["interventions"][i]["parameters"][p]
   return _f
def _isetter(i, p):
   def _f(cfg, v):
      cfg["interventions"][i]["parameters"][p] = v
   return _f
def _tgetter(i):
   def _f(cfg):
      return cfg["interventions"][i]["time"]
   return _f
def _tsetter(i):
   def _f(cfg, t):
      cfg["interventions"][i]["time"] = t
   return _f

def paramArray(cfg, masked=[]):
   """
   This is a little obscure, but it returns a function to get them
   elements of the config that it is permitted to change as an array,
   and given such an array sets the corresponding elements of the
   config. That way we can take gradients relative to parameters
   that live in the wooly yaml.
   """
   param_funcs = []

   for p in cfg.get("parameters", {}).keys():
      if p in masked: continue
      param_funcs.append((_getter(p), _setter(p)))

   for i, intv in enumerate(i for i in cfg.get("interventions", []) if "time" in i):
#      param_funcs.append((_tgetter(i), _tsetter(i)))
      for p in intv.get("parameters", {}).keys():
         if p in masked: continue
         param_funcs.append((_igetter(i,p), _isetter(i,p)))

   getp = lambda cfg: np.array(list(g(cfg) for (g, _) in param_funcs))
   _ev  = lambda fv: fv[0][1](fv[0][0], fv[1])
   setp = lambda cfg, a: list(map(_ev, zip([(cfg, s) for (_, s) in param_funcs], a)))
   return getp, setp

def dgu_cases(fn):
   """
   Read coronavirus cases for the UK as published by data.gov.uk

   https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=overview&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newCasesBySpecimenDate%22:%22newCasesBySpecimenDate%22,%22cumCasesBySpecimenDate%22:%22cumCasesBySpecimenDate%22%7D&format=csv
   """
   def read_csv():
      with open(fn) as fp:
         for atype, aname, acode, date, cases, ccases in csv.reader(fp, delimiter=','):
            if "area" in aname: ## header
               continue
            if acode != "K02000001": ## UK, not devolved nations
               continue
            date = time.strptime(date, "%Y-%m-%d")
            cases  = int(cases) if cases != "" else 0
            ccases = int(ccases) if ccases != "" else 0
            yield (date.tm_yday, cases, ccases)
   return np.array(list(read_csv()))[::-1]

def dgu(fn):
   """
   Read coronavirus deaths for the UK as published by data.gov.uk

   https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=overview&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newDeaths28DaysByDeathDate%22:%22newDeaths28DaysByDeathDate%22,%22cumDeaths28DaysByDeathDate%22:%22cumDeaths28DaysByDeathDate%22%7D&format=csv
   """
   url = "https://api.coronavirus.data.gov.uk/v1/data?filters=areaType=overview&structure=%7B%22areaType%22:%22areaType%22,%22areaName%22:%22areaName%22,%22areaCode%22:%22areaCode%22,%22date%22:%22date%22,%22newDeaths28DaysByDeathDate%22:%22newDeaths28DaysByDeathDate%22,%22cumDeaths28DaysByDeathDate%22:%22cumDeaths28DaysByDeathDate%22%7D&format=csv"
   try:
       os.stat(fn)
   except IOError:
       req = urllib.request.Request(url)
       with urllib.request.urlopen(req) as response:
           gzdata = response.read()
       data = gzip.decompress(gzdata)
       with open(fn, 'wb') as f:
           f.write(data)
   def read_csv():
      with open(fn) as fp:
         for atype, aname, acode, date, dead, cdead in csv.reader(fp, delimiter=','):
            if "area" in aname: ## header
               continue
            if acode != "K02000001": ## UK, not devolved nations
               continue
            date = time.strptime(date, "%Y-%m-%d")
            deaths = int(cdead) if cdead != "" else 0
            yield (date.tm_yday, deaths)
   return np.array(list(read_csv()))[::-1]

def data(fn):
   """
   Read generic data in (YYYY-MM-DD, dead) format
   """
   def read_csv():
      with open(fn) as fp:
         for date, dead in csv.reader(fp, delimiter=','):
            try:
               date = time.strptime(date, "%Y-%m-%d")
            except ValueError:
               continue
            deaths = int(dead)
            yield (date.tm_yday, deaths)
   return np.array(list(read_csv()))

def optimise(cfg, getm, setp, p0, times, dead, interventions):
   def obj(x):
      ## we do not allow negative parameters, very bad
      if np.any(x[1:] < 0):
         return np.inf

      ## set time
      t0 = x[0]
      cfg["meta"]["t0"] = t0

      ## register interventions against the reference times
      def regiv(iv):
         niv = iv.copy()
         niv["time"] += t0
         return niv
      cfg["interventions"] = [regiv(iv) for iv in interventions]

      ## set the parameters
      setp(cfg, x[1:])

      ## run the model
      t, traj, _, _ = runModel(**cfg["meta"], **cfg)
      M = interp1d(t, getm(traj), kind="previous",  bounds_error=False,
                   fill_value=0)(times)

      ## measure the result
      dist = np.sqrt(np.sum((M-dead)**2, where=dead >= 0))
      log.info("Distance: {}".format(dist))
      return dist

   p0 = np.hstack([[0.0], p0])
   fit = minimize(obj, p0, method='nelder-mead',
                  options={'xatol': 1e-8, 'disp': True})

   log.info("Fitting complete:\n{}".format(fit))

   return fit.x[0], fit.x[1:]

def command():
   logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                      format='%(asctime)s - %(name)s:%(levelname)s - %(message)s')

   parser = argparse.ArgumentParser("fit")
   parser.add_argument("-y", "--yaml", default=None, help="Config file")
   parser.add_argument("-m", "--mask", nargs="*", default=[], help="Variables to mask")
   parser.add_argument("-e", "--end", default=None, help="Truncate the data at end date")
   parser.add_argument("-t", "--time", default=0, type=float, help="Shift dataset time by given amount")
   parser.add_argument("--dgu", default=None, help="coronavirus.data.gov.uk format for the dead\n\t\thttps://coronavirus.data.gov.uk/downloads/csv/coronavirus-deaths_latest.csv")
   parser.add_argument("--data", default=None, help="generic YYYY-MM-DD,dead format for data")

   args = parser.parse_args()

   if args.yaml is None:
      log.error("--yaml is a required argument")

   dead = None
   if args.data:
      dead = data(args.data)
   elif args.dgu:
      dead = dgu(args.dgu)

   if dead is None:
      log.error("There are no dead. Need a data file of some sort")

   if args.end:
      end = time.strptime(args.end, "%Y-%m-%d")
      idx = np.sum(dead[:,0] <= end.tm_yday)
      dead = dead[:idx]

   cfg = config_load(args.yaml)
   model = SEIRCTODEMem
   cfg["meta"]["model"] = model

   def getm(traj):
      return traj[:,model.colindex("M")]
   getp, setp = paramArray(cfg, args.mask)

   ## the times of the dead
   dead_t = dead[:,0] + args.time
   ## these are the actual counts of the dead
   dead_d = dead[:,1]

   ## this is the last day of data
   tmax  = max(dead_t)
   ## one output point per day
   steps = int(tmax)
   ## we want a time-series of
   times = np.linspace(0, tmax, steps)
   ## interpolate the dead onto this time support
   dead_i = interp1d(dead_t, dead_d, kind="previous", bounds_error=False,
                     fill_value=np.nan)(times)

   ## set to run for the specific required time at the specific step
   cfg["meta"]["tmax"] = tmax
   cfg["meta"]["steps"] = steps+1

   interventions = cfg.get("interventions", [])

   ## perform a stochastic gradient descent
   t0, params = optimise(cfg, getm, setp, getp(cfg), times, dead_i, interventions)
   cfg["meta"]["t0"] = t0
   setp(cfg, params)

   save_human(cfg, "{}-fit.yaml".format(cfg["meta"]["output"]))

   t, traj, _, _ = runModel(**cfg["meta"], **cfg)
   M = getm(traj)

   fig, (ax1, ax2) = plt.subplots(2, 1)

   ax1.set_xlabel("Days since outbreak start")
   ax1.set_ylabel("Cumulative infections")
   ax1.set_xlim(0, tmax)
   ax1.plot(t, M, label="Simulated")
   ax1.plot(times, dead_i, label="Data")
   for e in interventions:
      ax1.axvline(e["time"], c=(0, 0, 0), lw=0.5, ls='--')
   ax1.legend()

   ax2.set_xlabel("Days since outbreak start")
   ax2.set_ylabel("Cumulative infections")
   ax2.set_xlim(0, tmax)
   ax2.set_yscale("log")
   ax2.plot(t, M, label="Simulated")
   ax2.plot(times, dead_i, label="Data")
   for e in interventions:
      ax2.axvline(e["time"], c=(0, 0, 0), lw=0.5, ls='--')
   ax2.legend()

   plt.savefig("{}-fit.png".format(cfg["meta"]["output"]))

if __name__ == '__main__':
   command()
