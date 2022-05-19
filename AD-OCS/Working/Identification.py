# IDENTIFICATION
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm

import pylops
from scipy.optimize import curve_fit
from scipy.optimize import least_squares
from scipy.stats import linregress
from sklearn.linear_model import LinearRegression

from dataimport import*
from PhysConstants import*
from ReactorConf import*

# Get raw data
HRT   = T1["HRT"]
S1    = T1["S1"]  # [g/L] - COD
XT    = T1["XT"]
S2    = T1["S2"]  # [mmol/L] - VFA
X_1   = T1["X1"]
X_2   = T1["X2"]
Z     = T1["Z"]
C     = T1["C"]
CO2   = T1["CO2"]
B     = T1["B"]
pH    = T1["pH"]
q_C   = T1["q_C"]  # [mmol/L/d]
P_C   = T1["P_C"]  # [atm]
q_M   = T1["q_CH4"]

Dil     = 1/HRT

S1_in = float(T2["S1in"])    # [gCOD/L]
S2_in = float(T2["S2in"])    # [mmol/L]
C_in  = float(T2["Cin"])    # [mmol/L]
XT_in = float(T2["XTin"])    # [gCOD/L]

# KINETICS

Xr1 = (Dil*S1, Dil)
Yr1 = S1

def func1(X,a,b):
    x1,x2 = X
    return a*x1 +a*b*x2 + b*C_d[0]/(1-C_d[0])

popt1, pcov1 = curve_fit(func1, Xr1, Yr1)

KS1 = popt1[1]                          # [1/d]      Max biomass growth rate
mu1_max = alfa/(1-C_d[0])/popt1[0]      # [g/L]      Half saturation constant

Xr2 = (Dil, S2)
Yr2 = S2

def func2(X,a,b,c):
    x1,x2 = X
    return a*x1*x2 + a*b*x1 + C_d[1]/(1-C_d[1])*b + a*c*x1*(x2**2) + C_d[1]/(1-C_d[1])*c*(x2**2)

guess2 = [10, 3, 1/300]
popt2, pcov2 = curve_fit(func2, Xr2, Yr2, guess2)

KS2     = popt2[1];
mu2_max = alfa/(1-C_d[1])/popt2[0];
KI2     = 1/popt2[2];


mu_max = (mu1_max, mu2_max)         # [1/d]      Max biomass growth rate
Ks     = (KS1, KS2)                 # [g/L]      Half saturation constant
KI2    = np.abs(KI2)                # [mmol/L]   Inhibition constant for S2
kd     = np.multiply(C_d,mu_max)

# Hydrolysis

X_hydr = XT
Y_hydr = Dil*(XT_in-XT)
mdl_hydr1= LinearRegression(fit_intercept=True).fit(np.array(X_hydr).reshape(-1,1), np.array(Y_hydr))
mdl_hydr2= LinearRegression(fit_intercept=False).fit(np.array(X_hydr).reshape(-1,1), np.array(Y_hydr))
scoreh1 = mdl_hydr1.score(np.array(X_hydr).reshape(-1,1), np.array(Y_hydr))
scoreh2 = mdl_hydr2.score(np.array(X_hydr).reshape(-1,1), np.array(Y_hydr))

if scoreh1 > scoreh2:
    k_hyd = mdl_hydr1.coef_
    int_hyd = 'Yes'
    mdl_hyd = mdl_hydr1
else:
    k_hyd = mdl_hydr2.coef_
    int_hyd = 'No'
    mdl_hyd = mdl_hydr2

# Physical - L/G TRANSFER

pKb = -np.log10(Kb)
fun = 1/(1+10**(pH-pKb))
X3r = C*fun - KH*P_C
Y3r = q_C

mdl31= LinearRegression(fit_intercept=True).fit(np.array(X3r).reshape(-1,1), np.array(Y3r))
mdl32= LinearRegression(fit_intercept=False).fit(np.array(X3r).reshape(-1,1), np.array(Y3r))
score31 = mdl31.score(np.array(X3r).reshape(-1,1), np.array(Y3r))
score32 = mdl32.score(np.array(X3r).reshape(-1,1), np.array(Y3r))

if score31 > score32:
    kLa = mdl31.coef_
    int3 = 'Yes'
    mdl3 = mdl31
