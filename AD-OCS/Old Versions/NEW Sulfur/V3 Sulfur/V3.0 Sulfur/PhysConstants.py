# Physical Constants
import numpy as np

Rgas_L_atm_K = 0.08205746 # L*atm/(mol*K)
Rgas_J_mol_K = 8.3144598 # J/(mol*K)
Rgas_m3_atm_K = 0.08205746e-3 # m^3*atm/(mol*K)

Ka   = 1.5e-5
Kb   = 6.5e-7
Kc   = 4.5e-11

MW_APr = 74.08                       # [g/mol] Propionic Acid
MW_AAc = 60.052                      # [g/mol] Acetic Acid
MW_ABu = 88.11                       # [g/mol] Butyric Acid
MW_APe = 102.13                      # [g/mol] Pentanoic Acid
MW_co  = 44                          # [g/mol] CO2
MW_met = 16                          # [g/mol] CH4
MW_H2S = 34                          # [g/mol] H2S
MW_O2  = 32                          # [g/mol] O2

MW_gas  = [MW_met,MW_co,MW_H2S]
Y_srb  = 0.0342*64/1000               # [g/mmol] Yield 
