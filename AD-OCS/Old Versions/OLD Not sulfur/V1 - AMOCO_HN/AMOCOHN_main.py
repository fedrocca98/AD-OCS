# Modified Version of AMOCO_HN
# First try implementation
#

import math
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

from SS_Algebraic import*

# SYSTEM

y0 = [SSTATE[0], SSTATE[1], SSTATE[2], SSTATE[3], SSTATE[4], SSTATE[5], SSTATE[6]]

def f_Model_Deviations_Simple(x,t,alfa,mu_max,Ks,KI2,KH,Pt,kLa,D,y_in,k,kd,N_bac,N_S1):

    XT, X1, X2, Z, S1, S2, C = x

    if t < 20 or t > 100:
        S1in = y_in[0]
        S2in = y_in[1]
        Cin  = y_in[2]
        Zin  = y_in[3]
        XTin = y_in[4]
    else:
        S1in = y_in[0]
        S2in = y_in[1]
        Cin  = y_in[2]
        Zin  = y_in[3]
        XTin = 1.2*y_in[4]

    mu1 = mu_max[0]*(S1/(S1+Ks[0]))                     # Monod
    mu2 = mu_max[1]*(S2/(S2+Ks[1]+S2**2/KI2))           # Haldane

    qM  = k[5]*mu2*X2                                   # Methane molar flow [mmol/L/day]
    CO2 = C + S2 - Z                                    # [mmol/L]
    phi = CO2 + KH*Pt + qM/kLa
    Pc  = (phi - (phi**2- 4*KH*Pt*CO2)**0.5)/(2*KH)     # [atm] - Partial pressure CO2
    qC  = kLa*(CO2 - KH*Pc)                             # [mmol/L/d] - Carbon Molar Flow
    CONTROL = KH*Pc**2-Pc*phi + Pt*CO2                  # Control equation, has to be zero

    dXT = D*(XTin - XT) - k[6]*XT                       # Evolution of particulate
    dX1 = (mu1 - alfa*D - kd[0])*X1                     # Evolution of biomass 1 (acidogen.)
    dX2 = (mu2 - alfa*D - kd[1])*X2                     # Evolution of biomass 2 (methanogen)
    dZ  = D*(Zin - Z) + (k[0]*N_S1 - N_bac)*mu1*X1 - N_bac*mu2*X2 + kd[0]*N_bac*X1 + kd[1]*N_bac*X2 # Evolution of alcalinity;
    dS1 = D*(S1in - S1) - k[0]*mu1*X1 + k[6]*XT                                                     # Evolution of organic substrate
    dS2 = D*(S2in - S2) + k[1]*mu1*X1 - k[2]*mu2*X2       # Evolution of VFA
    dC  = D*(Cin - C)   + k[3]*mu1*X1 + k[4]*mu2*X2 - qC  # Evolution of inorganic carbon

    dxdt = [dXT, dX1, dX2, dZ, dS1, dS2, dC]

    return dxdt

tspan = np.linspace(1,200,10000)
YOUT = odeint(f_Model_Deviations_Simple,y0,tspan,args=(alfa, mu_max, Ks, KI2, KH, Pt, kLa, D, y_in, k, kd, N_bac, N_S1))

XT = YOUT[:,0]   # [g/L]
X1 = YOUT[:,1]   # [g/L]
X2 = YOUT[:,2]   # [g/L]
Z  = YOUT[:,3]   # [mmol/L]
S1 = YOUT[:,4]   # [g/L]
S2 = YOUT[:,5]   # [mmol/L]
C  = YOUT[:,6]   # [mmol/L]

# Solver Output
mu1 = np.empty(len(XT))
mu2 = np.empty(len(XT))
CO2 = np.empty(len(XT))
B   = np.empty(len(XT))
phi = np.empty(len(XT))
p_C = np.empty(len(XT))
q_C = np.empty(len(XT))
q_M = np.empty(len(XT))
pH  = np.empty(len(XT))

for x in range(len(XT)):
    mu1[x] = mu_max[0]*(S1[x]/(S1[x]+Ks[0]))                     # Monod
    mu2[x] = mu_max[1]*(S2[x]/(S2[x]+Ks[1]+S2[x]**2/KI2))        # Haldane
    CO2[x] = C[x] + S2[x] - Z[x]
    B[x]   = Z[x] - S2[x]
    phi[x] = CO2[x] + KH*Pt + k[5]/kLa*mu2[x]*X2[x]
    p_C[x]  = (phi[x] - (phi[x]**2- 4*KH*Pt*CO2[x])**0.5)/(2*KH)
    q_C[x] = kLa*(CO2[x] - KH*p_C[x])
    q_M[x] = k[5]*mu2[x]*X2[x]
    pH[x]  = np.real(-np.log10(Kb*CO2[x]/B[x]))
q_tot = q_C+q_M
x_M   = np.divide(q_M,q_tot)
print("Mole fraction of methane in the gas at the end",float(x_M[-1]))

plt.close("all")


