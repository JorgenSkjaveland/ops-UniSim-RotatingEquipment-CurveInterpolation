#Author: Jørgen Skjæveland 31.07.25
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import os
from scipy.interpolate import CubicSpline



def main():
    #Initialize the program with golbal input parameters. Name and method of interpolation.
    try:
        CompressorName = str(input("Enter the name of the compressor: "))
    except:
        print("Invalid input. Using 'Compressor' as default.")
        CompressorName = "Compressor"
    try:
        method = str(input("Do you wan to use Cubic Spline interpolation or Polynomial fit? (C/P): ")).lower()
        if not (method == "c" or method == "p"):
            print("Invalid input. Using Cubic Spline interpolation as default.")
        method = "c"
    except:
        print("Invalid input. Using Cubic Spline interpolation as default.")
        method = "c"

    GetDataForUniSim(CompressorName, method)
    return 0


def ReadCSVInFolder():
    input_folder = Path.cwd() / "InputCurves"
    csv_files = list(input_folder.glob("*.csv"))
    names = [file.name for file in csv_files]
    dataframes = [pd.read_csv(file, header=None) for file in csv_files]
    return dataframes, names

def EfficiencyCurve(dataframe: pd.DataFrame, name: str, n: int = 25, method: str = "c"):
    Flow = np.flip(dataframe.iloc[:, 0].to_numpy())
    Head = np.flip(dataframe.iloc[:, 1].to_numpy())
    Efficiency = np.flip(dataframe.iloc[:, 2].to_numpy())
    Flow_list = np.linspace(Flow.min(), Flow.max(), n)

    if method == "p":
        polynomial_Head = np.polynomial.Polynomial.fit(Flow, Head, 3)
        polynomial_Efficiency = np.polynomial.Polynomial.fit(Flow, Efficiency, 4)
        Head_list = polynomial_Head(Flow_list)
        Efficiency_list = polynomial_Efficiency(Flow_list)
    elif method == "c":
        cubic_spline_Head = CubicSpline(np.sort(Flow), Head)
        cubic_spline_Efficiency = CubicSpline(np.sort(Flow), Efficiency)
        Head_list = cubic_spline_Head(Flow_list)
        Efficiency_list = cubic_spline_Efficiency(Flow_list)

    result_table = np.array([Flow_list,
                             Head_list,
                             Efficiency_list]).T
    folder = "RotatingEquipmentDataForUniSim"
    os.makedirs(folder, exist_ok=True)
    np.savetxt(f"{folder}/{name[0:-4]}.tsv", result_table, delimiter='\t',
               header=("Flow [m3/h] \t Head [kJ/kg] \t Efficiency [%]"))
    PlotEfficiencyFit(Flow, Efficiency, Flow_list, Efficiency_list, name, folder, method)
    PlotHeadFit(Flow, Head, Flow_list, Head_list, name, folder, method)
    if method == "p":
        return Flow, Head, Efficiency, polynomial_Head(Flow_list), polynomial_Efficiency(Flow_list)
    elif method == "c":
        return Flow, Head, Efficiency, cubic_spline_Head(Flow_list), cubic_spline_Efficiency(Flow_list)
    
def PlotEfficiencyFit(Flow, Efficiency, Flow_list, Efficiency_list, name=None, folder=None, method="c"):
    ax = plt.subplot(111)
    ax.scatter(Flow, Efficiency, marker='1', alpha=1, color="sandybrown", label="Inputs")
    ax.plot(Flow_list, Efficiency_list, color="saddlebrown", label="Outputs")
    plt.legend()
    if name != None and method == "p":
        ax.set_title(f"Polynomial fit: {name[0:-4]}")
    elif name != None and method == "c":
        ax.set_title(f"Cubic Spline interpolation: {name[0:-4]}")
    else:
        ax.set_title(f"{method} fit")
    ax.set_ylabel("Polytropic Efficiency [%]")
    ax.set_xlabel("Flow [m3/h]")
    plt.savefig(f"{folder}/Efficiency Curve - {name[0:-4]}.png")
    plt.close()
    return 0

def PlotHeadFit(Flow, Head, Flow_list, Head_list, name=None, folder=None, method: str = "c"):
    ax = plt.subplot(111)
    ax.scatter(Flow, Head, marker='1', alpha=1, color="lightsteelblue", label="Inputs")
    ax.plot(Flow_list, Head_list, color="steelblue", label="Outputs")
    plt.legend()
    if name != None and method == "p":
        ax.set_title(f"Polynomial fit: {name[0:-4]}")
    elif name != None and method == "c":
        ax.set_title(f"Cubic Spline interpolation: {name[0:-4]}")
    else:
        ax.set_title(f"{method} fit")
    ax.set_ylabel("Head [kJ/kg]")
    ax.set_xlabel("Flow [m3/h]")
    plt.savefig(f"{folder}/Head Curve - {name[0:-4]}.png")
    plt.close()
    return 0

def Plot3D(CompressorName: str):
    tsv_files = list((Path(__file__).parent / "CompressorDataForUniSim").glob("*.tsv"))
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    ax.set_xlabel("Flow [m3/h]")
    ax.set_ylabel("Head [kJ/kg]")
    ax.set_zlabel("Poly. Eff [%]")
    for file in tsv_files:
        name = file.name
        CompressorData = pd.read_csv(file, delimiter='\t')
        ax.plot(CompressorData.values[:, 0], CompressorData.values[:, 1], CompressorData.values[:, 2])
    ax.set_title(f"{CompressorName}")
    plt.legend()
    plt.show()
    return 0

def PlotFlowHead(CompressorName: str):
    tsv_files = list((Path(__file__).parent / "CompressorDataForUniSim").glob("*.tsv"))
    fig, ax = plt.subplots()
    ax.set_xlabel("Flow [m3/h]")
    ax.set_ylabel("Head [kJ/kg]")
    for file in tsv_files:
        name = file.name
        CompressorData = pd.read_csv(file, delimiter='\t')
        ax.plot(CompressorData.values[:, 0], CompressorData.values[:, 1])
    ax.set_title(f"{CompressorName}")
    plt.legend()
    fig.savefig(f"CompressorDataForUniSim/{CompressorName}.png")
    plt.close()
    return 0
    

def GetDataForUniSim(CompressorName: str, method: str = "c"):
    
    dataframes, names = ReadCSVInFolder()
    for dataframe, name in zip(dataframes, names):
        EfficiencyCurve(dataframe, name)
    PlotFlowHead(CompressorName)
    Plot3D(CompressorName)
    return 0


if __name__ == "__main__":
    main()
