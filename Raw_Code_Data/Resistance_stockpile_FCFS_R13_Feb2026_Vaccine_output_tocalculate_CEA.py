# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 16:51:08 2026

@author: chenr
"""


"""
Change parameter:
#The probability of treatment rate
u = 1

#Time of vaccine availabe
t <= 240

#Basic reproduction number (R0)
R0 = 1.5 / 2.0 / 3.0 
beta_assum = 0.105 / 0.14 / 0.21

#Treament rate #u = np.array([0.93, 0.79, 0]) # Treatment rate = np.array([0.07, 0.21, 1])
HR ratio in different age groups:
0-18:7%
19-64:21%
65+:100%

#First come, firtst serve. u = 0 else u = 1

"""



import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
from scipy.interpolate import interp1d

# Define the parameters
N = np.array([914120, 4863980, 1756100])
#N = np.array([914120-914120*0.613, 4863980-4863980*0.148, 1756100-1756100*0.509])
sum(N)
n = np.array([[3.061728,3.823045,0.230453],
              [0.68895,5.843111,0.3397],
              [0.256098,4.804878,1.768293]])

# 设置总药物库存量
TOTAL_ANTIVIRAL_STOCK = 1100000  # 1,110,000剂
antiviral_used = 0
treatment_active = True
time_drug_exhausted = None

# Antiviral treatment - Baloxaivr, Oseltamivir, Zanamivir
# Beta_Su: 0-18, 19-64, 65+ = 1 : 0.510 : 0.087
"""
drugs_distribution = {'BXM': 0.9, 
                      'OTV': 0.1, 
                      'ZNV': 0.0} # BXM + OTV + ZNV = 1
