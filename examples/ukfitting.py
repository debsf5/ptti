import matplotlib.pyplot as plt
import numpy as np
import csv
import time

from ptti.seirct_ode import SEIRCTODEMem
from ptti.model import runModel

def uk_mortality(fn):
    def read_csv():
        with open(fn) as fp:
            for date, deaths_Economist, deaths_Excess in csv.reader(fp, delimiter=','):
                if date == "date": ## header
                    continue
                date = time.strptime(date, "%d/%m/%Y")
                deaths_Economist, deaths_Excess = int(deaths_Economist), int(deaths_Excess)
                yield (date.tm_yday, deaths_Economist, deaths_Excess)
    return np.array(list(read_csv()))

# uk_mortality data starts on 1st Jan 2020,
# deaths_Economist first deaths 7th March (t=66)
# deaths_Excess first deaths 5th March (t=64)

t0, tmax, steps = -14, 127, 141  # Day 0 is 1st Jan 2020, -14 is 18th Dec 2019
    # simulation runs from 1st Jan to 8th May (t=128)
ifr = 0.008
offset = 0 ## date offset for uk case data

initial = {
    "N": 67886011,
    "IU": 2,
}

params = {
    "beta":  0.0375,
    "c":     13,
    "alpha": 0.2,
    "gamma": 0.1429,
    "theta": 0.0,
}

interventions = [
    { "time": 75, "parameters": { "c": 10 } },  # 16th March 2020 voluntary distancing
    { "time": 82, "parameters": { "c": 4 } }    # 23rd March 2020 lockdown
]

model = SEIRCTODEMem
t, traj, events = runModel(model, t0, tmax, steps, params, initial, interventions)
RU = traj[:, model.colindex("RU")]
RD = traj[:, model.colindex("RD")]
t += offset
cases = RU + RD
deaths = ifr * cases

ukm = uk_mortality("uk_mortality.csv")
ukt = ukm[:,0]
ukdeaths_Economist = ukm[:,1]
ukdeaths_Excess = ukm[:,2]

fig, (ax1, ax2) = plt.subplots(2, 1)

ax1.set_xlabel("Days since outbreak start")
ax1.set_ylabel("Cases")
ax1.set_xlim(t0, tmax)
ax1.set_yscale("log")
ax1.plot(t, cases, label="Simulated")
ax1.plot(ukt, ukcases, label="UK data")
ax1.legend()

ax2.set_xlabel("Days since outbreak start")
ax2.set_ylabel("Deaths")
ax2.set_xlim(t0, tmax)
#ax2.set_yscale("log")
ax2.plot(t, deaths, label="Simulated")
ax2.plot(ukt, ukdeaths_Economist, label="UK deaths - Economist")
ax2.plot(ukt, ukdeaths_Excess, label="UK deaths - Excess")
ax2.legend()

fig.show()

input()