else:
    kLa = mdl32.coef_
    int3 = 'No'
    mdl3 = mdl32

# Yield coefficients: [CODdeg, VFAprof, VFAcons, CO2prod(1), CO2prod(2), CH4prod, hydrolysis]
mu_1 = alfa*Dil + C_d[0]*mu1_max
mu_2 = alfa*Dil + C_d[1]*mu2_max

X4r = mu_1*X_1
Y4r = Dil*(S1_in - S1) + k_hyd*XT
mdl41 = LinearRegression(fit_intercept=True).fit(np.array(X4r).reshape(-1,1), np.array(Y4r))
mdl42 = LinearRegression(fit_intercept=False).fit(np.array(X4r).reshape(-1,1), np.array(Y4r))
score41 = mdl41.score(np.array(X4r).reshape(-1,1), np.array(Y4r))
score42 = mdl42.score(np.array(X4r).reshape(-1,1), np.array(Y4r))
if score41 > score42:
    k1 = mdl41.coef_
    int4 = 'Yes'
    mdl4 = mdl41
else:
    k1 = mdl42.coef_
    int4 = 'No'
    mdl4 = mdl42
   
X5r = mu_2
Y5r = q_M/X_2
mdl51 = LinearRegression(fit_intercept=True).fit(np.array(X5r).reshape((-1,1)),np.array(Y5r))
mdl52 = LinearRegression(fit_intercept=False).fit(np.array(X5r).reshape((-1,1)),np.array(Y5r))
score51 = mdl51.score(np.array(X5r).reshape(-1,1), np.array(Y5r))
score52 = mdl52.score(np.array(X5r).reshape(-1,1), np.array(Y5r))
if score51 > score52:
    k6 = mdl51.coef_
    int5 = 'Yes'
    mdl5 = mdl51
else:
    k6 = mdl52.coef_
    int5 = 'No'
    mdl5 = mdl52
    
X61 = np.array(Dil*(S2_in-S2)).reshape((-1,1))
X62 = np.array(Dil*(S1_in-S1) + k_hyd*XT).reshape((-1,1))
X6r = np.hstack((X61,X62))
Y6r = np.array(q_M)

mdl61 = LinearRegression(fit_intercept=True).fit(X6r,Y6r)
mdl62 = LinearRegression(fit_intercept=False).fit(X6r,Y6r)
score61 = mdl61.score(X6r, Y6r)
score62 = mdl62.score(X6r, Y6r)

if score61 > score62:
    AA = mdl61.coef_[0]
    BB = mdl61.coef_[1]/AA
    int6 = 'Yes'
    mdl6 = mdl61
else:
    AA = mdl62.coef_[0]
    BB = mdl62.coef_[1]/AA
    int6 = 'No'
    mdl6 = mdl62
        
X71 = np.array(Dil*(S1_in-S1) + k_hyd*XT).reshape((-1,1))
X72 = np.array(q_M).reshape((-1,1))
X7r = np.hstack((X71,X72))
Y7r = np.array(q_C - Dil*(C_in - C))

mdl71 = LinearRegression().fit(X7r,Y7r)
mdl72 = LinearRegression(fit_intercept=False).fit(X7r,Y7r)
score71 = mdl71.score(X7r, Y7r)
score72 = mdl72.score(X7r, Y7r)

if score71 > score72:
    CC = mdl71.coef_[0]
    DD = mdl71.coef_[1]
    int7 = 'Yes'
    mdl7 = mdl71
else:
    CC = mdl72.coef_[0]
    DD = mdl72.coef_[1]
    int7 = 'No'
    mdl7 = mdl72

k2 = BB*k1
k3 = k6/AA
k4 = CC*k1
k5 = DD*k6

k = [k1, k2, k3, k4, k5, k6, k_hyd]

print(f'k1: {k1}, intercept: {int4}')
print(f'k2: {k2}, intercept: {int6}')
print(f'k3: {k3}, intercept: {int6}')
print(f'k4: {k4}, intercept: {int7}')
print(f'k5: {k5}, intercept: {int7}')
print(f'k6: {k6}, intercept: {int5}')
print(f'k_hyd: {k_hyd}, intercept: {int_hyd}')
print(f'kLa: {kLa}, intercept: {int3},')