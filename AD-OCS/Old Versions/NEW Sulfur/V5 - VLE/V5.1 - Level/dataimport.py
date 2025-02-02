import pandas as pd
import numpy as np
from pathlib import Path

print('Choose a datasets: \n 1 -> AMOCO_HN \n 2 -> provaADM1')
name_index = 1 # input("->")

datasets = ["amoco_HN level","provaADM1"]
simname  = datasets[int(name_index) -1]
print("Data are from:",simname)

filename: Path = simname + '.xlsx'
folder: Path = Path(Path.cwd())
folder: Path = folder.joinpath('data')
reading_path =  (folder/filename)

colnames = ["HRT", "XT", "S1", "S2", "X1", "X2", "C", "Z", "CO2", "B", "pH", "P_C", "q_C", "q_CH4"]

T1 = pd.read_excel(reading_path, sheet_name = "SS_Values",header = None, names = colnames, skiprows = 1)
T2 = pd.read_excel(reading_path, sheet_name = "Influent", header = 0)
T3 = pd.read_excel(reading_path, sheet_name = "Deviations", header = 0, index_col = 0)

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

Dil     = 1/HRT # [1/d] - Vector of dilution rates


