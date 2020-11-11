econ_inputs = {}

# Parameters
# econ_inputs['Population'] = 67886011 # From scenario

econ_inputs['Shutdown'] = dict()
econ_inputs['Shutdown']['UK_Shutdown_GDP_Penalty'] = 0.25  # How much economic damage is happening.
econ_inputs['Shutdown']['UK_Open_Contacts'] = 11  # baseline pre-pandemic (ref Polymod, UK only, & BBC Pandemic)
econ_inputs['Shutdown']['UK_Shutdown_Contacts'] = 11 * 0.3  # Shutdown level
econ_inputs['Shutdown']['UK_GDP_Monthly'] = 186000000000


# We will (potentially) model several possible interventions, with different costs.
# Tracing alone, universal testing + tracing, or partial / scaled testing + tracing.
# In each case, we need to compute costs from

econ_inputs['Trace'] = dict()
econ_inputs['Trace']['Time_to_Trace_Contact'] = 37.8 / 30.0  
    # 1.26 hours to trace each contact: 37.8 hours to trace 30 contacts (see Table B of PTTI draft report

econ_inputs['Trace']['Duplicated_Contacts'] = 2 # The daily contacts should be the unique contacts, so we remove repeat contacts

# Hire_Interval = 90 # Now Unused

# Variable Tracing Costs
econ_inputs['Trace']['Phone_Credit_Costs'] = 5 # Daily, per person.

# Max_Number_of_Tracers = UK_Population/1000
econ_inputs['Trace']['Cost_per_Tracer'] = 0
econ_inputs['Trace']['Tracer_Salary'] = 80  # Daily
econ_inputs['Trace']['Cost_per_Tracer'] += econ_inputs['Trace']['Tracer_Salary']
# We need to add the *daily* cost for other factors
econ_inputs['Trace']['Cost_per_Tracer'] += econ_inputs['Trace']['Phone_Credit_Costs'] # Add phone costs

# Number_of_Tracing_Supervisors = Max_Number_of_Tracers/50
econ_inputs['Trace']['Tracing_Supervisor_Salary'] = 160  # Daily
econ_inputs['Trace']['Tracers_Per_Supervisor'] = 50  # Daily
econ_inputs['Trace']['Number_of_Tracing_Team_Leads'] = 343
econ_inputs['Trace']['Team_Lead_Salary'] = 300  # Daily

econ_inputs['Trace']['Hiring_Cost'] = 200  # £200 per recruitment for advertisements, phone interviews, salary of recruiters

econ_inputs['Trace']['Tracer_Training_Course_Cost'] = 72000  # Three training courses (including refreshers) one for each staff cadre
econ_inputs['Trace']['Tracer_Contract_Length'] = 30*3 # Length of window over which tracers are hired


# Tracers_Day_N = Max_Number_of_Tracers # This can vary. Set to max for now. (This is overridden in the econ model now.)
# We assume supervisors and team leads are employed the entire time we do this, regardless of varying number of tracers.

econ_inputs['Trace']['Tracing_App_Development_Deployment'] = 10000000  # ball park estimate of developing, maintenance & running app for 1 year

econ_inputs['Trace']['Cost_Per_Extra_Phones_for_Tracers'] = 200  # For any tracers without phones / replacements.
econ_inputs['Trace']['Tracer_Percentage_Needing_Phones'] = 0.1  # Fairly small percentage.
#econ_inputs['Trace']['Tracers_Per_Infected_Person'] = 58.0/8 # See report - 58 hours, tracers work 8 hour days.

econ_inputs['Trace']['Rural_Pct'] = 0.17
econ_inputs['Trace']['Daily_Travel_Cost'] = 10
# Travelers = (Max_Number_of_Tracers * Rural_Pct) + Number_of_Tracing_Supervisors + Number_of_Tracing_Team_Leads

econ_inputs['Trace']['Tracing_Daily_Public_Communications_Costs'] = 100000 #Messaging, etc.


# Testing Costs

# PCR Machine Capabilities

econ_inputs['Test'] = dict()

