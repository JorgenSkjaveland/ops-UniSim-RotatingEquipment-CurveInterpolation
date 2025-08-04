#Author: Jørgen Skjæveland 31.07.25

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy as sp
from pathlib import Path
import os

def ReadCSVInFolder():
    csv_files = list(Path(__file__).parent.glob("*.csv"))
    names = [file.name for file in csv_files]
    dataframes = [pd.read_csv(file, header=None) for file in csv_files]
    return dataframes, names

def EfficiencyCurve(dataframe: pd.DataFrame, name: str, n: int = 25):
    Flow = np.flip(dataframe.iloc[:, 0].to_numpy())
    Head = np.flip(dataframe.iloc[:, 1].to_numpy())
    Efficiency = np.flip(dataframe.iloc[:, 2].to_numpy())
    spl_Head = sp.interpolate.CubicSpline(Flow, Head)
    spl_Efficiency = sp.interpolate.CubicSpline(Flow, Efficiency)
    Flow_list = np.linspace(Flow.min(), Flow.max(), n)
    Head_list = spl_Head(Flow_list)
    Efficiency_list = spl_Efficiency(Flow_list)
    result_table = np.array([Flow_list,
                             Head_list,
                             Efficiency_list]).T
    folder = "CompressorDataForUniSim"
    os.makedirs(folder, exist_ok=True)
    np.savetxt(f"{folder}/{name[0:-4]}.tsv", result_table, delimiter='\t',
               header=("Flow [m3/h] \t Head [kJ/kg] \t Efficiency [%]"))
    PlotEfficiencyFit(Flow, Efficiency, Flow_list, Efficiency_list, name, folder)
    PlotHeadFit(Flow, Head, Flow_list, Head_list, name, folder)
    return Flow, Head, Efficiency, spl_Head(Flow_list), spl_Efficiency(Flow_list)
    
def PlotEfficiencyFit(Flow, Efficiency, Flow_list, Efficiency_list, name=None, folder=None):
    ax = plt.subplot(111)
    ax.scatter(Flow, Efficiency, marker='1', alpha=1, color="sandybrown", label="Inputs")
    ax.plot(Flow_list, Efficiency_list, color="saddlebrown", label="Outputs")
    plt.legend()
    if name != None:
        ax.set_title(f"Cubic Spline fit: {name}")
    else:
        ax.set_title("Cubic Spline fit")
    ax.set_ylabel("Polytropic Efficiency [%]")
    ax.set_xlabel("Flow [m3/h]")
    plt.savefig(f"{folder}/Efficiency Curve - {name[0:-4]}.png")
    plt.close()
    return 0

def PlotHeadFit(Flow, Head, Flow_list, Head_list, name=None, folder=None):
    ax = plt.subplot(111)
    ax.scatter(Flow, Head, marker='1', alpha=1, color="lightsteelblue", label="Inputs")
    ax.plot(Flow_list, Head_list, color="steelblue", label="Outputs")
    plt.legend()
    if name != None:
        ax.set_title(f"Cubic Spline fit: {name}")
    else:
        ax.set_title("Cubic Spline fit")
    ax.set_ylabel("Head [kJ/kg]")
    ax.set_xlabel("Flow [m3/h]")
    plt.savefig(f"{folder}/Head Curve - {name[0:-4]}.png")
    plt.close()
    

def GetDataForUniSim():
    dataframes, names = ReadCSVInFolder()
    for dataframe, name in zip(dataframes, names):
        EfficiencyCurve(dataframe, name)

GetDataForUniSim()