"""

relative_Resistance_transmissin = 0.9

# ============ 生成66种药物分布组合 ============
def generate_drug_combinations():
    combinations = []
    for bxm in np.arange(0, 1.1, 0.1):
        bxm = round(bxm, 1)
        for otv in np.arange(0, 1.1 - bxm, 0.1):
            otv = round(otv, 1)
            znv = round(1.0 - bxm - otv, 1)
            if znv >= 0:
                combinations.append((bxm, otv, znv))
    return combinations

# 所有66种组合
all_drug_combinations = generate_drug_combinations()
print(f"总共有 {len(all_drug_combinations)} 种药物分布组合")

# 存储结果的列表
results = []


# Hospitalization Incidence OTV,ZNV vs. BXM https://pmc.ncbi.nlm.nih.gov/articles/PMC8423480/#s6
drugs = {
    'BXM':  {
        'transmission_efficacy': np.array([0.29, 0.29, 0.29]), # Reduce to transmission
        'Resistance_susceptibility_antiviral': np.array([1/2, 1/2, 1/2]), # If resistance emergance, the affect to drug efficacy.
        #'relative_Resistance_transmissin': np.array([0.9, 0.9, 0.9]), # Fitness cost=10%.
        'prob_resistance': np.array([0.1, 0.05, 0.02]), # The probability of resistance
        'prob_hospitalization': np.array([0.29, 0.29, 0.29]), # Reduce to hospitalization
        'duration_recovery': np.array([1/3.1, 1/3.1, 1/3.1]), # Reduce to duration of recovery
        'duration_recovery_resistance': np.array([1/3.44, 1/3.44, 1/3.44]) # Resistance affect to reduce recovery duration
            },
    'OTV':  {
        'transmission_efficacy': np.array([0.11, 0.11, 0.11]), #If resistance emergance, the affect to drug efficacy.
        'Resistance_susceptibility_antiviral': np.array([1/2, 1/2, 1/2]), # If resistance emergance, the affect to drug efficacy.
        #'relative_Resistance_transmissin': np.array([0.9, 0.9, 0.9]), # Fitness cost=10%.
        'prob_resistance': np.array([0.05, 0.02, 0.01]), # The probability of resistance
        'prob_hospitalization': np.array([0.23, 0.23, 0.23]), # Reduce to hospitalization
        'duration_recovery': np.array([1/3.6, 1/3.6, 1/3.6]), # Reduce to duration of recovery
        'duration_recovery_resistance': np.array([0.25, 0.25, 0.25]) # Resistance affect to reduce recovery duration
            },
    'ZNV':  {
        'transmission_efficacy': np.array([0.02, 0.02, 0.02]), # Reduce to transmission
        'Resistance_susceptibility_antiviral': np.array([1/2, 1/2, 1/2]), # If resistance emergance, the affect to drug efficacy.
        #'relative_Resistance_transmissin': np.array([0.9, 0.9, 0.9]), # Fitness cost=10%.
        'prob_resistance': np.array([0.005, 0.005, 0.005]), # The probability of resistance
        'prob_hospitalization': np.array([0.18, 0.18, 0.18]), # [muply] Reduce to hospitalization
        'duration_recovery': np.array([1/3.5, 1/3.5, 1/3.5]), # [Time] Reduce to duration of recovery
        'duration_recovery_resistance': np.array([0.25, 0.25, 0.25]) # Resistance affect to reduce recovery duration
            }
    }

# Other parameters (fixed or with initial guesses)
p = np.array([1/3, 1/3, 1/3])
sigma = np.array([1/1.25, 1/1.25, 1/1.25])
sigma_a = np.array([1/1.25, 1/1.25, 1/1.25])
gamma_a = np.array([1/4.1, 1/4.1, 1/4.1])
lambda_ = np.array([1/0.25, 1/0.25, 1/0.25])
lambda_t = np.array([1/1.25, 1/1.25, 1/1.25])
lambda_t_R = np.array([1/2.25, 1/2.25, 1/2.25])
#u = np.array([0.1, 0.1, 0.1])
#u = np.array([0, 0, 0])
u = 0
#u = np.array([0.93, 0.79, 0]) # Treatment rate = np.array([0.07, 0.21, 1])

# The probability of hospitalizaiton after treatment/resistance
h_u = np.array([5.40458e-02/7, 0.006, 5.55933e-02/7])

# h_t = h_u
# h_tr= h_u

h_t = {
       'BXM': h_u * (1 - drugs['BXM']['prob_hospitalization']),
       'OTV': h_u * (1 - drugs['OTV']['prob_hospitalization']),
       'ZNV': h_u * (1 - drugs['ZNV']['prob_hospitalization'])
       }
h_tr = {
        'BXM': h_u * (1 - drugs['BXM']['prob_hospitalization'] * drugs['BXM']['Resistance_susceptibility_antiviral']),
        'OTV': h_u * (1 - drugs['OTV']['prob_hospitalization'] * drugs['OTV']['Resistance_susceptibility_antiviral']),
        'ZNV': h_u * (1 - drugs['ZNV']['prob_hospitalization'] * drugs['ZNV']['Resistance_susceptibility_antiviral'])
       }

omega_u = np.array([1/2, 1/2, 1/2])
omega_t = np.array([1/2, 1/2, 1/2])
omega_tr = np.array([1/2, 1/2, 1/2])

# The duration of recovery after treatment/resistance
gamma_u = np.array([1/4.1, 1/4.1, 1/4.1])
# gamma_t = np.array([1/3.6, 1/3.6, 1/3.6])
# gamma_tr = np.array([1/4, 1/4, 1/4])
gamma_t = {
    'BXM': drugs['BXM']['duration_recovery'],
    'OTV': drugs['OTV']['duration_recovery'],
    'ZNV': drugs['ZNV']['duration_recovery']
    }

gamma_tr = {
    'BXM': drugs['BXM']['duration_recovery_resistance'],
    'OTV': drugs['OTV']['duration_recovery_resistance'],
    'ZNV': drugs['ZNV']['duration_recovery_resistance']    
    }

# Joseph T. Wu -- Case-hospitalization rate = 0.73%
# Joseph T. Wu -- Case-fatality rate = 4.4 (per 100000 infections)
# Joseph T. Wu -- Hospitaization-fatality rate = 26/4253 = 0.006113331765812368
# death/hospitalization age = 0.00047, 0.011, 0.03
d = np.array([0.00047, 0.014392991, 0.03])
gamma_h = np.array([1/5.0, 1/5.0, 1/5.0])
xi = np.array([1/15.0, 1/15.0, 1/15.0])

#c = np.array([0.01, 0.01, 0.01])
#c = np.array([0.18, 0.18, 0.18])
# Treatment-specific equations
c_BXM = drugs['BXM']['prob_resistance']
c_OTV = drugs['OTV']['prob_resistance']
c_ZNV = drugs['ZNV']['prob_resistance']

# Vaccination parameters
#alpha = np.array([1/365, 1/365, 1/365])
alpha = np.array([0, 0, 0])
v = np.array([0, 0, 0])

# Derived transmission rates
# Beta_Su: 0-18, 19-64, 65+ = 1 : 0.510 : 0.08
# R0=2.05

#R0=1.5
#beta_assum=0.105
#R0=2.0
#beta_assum=0.14
#R0=3.0
beta_assum=0.21
age_suscep = np.array([1, 0.510, 0.08])
beta_Su = age_suscep * beta_assum
beta_Ra = 0.5 * beta_Su * relative_Resistance_transmissin
beta_Rp = 0.5 * beta_Su * relative_Resistance_transmissin
beta_Ru = beta_Su * relative_Resistance_transmissin
#beta_Rt = beta_Su * (1-0.11*0.5)
beta_Rt = {
    'BXM': beta_Su * (1 - drugs['BXM']['transmission_efficacy'] * drugs['BXM']['Resistance_susceptibility_antiviral']),
    'OTV': beta_Su * (1 - drugs['OTV']['transmission_efficacy'] * drugs['OTV']['Resistance_susceptibility_antiviral']),
    'ZNV': beta_Su * (1 - drugs['ZNV']['transmission_efficacy'] * drugs['ZNV']['Resistance_susceptibility_antiviral'])
    }

#beta_RAtB = beta_Su * (1-0.11) * 0.9
beta_RAtB = {
    'BXM': beta_Su * (1 - drugs['BXM']['transmission_efficacy']) * relative_Resistance_transmissin,
    'OTV': beta_Su * (1 - drugs['OTV']['transmission_efficacy']) * relative_Resistance_transmissin,
    'ZNV': beta_Su * (1 - drugs['ZNV']['transmission_efficacy']) * relative_Resistance_transmissin
    }

#beta_Rrt = beta_Su * (1 - 0.11 * beta_Su)
beta_Rrt = {
    'BXM': beta_Su * (1 - drugs['BXM']['transmission_efficacy'] * drugs['BXM']['Resistance_susceptibility_antiviral']),
    'OTV': beta_Su * (1 - drugs['OTV']['transmission_efficacy'] * drugs['OTV']['Resistance_susceptibility_antiviral']),
    'ZNV': beta_Su * (1 - drugs['ZNV']['transmission_efficacy'] * drugs['ZNV']['Resistance_susceptibility_antiviral'])
    }
beta_RH = np.zeros((3,3))

beta_Sa = 0.5 * beta_Su
beta_Sp = 0.5 * beta_Su
#beta_St = 0.89 * beta_Su
beta_St = {
    'BXM': beta_Su * (1 - drugs['BXM']['transmission_efficacy']), 
    'OTV': beta_Su * (1 - drugs['OTV']['transmission_efficacy']),
    'ZNV': beta_Su * (1 - drugs['ZNV']['transmission_efficacy'])
    }

beta_SH_S = np.zeros((3,3))

# Initial conditions
#S0 = np.array([914120-914120*0.613, 4863980-4863980*0.148, 1756100-1756100*0.509])
#V0 = np.array([914120*0.613, 4863980*0.148, 1756100*0.509])
S0 = np.array([914120-914120*0, 4863980-4863980*0, 1756100-1756100*0])
V0 = np.array([914120*0, 4863980*0, 1756100*0])
#E_R0 = np.array([0, 0, 0])
E_R_BXM0 = np.array([0, 0, 0])
E_R_OTV0 = np.array([0, 0, 0])
E_R_ZNV0 = np.array([0, 0, 0])

#I_Ra0 = np.array([0, 0, 0])
I_R_BXM_a0 = np.array([0, 0, 0])
I_R_OTV_a0 = np.array([0, 0, 0])
I_R_ZNV_a0 = np.array([0, 0, 0])

#I_Rp0 = np.array([0, 0, 0])
I_R_BXM_p0 = np.array([0, 0, 0])
I_R_OTV_p0 = np.array([0, 0, 0])
I_R_ZNV_p0 = np.array([0, 0, 0])

#I_Ru0 = np.array([0, 0, 0])
I_R_BXM_u0 = np.array([0, 0, 0])
I_R_OTV_u0 = np.array([0, 0, 0])
I_R_ZNV_u0 = np.array([0, 0, 0])

#I_Rt0 = np.array([0, 0, 0])
#I_Rt_BXM0=np.array([0, 0, 0])
I_R_BXM_t_BXM0=np.array([0, 0, 0])
I_R_BXM_t_OTV0=np.array([0, 0, 0])
I_R_BXM_t_ZNV0=np.array([0, 0, 0])

#I_Rt_OTV0=np.array([0, 0, 0])
I_R_OTV_t_BXM0=np.array([0, 0, 0])
I_R_OTV_t_OTV0=np.array([0, 0, 0])
I_R_OTV_t_ZNV0=np.array([0, 0, 0])

#I_Rt_ZNV0=np.array([0, 0, 0])
I_R_ZNV_t_BXM0=np.array([0, 0, 0])
I_R_ZNV_t_OTV0=np.array([0, 0, 0])
I_R_ZNV_t_ZNV0=np.array([0, 0, 0])

H_R0 = np.array([0, 0, 0])

E_S0 = np.array([0, 0, 0])
I_Sa0 = np.array([0, 0, 0])
I_Sp0 = np.array([0, 0, 0])
I_Su0 = np.array([2, 1, 1])
#I_St0 = np.array([0, 0, 0])
I_St_BXM0=np.array([0, 0, 0])
I_St_OTV0=np.array([0, 0, 0])
I_St_ZNV0=np.array([0, 0, 0])

#I_Rrt0 = np.array([0, 0, 0])
I_Rrt_BXM0=np.array([0, 0, 0])
I_Rrt_OTV0=np.array([0, 0, 0])
I_Rrt_ZNV0=np.array([0, 0, 0])

H_S0 = np.array([0, 0, 0])
D0 = np.array([0, 0, 0])
R0 = np.array([0, 0, 0])

y0 = np.concatenate([S0, V0, 
                     E_R_BXM0, E_R_OTV0, E_R_ZNV0,
                     I_R_BXM_a0, I_R_OTV_a0, I_R_ZNV_a0,
                     I_R_BXM_p0, I_R_OTV_p0, I_R_ZNV_p0,
                     I_R_BXM_u0, I_R_OTV_u0, I_R_ZNV_u0,
                     I_R_BXM_t_BXM0, I_R_BXM_t_OTV0, I_R_BXM_t_ZNV0,
                     I_R_OTV_t_BXM0, I_R_OTV_t_OTV0, I_R_OTV_t_ZNV0,
                     I_R_ZNV_t_BXM0, I_R_ZNV_t_OTV0,  I_R_ZNV_t_ZNV0, 
                     H_R0, 
                     E_S0, I_Sa0, I_Sp0, I_Su0, 
                     I_St_BXM0, I_St_OTV0, I_St_ZNV0, 
                     I_Rrt_BXM0, I_Rrt_OTV0, I_Rrt_ZNV0, 
                     H_S0, D0, R0])

# Time span for simulation
t_span = (0, 501)
#t_eval = np.linspace(0, 101, 1)
t_eval = np.arange(0, 501, 1)

# Modify the seir_model function to track incidence
def seir_model_with_incidence(t, y):
    global antiviral_used, treatment_active, time_drug_exhausted
    global vaccine_stopped_time
    
    
    # Unpack the state variables
    S = y[0:3]
    V = y[3:6]
    E_R_BXM = y[6:9]
    E_R_OTV = y[9:12]
    E_R_ZNV = y[12:15]
    I_R_BXM_a = y[15:18]
    I_R_OTV_a = y[18:21]
    I_R_ZNV_a = y[21:24]
    I_R_BXM_p = y[24:27]
    I_R_OTV_p = y[27:30]
    I_R_ZNV_p = y[30:33]
    I_R_BXM_u = y[33:36]
    I_R_OTV_u = y[36:39]
    I_R_ZNV_u = y[39:42]
    I_R_BXM_t_BXM = y[42:45]
    I_R_BXM_t_OTV = y[45:48]
    I_R_BXM_t_ZNV = y[48:51]
    I_R_OTV_t_BXM = y[51:54]
    I_R_OTV_t_OTV = y[54:57]
    I_R_OTV_t_ZNV = y[57:60]
    I_R_ZNV_t_BXM = y[60:63]
    I_R_ZNV_t_OTV = y[63:66]
    I_R_ZNV_t_ZNV = y[66:69]
    H_R = y[69:72]
    E_S = y[72:75]
    I_Sa = y[75:78]
    I_Sp = y[78:81]
    I_Su = y[81:84]
    I_St_BXM = y[84:87]
    I_St_OTV = y[87:90]
    I_St_ZNV = y[90:93]
    I_Rrt_BXM = y[93:96]
    I_Rrt_OTV = y[96:99]
    I_Rrt_ZNV = y[99:102]
    H_S = y[102:105]
    D = y[105:108]
    R = y[108:111]

    # Additional variables to track incidence
    if len(y) > 111:
        cumul_incidence_R = y[111:114]
        cumul_incidence_S = y[114:117]
        cumul_treated = y[117:120]
        cumul_hos = y[120:123]
        cumul_vaccine = y[123:126]
    else:
        cumul_incidence_R = np.zeros(3)
        cumul_incidence_S = np.zeros(3)
        cumul_treated = np.zeros(3)
        cumul_hos = np.zeros(3)
        cumul_vaccine = np.zeros(3)
        
    # Force non-negativity
    S = np.maximum(S,0)
    V = np.maximum(V,0)
    E_R_BXM = np.maximum(E_R_BXM,0)
    E_R_OTV = np.maximum(E_R_OTV,0)
    E_R_ZNV = np.maximum(E_R_ZNV,0)
    I_R_BXM_a = np.maximum(I_R_BXM_a,0)
    I_R_OTV_a = np.maximum(I_R_OTV_a,0)
    I_R_ZNV_a = np.maximum(I_R_ZNV_a,0)
    I_R_BXM_p = np.maximum(I_R_BXM_p,0)
    I_R_OTV_p = np.maximum(I_R_OTV_p,0)
    I_R_ZNV_p = np.maximum(I_R_ZNV_p,0)
    I_R_BXM_u = np.maximum(I_R_BXM_u,0)
    I_R_OTV_u = np.maximum(I_R_OTV_u,0)
    I_R_ZNV_u = np.maximum(I_R_ZNV_u,0)
    I_R_BXM_t_BXM = np.maximum(I_R_BXM_t_BXM,0)
    I_R_BXM_t_OTV = np.maximum(I_R_BXM_t_OTV,0)
    I_R_BXM_t_ZNV = np.maximum(I_R_BXM_t_ZNV,0)
    I_R_OTV_t_BXM = np.maximum(I_R_OTV_t_BXM,0)
    I_R_OTV_t_OTV = np.maximum(I_R_OTV_t_OTV,0)
    I_R_OTV_t_ZNV = np.maximum(I_R_OTV_t_ZNV,0)
    I_R_ZNV_t_BXM = np.maximum(I_R_ZNV_t_BXM,0)
    I_R_ZNV_t_OTV = np.maximum(I_R_ZNV_t_OTV,0)
    I_R_ZNV_t_ZNV = np.maximum(I_R_ZNV_t_ZNV,0)
    H_R = np.maximum(H_R,0)
    E_S = np.maximum(E_S,0)
    I_Sa = np.maximum(I_Sa,0)
    I_Sp = np.maximum(I_Sp,0)
    I_Su = np.maximum(I_Su,0)
    I_St_BXM = np.maximum(I_St_BXM,0)
    I_St_OTV = np.maximum(I_St_OTV,0)
    I_St_ZNV = np.maximum(I_St_ZNV,0)
    I_Rrt_BXM = np.maximum(I_Rrt_BXM,0)
    I_Rrt_OTV = np.maximum(I_Rrt_OTV,0)
    I_Rrt_ZNV = np.maximum(I_Rrt_ZNV,0)
    H_S = np.maximum(H_S,0)
    D = np.maximum(D,0)
    R = np.maximum(R,0)


    # Force of infection for each age group
    f_R_BXM=np.sum((beta_Ra*n)*(I_R_BXM_a/N),axis=1)+\
            np.sum((beta_Rp*n)*(I_R_BXM_p/N),axis=1)+\
            np.sum((beta_Ru*n)*(I_R_BXM_u/N),axis=1)+\
            np.sum((beta_Rt['BXM']*n)*(I_R_BXM_t_BXM/N),axis=1)+\
            np.sum((beta_RAtB['OTV']*n)*(I_R_BXM_t_OTV/N),axis=1)+\
            np.sum((beta_RAtB['ZNV']*n)*(I_R_BXM_t_ZNV/N),axis=1)+\
            np.sum((beta_Rrt['BXM']*n)*(I_Rrt_BXM/N),axis=1)

    f_R_OTV=np.sum((beta_Ra*n)*(I_R_OTV_a/N),axis=1)+\
            np.sum((beta_Rp*n)*(I_R_OTV_p/N),axis=1)+\
            np.sum((beta_Ru*n)*(I_R_OTV_u/N),axis=1)+\
            np.sum((beta_RAtB['BXM']*n)*(I_R_OTV_t_BXM/N),axis=1)+\
            np.sum((beta_Rt['OTV']*n)*(I_R_OTV_t_OTV/N),axis=1)+\
            np.sum((beta_RAtB['ZNV']*n)*(I_R_OTV_t_ZNV/N),axis=1)+\
            np.sum((beta_Rrt['OTV']*n)*(I_Rrt_OTV/N),axis=1)

    f_R_ZNV=np.sum((beta_Ra*n)*(I_R_ZNV_a/N),axis=1)+\
            np.sum((beta_Rp*n)*(I_R_ZNV_p/N),axis=1)+\
            np.sum((beta_Ru*n)*(I_R_ZNV_u/N),axis=1)+\
            np.sum((beta_RAtB['BXM']*n)*(I_R_ZNV_t_BXM/N),axis=1)+\
            np.sum((beta_RAtB['OTV']*n)*(I_R_ZNV_t_OTV/N),axis=1)+\
            np.sum((beta_Rt['ZNV']*n)*(I_R_ZNV_t_ZNV/N),axis=1)+\
            np.sum((beta_Rrt['ZNV']*n)*(I_Rrt_ZNV/N),axis=1)
       
    f_S=np.sum((beta_Sa*n)*(I_Sa/N),axis=1)+\
        np.sum((beta_Sp*n)*(I_Sp/N),axis=1)+\
        np.sum((beta_Su*n)*(I_Su/N),axis=1)+\
        np.sum((beta_St['BXM']*n)*(I_St_BXM/N),axis=1)+\
        np.sum((beta_St['OTV']*n)*(I_St_OTV/N),axis=1)+\
        np.sum((beta_St['ZNV']*n)*(I_St_ZNV/N),axis=1)

    # Calculate new infections
    new_infections_R = (f_R_BXM+f_R_OTV+f_R_ZNV) * S
    new_infections_R_BXM = f_R_BXM * S
    new_infections_R_OTV = f_R_OTV * S
    new_infections_R_ZNV = f_R_ZNV * S
    new_infections_S = f_S * S

    
    # ============ 药物库存管理逻辑 ============
    # 计算当前累计已使用药物
    current_antiviral_used = np.sum(cumul_treated)
    
    # 计算剩余库存
    remaining_stock = TOTAL_ANTIVIRAL_STOCK - current_antiviral_used
    
    # 检查药物是否已经耗尽
    if remaining_stock <= 0:
        if treatment_active and time_drug_exhausted is None:
            time_drug_exhausted = t
            treatment_active = False
            print(f"抗病毒药物在第 {t:.0f} 天耗尽, 累计使用: {current_antiviral_used:.0f}")
        u_current = 1.0  # 药物耗尽，无治疗
    else:
        # 计算当前时间步需要的治疗量
        needed_treatments_R = np.sum((1 - np.array([0, 0, 0])) * lambda_ * 
                                   (I_R_BXM_p + I_R_OTV_p + I_R_ZNV_p))
        needed_treatments_S = np.sum((1 - np.array([0, 0, 0])) * lambda_ * I_Sp)
        needed_treatments_total = needed_treatments_R + needed_treatments_S
        
        # 如果需求超过剩余库存，按比例减少治疗
        if needed_treatments_total > remaining_stock:
            scale_factor = remaining_stock / needed_treatments_total
            u_current = 1 - (1 - np.array([0, 0, 0])) * scale_factor
            #u_current = 1
            if treatment_active:
                treatment_active = False
                time_drug_exhausted = t
                print(f"抗病毒药物在第 {t:.0f} 天部分耗尽, 按比例治疗, 累计使用: {current_antiviral_used:.0f}")
        else:
            u_current = np.array([0, 0, 0])
    
    # 计算实际的新治疗人数
    new_treatments_R = (1 - u_current) * lambda_ * (I_R_BXM_p + I_R_OTV_p + I_R_ZNV_p)
    new_treatments_S = (1 - u_current) * lambda_ * I_Sp
    total_new_treatments = np.sum(new_treatments_R) + np.sum(new_treatments_S)

    # ============ 疫苗接种逻辑 ============
    # Time for vaccine availble
    if t <= 120:
        v = np.array([0, 0, 0])   
        alpha = np.array([0, 0, 0])
    
    else:    
        total_new_infections = np.sum(new_infections_R) + np.sum(new_infections_S)
        if total_new_infections < 1:
            v = np.array([0, 0, 0])
            alpha = np.array([1/365, 1/365, 1/365])
            # 记录疫苗接种停止的时间（只记录第一次）
            if 'vaccine_stopped_time' not in globals() or vaccine_stopped_time is None:
                vaccine_stopped_time = t
                print(f"Vaccination stopped at day {t:.1f} due to low new infections: {total_new_infections:.6f}")
        else:
            v = np.array([0.9*(1/365), 0.95*(1/365), 0.75*(1/365)])
            alpha = np.array([1/365, 1/365, 1/365])

    # Differential equations
    dSdt = alpha * V - v * S - (new_infections_R + new_infections_S)
    dVdt = v * S - alpha * V
    
    dE_R_BXMdt = new_infections_R_BXM - ((1 - p) * sigma + p * sigma_a) * E_R_BXM
    dE_R_OTVdt = new_infections_R_OTV - ((1 - p) * sigma + p * sigma_a) * E_R_OTV
    dE_R_ZNVdt = new_infections_R_ZNV - ((1 - p) * sigma + p * sigma_a) * E_R_ZNV  
    
    dI_R_BXM_adt = p * sigma_a * E_R_BXM - gamma_a * I_R_BXM_a
    dI_R_OTV_adt = p * sigma_a * E_R_OTV - gamma_a * I_R_OTV_a
    dI_R_ZNV_adt = p * sigma_a * E_R_ZNV - gamma_a * I_R_ZNV_a
    
    dI_R_BXM_pdt = (1 - p) * sigma * E_R_BXM - lambda_ * I_R_BXM_p
    dI_R_OTV_pdt = (1 - p) * sigma * E_R_OTV - lambda_ * I_R_OTV_p
    dI_R_ZNV_pdt = (1 - p) * sigma * E_R_ZNV - lambda_ * I_R_ZNV_p
    
    dI_R_BXM_udt = u_current * lambda_ * I_R_BXM_p - (h_u * omega_u + (1 - h_u) * gamma_u) * I_R_BXM_u
    dI_R_OTV_udt = u_current * lambda_ * I_R_OTV_p - (h_u * omega_u + (1 - h_u) * gamma_u) * I_R_OTV_u
    dI_R_ZNV_udt = u_current * lambda_ * I_R_ZNV_p - (h_u * omega_u + (1 - h_u) * gamma_u) * I_R_ZNV_u
    
    dI_R_BXM_t_BXMdt = (drugs_distribution['BXM']*(1-u_current)*lambda_*I_R_BXM_p - \
                  (h_tr['BXM']*omega_tr + (1-h_tr['BXM'])*gamma_tr['BXM'])*I_R_BXM_t_BXM)
    dI_R_BXM_t_OTVdt = (drugs_distribution['OTV']*(1-u_current)*lambda_*I_R_BXM_p - \
                  (h_t['OTV']*omega_t + (1-h_t['OTV'])*gamma_t['OTV'])*I_R_BXM_t_OTV)
    dI_R_BXM_t_ZNVdt = (drugs_distribution['ZNV']*(1-u_current)*lambda_*I_R_BXM_p - \
                  (h_t['ZNV']*omega_t + (1-h_t['ZNV'])*gamma_t['ZNV'])*I_R_BXM_t_ZNV)
    
    dI_R_OTV_t_BXMdt = (drugs_distribution['BXM']*(1-u_current)*lambda_*I_R_OTV_p - \
                  (h_t['BXM']*omega_t + (1-h_t['BXM'])*gamma_t['BXM'])*I_R_OTV_t_BXM)   
    dI_R_OTV_t_OTVdt = (drugs_distribution['OTV']*(1-u_current)*lambda_*I_R_OTV_p - \
                  (h_tr['OTV']*omega_tr + (1-h_tr['OTV'])*gamma_tr['OTV'])*I_R_OTV_t_OTV)
    dI_R_OTV_t_ZNVdt = (drugs_distribution['ZNV']*(1-u_current)*lambda_*I_R_OTV_p - \
                  (h_t['ZNV']*omega_t + (1-h_t['ZNV'])*gamma_t['ZNV'])*I_R_OTV_t_ZNV) 

    dI_R_ZNV_t_BXMdt = (drugs_distribution['BXM']*(1-u_current)*lambda_*I_R_ZNV_p - \
                  (h_t['BXM']*omega_t + (1-h_t['BXM'])*gamma_t['BXM'])*I_R_ZNV_t_BXM)
    dI_R_ZNV_t_OTVdt = (drugs_distribution['OTV']*(1-u_current)*lambda_*I_R_ZNV_p - \
                  (h_t['OTV']*omega_t + (1-h_t['OTV'])*gamma_t['OTV'])*I_R_ZNV_t_OTV)
    dI_R_ZNV_t_ZNVdt = (drugs_distribution['ZNV']*(1-u_current)*lambda_*I_R_ZNV_p - \
                  (h_tr['ZNV']*omega_tr + (1-h_tr['ZNV'])*gamma_tr['ZNV'])*I_R_ZNV_t_ZNV)
    
    dH_Rdt=h_u*omega_u*I_R_BXM_u + h_u*omega_u*I_R_OTV_u + h_u*omega_u*I_R_ZNV_u +\
        h_tr['BXM']*omega_tr*I_R_BXM_t_BXM +\
        h_t['OTV']*omega_t*I_R_BXM_t_OTV +\
        h_t['ZNV']*omega_t*I_R_BXM_t_ZNV +\
        h_t['BXM']*omega_t*I_R_OTV_t_BXM +\
        h_tr['OTV']*omega_tr*I_R_OTV_t_OTV +\
        h_t['ZNV']*omega_t*I_R_OTV_t_ZNV +\
        h_t['BXM']*omega_t*I_R_ZNV_t_BXM +\
        h_t['OTV']*omega_t*I_R_ZNV_t_OTV +\
        h_tr['ZNV']*omega_tr*I_R_ZNV_t_ZNV -\
        ((1-d)*gamma_h+d*xi)*H_R  
     
    dE_Sdt = new_infections_S - ((1 - p) * sigma + p * sigma_a) * E_S
    dI_Sadt = p * sigma_a * E_S - gamma_a * I_Sa
    dI_Spdt = (1 - p) * sigma * E_S - lambda_ * I_Sp
    
    dI_Sudt = u_current * lambda_ * I_Sp - ((1 - h_u) * gamma_u + h_u * omega_u) * I_Su   
    
    dI_St_BXMdt = drugs_distribution['BXM']*(1-u_current)*(1-c_BXM)*lambda_*I_Sp - \
                 (h_t['BXM']*omega_t + (1-h_t['BXM'])*gamma_t['BXM'])*I_St_BXM
    dI_St_OTVdt = drugs_distribution['OTV']*(1-u_current)*(1-c_OTV)*lambda_*I_Sp - \
                 (h_t['OTV']*omega_t + (1-h_t['OTV'])*gamma_t['OTV'])*I_St_OTV 
    dI_St_ZNVdt = drugs_distribution['ZNV']*(1-u_current)*(1-c_ZNV)*lambda_*I_Sp - \
                 (h_t['ZNV']*omega_t + (1-h_t['ZNV'])*gamma_t['ZNV'])*I_St_ZNV   
   
    
    dI_Rrt_BXMdt = drugs_distribution['BXM']*(1-u_current)*c_BXM*lambda_*I_Sp - \
                 ((1 - h_tr['BXM']) * gamma_tr['BXM'] + h_tr['BXM'] * omega_tr) * I_Rrt_BXM
    dI_Rrt_OTVdt = drugs_distribution['OTV']*(1-u_current)*c_OTV*lambda_*I_Sp - \
                 ((1 - h_tr['OTV']) * gamma_tr['OTV'] + h_tr['OTV'] * omega_tr) * I_Rrt_OTV    
    dI_Rrt_ZNVdt = drugs_distribution['ZNV']*(1-u_current)*c_ZNV*lambda_*I_Sp - \
                 ((1 - h_tr['ZNV']) * gamma_tr['ZNV'] + h_tr['ZNV'] * omega_tr) * I_Rrt_ZNV    

    
    dH_Sdt = h_u * omega_u * I_Su + \
                h_t['BXM'] * omega_t * I_St_BXM + h_t['OTV'] * omega_t * I_St_OTV + h_t['ZNV'] * omega_t * I_St_ZNV + \
                h_tr['BXM'] * omega_tr * I_Rrt_BXM + h_tr['OTV'] * omega_tr * I_Rrt_OTV + h_tr['ZNV'] * omega_tr * I_Rrt_ZNV - \
                ((1 - d) * gamma_h + d * xi) * H_S
    
    dDdt = d * xi * H_R + d * xi * H_S
    
    dRdt = gamma_a * (I_R_BXM_a + I_R_OTV_a + I_R_ZNV_a) + \
            (1 - h_u) * gamma_u * (I_R_BXM_u + I_R_OTV_u + I_R_ZNV_u) + \
            (1-h_tr['BXM'])*gamma_tr['BXM']*I_R_BXM_t_BXM + \
            (1-h_t['OTV'])*gamma_t['OTV']*I_R_BXM_t_OTV + \
            (1-h_t['ZNV'])*gamma_t['ZNV']*I_R_BXM_t_ZNV + \
            (1-h_t['BXM'])*gamma_t['BXM']*I_R_OTV_t_BXM + \
            (1-h_tr['OTV'])*gamma_tr['OTV']*I_R_OTV_t_OTV + \
            (1-h_t['ZNV'])*gamma_t['ZNV']*I_R_OTV_t_ZNV + \
            (1-h_t['BXM'])*gamma_t['BXM']*I_R_ZNV_t_BXM + \
            (1-h_t['OTV'])*gamma_t['OTV']*I_R_ZNV_t_OTV + \
            (1-h_tr['ZNV'])*gamma_tr['ZNV']*I_R_ZNV_t_ZNV + \
            (1 - d) * gamma_h * H_R + \
            gamma_a * I_Sa + \
            (1 - h_u) * gamma_u * I_Su + \
            (1-h_t['BXM'])*gamma_t['BXM']*I_St_BXM+(1-h_t['OTV'])*gamma_t['OTV']*I_St_OTV+(1-h_t['ZNV'])*gamma_t['ZNV']*I_St_ZNV + \
            (1 - h_tr['BXM']) * gamma_tr['BXM'] * I_Rrt_BXM+(1 - h_tr['OTV']) * gamma_tr['OTV'] * I_Rrt_OTV+(1 - h_tr['ZNV']) * gamma_tr['ZNV'] * I_Rrt_ZNV + \
            (1 - d) * gamma_h * H_S

    
    # Differential equations for cumulative incidence and treated
    dcumul_incidence_Rdt = new_infections_R
    dcumul_incidence_Sdt = new_infections_S
    dcumul_treateddt =  new_treatments_R + new_treatments_S
    dcumul_hosdt = h_u*omega_u*I_R_BXM_u + h_u*omega_u*I_R_OTV_u + h_u*omega_u*I_R_ZNV_u +\
                h_tr['BXM']*omega_tr*I_R_BXM_t_BXM +\
                h_t['OTV']*omega_t*I_R_BXM_t_OTV +\
                h_t['ZNV']*omega_t*I_R_BXM_t_ZNV +\
                h_t['BXM']*omega_t*I_R_OTV_t_BXM +\
                h_tr['OTV']*omega_tr*I_R_OTV_t_OTV +\
                h_t['ZNV']*omega_t*I_R_OTV_t_ZNV +\
                h_t['BXM']*omega_t*I_R_ZNV_t_BXM +\
                h_t['OTV']*omega_t*I_R_ZNV_t_OTV +\
                h_tr['ZNV']*omega_tr*I_R_ZNV_t_ZNV +\
                h_u * omega_u * I_Su + \
                h_t['BXM'] * omega_t * I_St_BXM + h_t['OTV'] * omega_t * I_St_OTV + h_t['ZNV'] * omega_t * I_St_ZNV + \
                h_tr['BXM'] * omega_tr * I_Rrt_BXM + h_tr['OTV'] * omega_tr * I_Rrt_OTV + h_tr['ZNV'] * omega_tr * I_Rrt_ZNV 
    
    dcumul_vaccinedt = v * S
    
    return np.concatenate([dSdt,dVdt,dE_R_BXMdt,dE_R_OTVdt,dE_R_ZNVdt,
                           dI_R_BXM_adt,dI_R_OTV_adt,dI_R_ZNV_adt,
                           dI_R_BXM_pdt,dI_R_OTV_pdt,dI_R_ZNV_pdt,
                           dI_R_BXM_udt,dI_R_OTV_udt,dI_R_ZNV_udt,
                           dI_R_BXM_t_BXMdt,dI_R_BXM_t_OTVdt,dI_R_BXM_t_ZNVdt,
                           dI_R_OTV_t_BXMdt,dI_R_OTV_t_OTVdt,dI_R_OTV_t_ZNVdt,
                           dI_R_ZNV_t_BXMdt,dI_R_ZNV_t_OTVdt,dI_R_ZNV_t_ZNVdt,
                           dH_Rdt,dE_Sdt,dI_Sadt,dI_Spdt,dI_Sudt,
                           dI_St_BXMdt,dI_St_OTVdt,dI_St_ZNVdt,
                           dI_Rrt_BXMdt,dI_Rrt_OTVdt,dI_Rrt_ZNVdt,dH_Sdt,dDdt,dRdt,
                           dcumul_incidence_Rdt, dcumul_incidence_Sdt, dcumul_treateddt, dcumul_hosdt, dcumul_vaccinedt])

# ============ 运行所有组合 ============
hosp_rate_matrix = {}  # 用于存储住院率矩阵

for i, (bxm, otv, znv) in enumerate(all_drug_combinations):
    print(f"正在运行组合 {i+1}/66: BXM={bxm}, OTV={otv}, ZNV={znv}")
    
    # 重置全局变量
    antiviral_used = 0
    treatment_active = True
    time_drug_exhausted = None
    vaccine_stopped_time = None
    
    # 设置当前药物分布
    drugs_distribution = {'BXM': bxm, 
                          'OTV': otv, 
                          'ZNV': znv}

    # 解决ODE系统
    y0_extended = np.concatenate([y0, np.zeros(15)])
    sol = solve_ivp(seir_model_with_incidence, t_span, y0_extended, method='LSODA', t_eval=t_eval, first_step=1, max_step=1)

    # 提取结果 
    cumul_vaccine = sol.y[123:126, :]
    cumul_treated = sol.y[117:120, :]
    cumul_Death = sol.y[105:108, :]
    cumul_incidence_R = sol.y[111:114, :]
    cumul_incidence_S = sol.y[114:117, :]
    cumul_incidence = cumul_incidence_R + cumul_incidence_S
    cumul_hos = sol.y[120:123, :]

    # 计算汇总指标
    Vaccine_used = max(cumul_vaccine[0]) + max(cumul_vaccine[1]) + max(cumul_vaccine[2])
    Antiviral_used = max(cumul_treated[0]) + max(cumul_treated[1]) + max(cumul_treated[2])
    
    # 确保药物使用量不超过总库存
    if Antiviral_used > TOTAL_ANTIVIRAL_STOCK * 1.001:  # 允许1%的浮点误差
        print(f"  警告: 药物使用量({Antiviral_used:.0f})超过总库存({TOTAL_ANTIVIRAL_STOCK:.0f})")
        Antiviral_used = TOTAL_ANTIVIRAL_STOCK  # 强制限制
    
    cumulative_incidence_Resistance = max(cumul_incidence_R[0]) + max(cumul_incidence_R[1]) + max(cumul_incidence_R[2])
    cumulative_incidence_Total = max(cumul_incidence[0]) + max(cumul_incidence[1]) + max(cumul_incidence[2])
    Hospitalization = max(cumul_hos[0]) + max(cumul_hos[1]) + max(cumul_hos[2])
    Death = max(cumul_Death[0]) + max(cumul_Death[1]) + max(cumul_Death[2])
    Death_0_18 = max(cumul_Death[0])
    Death_19_64	= max(cumul_Death[1])
    Death_65 = max(cumul_Death[2])
    incidence_0_18 = max(cumul_incidence[0])
    incidence_19_64	= max(cumul_incidence[1])
    hos_19_64 = max(cumul_hos[1])
    
    # 计算Hospitalization_rate并保存到结果中
    Hospitalization_day = sol.y[69]+sol.y[70]+sol.y[71]+sol.y[102]+sol.y[103]+sol.y[104]
    Hospitalization_day_scaled = (Hospitalization_day + 9540)/10600
    Hospitalization_rate_time_series = Hospitalization_day_scaled

    # 生成列名
    col_name = f"{bxm:.1f}bxm_{otv:.1f}otv_{znv:.1f}znv"
    # 存储到矩阵字典中
    hosp_rate_matrix[col_name] = Hospitalization_rate_time_series

    # 存储结果
    results.append({
        'BXM_proportion': bxm,
        'OTV_proportion': otv,
        'ZNV_proportion': znv,
        'Vaccine_used': round(Vaccine_used),
        'Antiviral_used': round(Antiviral_used),
        'cumulative_incidence_Total': round(cumulative_incidence_Total),
        'cumulative_incidence_Resistance': round(cumulative_incidence_Resistance),
        'Hospitalization': round(Hospitalization),
        'Death_0_18': round(Death_0_18),
        'Death_19_64': round(Death_19_64),
        'Death_65': round(Death_65),
        'incidence_0_18': round(incidence_0_18),
        'incidence_19_64': round(incidence_19_64),
        'hos_19_64': round(hos_19_64),
        'AR': round(cumulative_incidence_Total/7534200,4),
        'RAR': round(cumulative_incidence_Resistance/7534200,4),
        'Hospitalization_rate_max': round(max(Hospitalization_rate_time_series),4),
        'Drug_exhausted_day': time_drug_exhausted if time_drug_exhausted is not None else 500
    })

# ============ 保存结果 ============
# 将结果保存到CSV文件
results_df = pd.DataFrame(results)
results_df.to_csv('C:/Users/chenr/Desktop/Result_Influenza_pandemic/Mar27_2026/Output_dataset/FCFS_R03_output_to_CEA_anti_n_vaccine_3month.csv', index=False)
print("结果已保存到csv")

# 显示前几行结果
print("\n前5行结果:")
print(results_df.head())

# 创建住院率矩阵DataFrame
hosp_rate_df = pd.DataFrame(hosp_rate_matrix)

# 添加时间列作为第一列
hosp_rate_df.insert(0, 'Day', np.arange(0, len(hosp_rate_df)))

# 保存到CSV
hosp_rate_df.to_csv('C:/Users/chenr/Desktop/Result_Influenza_pandemic/Mar27_2026/Output_dataset/FCFS_R03_hospitalization_rates_matrix.csv', index=False)
print(f"住院率矩阵已保存到CSV，包含{len(hosp_rate_df)}个时间点 x {len(all_drug_combinations)}种药物组合")

# 显示矩阵的前几行和前几列
print("\n住院率矩阵前5行和前5列:")
print(hosp_rate_df.iloc[:5, :6])

print(f"\n药物总库存: {TOTAL_ANTIVIRAL_STOCK:,} 剂")
print(f"所有组合模拟完成!")