econ_inputs['Test']['PCR_Machines_Per_Lab'] = 10
econ_inputs['Test']['Shifts_per_Day'] = 2
econ_inputs['Test']['Hours_per_Shift'] = 9
econ_inputs['Test']['Time_per_Batch'] = 0.5  # Half Hour batches
econ_inputs['Test']['Tests_per_Batch'] = 96
econ_inputs['Test']['Tests_per_Machine_per_Hour'] = econ_inputs['Test']['Tests_per_Batch'] / econ_inputs['Test']['Time_per_Batch']
econ_inputs['Test']['Tests_per_Machine_per_Shift'] = econ_inputs['Test']['Tests_per_Machine_per_Hour'] * econ_inputs['Test']['Hours_per_Shift']
econ_inputs['Test']['Tests_per_Machine_per_Day'] = econ_inputs['Test']['Tests_per_Machine_per_Shift'] * econ_inputs['Test']['Shifts_per_Day']

econ_inputs['Test']['Lab_Techs_Per_Machine_Per_Shift'] = 2 # One to run the test, one to fill the wells.
econ_inputs['Test']['Tester_Contract_Length'] = 30*6 # Length of window over which lab technicians are hired


#Personnel Costs
# Moved to Econ Model
# Lab_supervisors	= Needed_Labs
# Max_Lab_Techs = Needed_PCR_Machines * Lab_Techs_Per_Machine_Per_Shift * Shifts_per_Day
# Lab_staff_trainings = Max_Lab_Techs + Lab_supervisors # Retrainings every 3 months?

econ_inputs['Test']['Lab_Tech_Salary'] = 200  # Per Shift
econ_inputs['Test']['Lab_Supervisor_Salary'] = 300  # Per Day
econ_inputs['Test']['Staff_Training_Cost'] = 200  # Trainings / retrainings every Period, per person.

econ_inputs['Test']['Cost_Per_PCR_Test'] = 4.5  # 3.50 for testing supplies, 0.50 for mail out, 0.50 for courier to lab.


# Setup / Fixed Costs
econ_inputs['Test']['Lab_Overhead_Cost_Daily'] = 500  # Estimated cost of £500 per day per lab for 289 labs with 10 RT LAMP PCR machines each
econ_inputs['Test']['PCR_Machines_Cost'] = 27000 #  Roche COBAS 8800 Machines, as suggested by: https://www.bmj.com/content/368/bmj.m1163
econ_inputs['Test']['PCR_Machine_Daily_Maintenance'] = 10  # assume maintenance costs averaging £10 per day


econ_inputs['Medical'] = dict() #Based on 20,133 Cases - Docherty et al BMJ 2020 https://www.bmj.com/content/bmj/369/bmj.m1985.full.pdf
econ_inputs['Medical']['ICU_Pct'] = 0.15
econ_inputs['Medical']['ICU_Fatality'] = 0.537
econ_inputs['Medical']['Non_ICU_Fatality'] = 0.363  # 4207 deaths out of 11580 non-ongoing no-ICU hospital cases

econ_inputs['Medical']['Hospitalized_Pct_Deaths'] = 0.60  # The percentage of deaths that occur in hospitals 

econ_inputs['Medical']['IFR'] = 0.011

# Based on Spreadsheet from v1.
econ_inputs['Medical']['NHS_Death_Cost'] = 500
# From a comment from Manuel Gomes on the paper: "The uni cost is:
# XC04Z Adult Critical Care, 3 Organs Supported £1,582.03
# Using the NHS cost inflation published below, the actual value should be ~£1675
# https://www.pssru.ac.uk/pub/uc/uc2019/sources-of-information.pdf"
econ_inputs['Medical']['NHS_ICU_Cost'] = 8*1675 # 8 days median stay in ICU (ICNARC data)
econ_inputs['Medical']['NHS_Hospital_Cost'] = 2422


#econ_inputs['Medical']['Productivity_Not_Working_Cost'] = 119
#econ_inputs['Medical']['Productivity_Death_Cost'] = 357 # 3 days at £119 per day
#econ_inputs['Medical']['Productivity_ICU_Cost'] = 2499  # 21 days at £119 per day
#econ_inputs['Medical']['Productivity_Hospital_Cost'] = 1190 # 10 days at £119 per day
#econ_inputs['Medical']['Productivity_Symptomatic_Cost'] = 357 # 3 days at £119 per day
econ_inputs['Medical']['Pct_Symptomatic'] = 0.5

################ DERIVED QUANTITIES - Do not touch these ###########

econ_inputs['Trace']['Supervisor_Daily_Cost'] = (econ_inputs['Trace']['Tracing_Supervisor_Salary'] +
                                                 econ_inputs['Trace']['Phone_Credit_Costs'] +
                                                 econ_inputs['Trace']['Daily_Travel_Cost'])