plt.figure(1)
ax1 = plt.subplot()
ax1.plot(tspan, X1, label="Acidogenics")
ax1.plot(tspan, X2, label="Methanogens")
ax1.set_xlabel('time [d]')
ax1.set_ylabel('Microbial Concentration [g/L]')
ax1.grid(True)
ax1.legend()

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('pH Value [-]', color = color)
ax2.plot(tspan, pH, linestyle='dashed',color =color, label="pH")
ax2.tick_params(axis='y', labelcolor=color)

plt.tight_layout()



plt.figure(2)
sub1 = plt.subplot(2,2,1)
sub1.plot(tspan,q_M,label="CH4")
sub1.plot(tspan,q_C,label="CO2")
sub1.set_ylabel('Gas Flowrate [mmol/L/d]')
sub1.set_xlabel('Time [d]')
sub1.grid(True)
sub1.legend()

sub2 = plt.subplot(2,2,2)
sub2.plot(tspan,Z,label="Alkalinity")
sub2.plot(tspan,C,label="In. Carbon")
sub2.set_ylabel('Inorganics Conc. [mmol/L]')
sub2.set_xlabel('Time [d]')
sub2.grid(True)
sub2.legend()

sub3 = plt.subplot(2,2,3)
sub3.plot(tspan,XT,label="Particulate (XT)")
sub3.plot(tspan,S1,label="COD (S1)")
sub3.set_ylabel('Substrates Conc. [g/L]')
sub3.set_xlabel('Time [d]')
sub3.grid(True)
sub3.legend()

sub4 = plt.subplot(2,2,4)
sub4.plot(tspan,S1,label="COD (S1)")
sub4.plot(tspan,S2,label="VFA (S2) [mmol/L]")
sub4.set_ylabel('Substrates Conc. ')
sub4.set_xlabel('Time [d]')
sub4.grid(True)
sub4.legend()

plt.figure(3)
sub1 = plt.subplot(6,2,1)
sub1.plot(tspan,S1/S1[0])
sub1.set_ylabel('S1*')
sub1.tick_params(labelbottom=False)
sub1.set_xlim(tspan[0],tspan[-1])
sub1.grid(True)

sub2 = plt.subplot(6,2,2)
sub2.plot(tspan,S2/S2[0])
sub2.set_ylabel('S2*')
sub2.tick_params(labelbottom=False)
sub2.set_xlim(tspan[0],tspan[-1])
sub2.grid(True)

sub3 = plt.subplot(6,2,3)
sub3.plot(tspan,X1/X1[0])
sub3.set_ylabel('X1*')
sub3.tick_params(labelbottom=False)
sub3.set_xlim(tspan[0],tspan[-1])
sub3.grid(True)

sub4 = plt.subplot(6,2,4)
sub4.plot(tspan,X2/X2[0])
sub4.set_ylabel('X2*')
sub4.tick_params(labelbottom=False)
sub4.set_xlim(tspan[0],tspan[-1])
sub4.grid(True)

sub5 = plt.subplot(6,2,5)
sub5.plot(tspan,C/C[0])
sub5.set_ylabel('C*')
sub5.tick_params(labelbottom=False)
sub5.set_xlim(tspan[0],tspan[-1])
sub5.grid(True)

sub6 = plt.subplot(6,2,6)
sub6.plot(tspan,Z/Z[0])
sub6.set_ylabel('Z*')
sub6.tick_params(labelbottom=False)
sub6.set_xlim(tspan[0],tspan[-1])
sub6.grid(True)

sub7 = plt.subplot(6,2,7)
sub7.plot(tspan,CO2/CO2[0])
sub7.set_ylabel('CO2*')
sub7.tick_params(labelbottom=False)
sub7.set_xlim(tspan[0],tspan[-1])
sub7.grid(True)

sub8 = plt.subplot(6,2,8)
sub8.plot(tspan,B/B[0])
sub8.set_ylabel('B*')
sub8.tick_params(labelbottom=False)
sub8.set_xlim(tspan[0],tspan[-1])
sub8.grid(True)

sub9 = plt.subplot(6,2,9)
sub9.plot(tspan,pH/pH[0])
sub9.set_ylabel('pH*')
sub9.tick_params(labelbottom=False)
sub9.set_xlim(tspan[0],tspan[-1])
sub9.grid(True)

sub10 = plt.subplot(6,2,10)
sub10.plot(tspan,XT/XT[0])
sub10.set_ylabel('XT*')
sub10.tick_params(labelbottom=False)
sub10.set_xlim(tspan[0],tspan[-1])
sub10.grid(True)

sub11 = plt.subplot(6,2,11)
sub11.plot(tspan,q_C/q_C[0])
sub11.set_ylabel('q_C*')
sub11.set_xlabel('Time [d]')
sub11.set_xlim(tspan[0],tspan[-1])
sub11.grid(True)

sub12 = plt.subplot(6,2,12)
sub12.plot(tspan,q_M/q_M[0])
sub12.set_ylabel('q_M*')
sub12.set_xlabel('Time [d]')
sub12.set_xlim(tspan[0],tspan[-1])
sub12.grid(True)

# plt.show()