econ_inputs['Trace']['Total_Team_Lead_Daily_Cost'] = (econ_inputs['Trace']['Number_of_Tracing_Team_Leads'] *
                                                      (econ_inputs['Trace']['Team_Lead_Salary'] +
                                                       econ_inputs['Trace']['Phone_Credit_Costs'] +
                                                       econ_inputs['Trace']['Daily_Travel_Cost']))
econ_inputs['Trace']['Tracer_Daily_Cost'] = (econ_inputs['Trace']['Tracer_Salary'] +
                                             econ_inputs['Trace']['Phone_Credit_Costs'] +
                                             econ_inputs['Trace']['Daily_Travel_Cost'] * econ_inputs['Trace']['Rural_Pct'])
econ_inputs['Trace']['Tracer_Initial_Cost'] = (econ_inputs['Trace']['Hiring_Cost'] +
                                               econ_inputs['Trace']['Tracer_Training_Course_Cost'] +
                                               econ_inputs['Trace']['Cost_Per_Extra_Phones_for_Tracers'])


econ_inputs['Test']['Lab_Peaktest_Ratio'] = 1.0/(econ_inputs['Test']['Tests_per_Machine_per_Day']*econ_inputs['Test']['PCR_Machines_Per_Lab'])
econ_inputs['Test']['Techs_Per_Lab'] = (econ_inputs['Test']['PCR_Machines_Per_Lab'] * econ_inputs['Test']['Shifts_per_Day'] * 
                                               econ_inputs['Test']['Lab_Techs_Per_Machine_Per_Shift'])
econ_inputs['Test']['Lab_Techs_Daily_Cost'] = (econ_inputs['Test']['Techs_Per_Lab'] * econ_inputs['Test']['Lab_Tech_Salary'])
econ_inputs['Test']['Lab_NonTechs_Daily_Cost'] = (econ_inputs['Test']['Lab_Overhead_Cost_Daily'] + 
                                               econ_inputs['Test']['Lab_Supervisor_Salary'] + 
                                               econ_inputs['Test']['PCR_Machines_Per_Lab']*econ_inputs['Test']['PCR_Machine_Daily_Maintenance'])
econ_inputs['Test']['Lab_Total_Daily_Cost'] = econ_inputs['Test']['Lab_Techs_Daily_Cost']+econ_inputs['Test']['Lab_NonTechs_Daily_Cost']
econ_inputs['Test']['Lab_Startup_Cost'] = ((econ_inputs['Test']['Techs_Per_Lab'] + 2)*(econ_inputs['Trace']['Hiring_Cost']+econ_inputs['Test']['Staff_Training_Cost']) +
                                            econ_inputs['Test']['PCR_Machines_Cost']*econ_inputs['Test']['PCR_Machines_Per_Lab'])   # +2 is for two supervisors per lab, one for each 9hr shift

econ_inputs['Medical']['Hospitalised_Fraction'] = (econ_inputs['Medical']['Hospitalized_Pct_Deaths']*econ_inputs['Medical']['IFR'] / 
                                                    (econ_inputs['Medical']['ICU_Pct']*econ_inputs['Medical']['ICU_Fatality'] +
                                                    (1-econ_inputs['Medical']['ICU_Pct']) * econ_inputs['Medical']['Non_ICU_Fatality'])
                                                   )
econ_inputs['Medical']['ICU_Fraction'] = econ_inputs['Medical']['Hospitalised_Fraction']*econ_inputs['Medical']['ICU_Pct']

econ_inputs['Medical']['Total_NHS_Cost_Per_Recovered'] = (econ_inputs['Medical']['IFR']*econ_inputs['Medical']['NHS_Death_Cost'] + 
                                                          econ_inputs['Medical']['ICU_Fraction']*econ_inputs['Medical']['NHS_ICU_Cost'] +
                                                          econ_inputs['Medical']['Hospitalised_Fraction']*econ_inputs['Medical']['NHS_Hospital_Cost'])


#econ_inputs['Medical']['Total_Productivity_Loss_Per_Recovered'] = (econ_inputs['Medical']['IFR']* econ_inputs['Medical']['Productivity_Death_Cost'] +
#                                                                   econ_inputs['Medical']['ICU_Fraction']*econ_inputs['Medical']['Productivity_ICU_Cost'] +
#                                                                   econ_inputs['Medical']['Hospitalised_Fraction']*econ_inputs['Medical']['Productivity_Hospital_Cost'] +
#                                                                  econ_inputs['Medical']['Pct_Symptomatic'] * econ_inputs['Medical']['Productivity_Symptomatic_Cost'])

