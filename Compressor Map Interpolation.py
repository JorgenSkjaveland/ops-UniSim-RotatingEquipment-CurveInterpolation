#Author: Jørgen Skjæveland 15.07.25

import numpy as np
import matplotlib.pyplot as plt
import scipy as sp

########################          Input Section         #############################


#The points on the speed curve, with as many points you would like. The points are [Flow [m3/h], Head [kJ/kg]]
SpeedCurve_CSV = np.array(["23KA002 70prct.csv", "23KA002 85prct.csv", "23KA002 95prct.csv", "23KA002 105prct.csv"])

#The speed curve, but ONLY the points where a efficiency line crosses the speed curve, often resulting in few points [Flow [m3/h], Head [kJ/kg]]
DiscreteEfficiencySpeedCurve = np.array(["23KA002 70prct Efficiency.csv", "23KA002 85prct Efficiency.csv", "23KA002 95prct Efficiency.csv", "23KA002 105prct Efficiency.csv"])

#The efficiency points which corresponds to the [Flow [m3/h], Head [kJ/kg]] points on the DiscreteEfficiencySpeedCurve
DiscreteEfficiencyPoints = {'1st': np.array([66.7, 67, 68, 69, 69, 68, 67, 66, 65, 64]), # 1st Curve
                            '2nd': np.array([67, 69, 70, 70, 69, 68, 67, 66.2]), # 2nd Curve
                            '3rd': np.array([68, 72, 72.5, 72.5, 72, 71, 70, 69.7]), #3rd Curve
                            '4th': np.array([71.4, 72, 72, 71, 70, 69, 68.5])} #4th Curve

#The names of the different curves
Names = np.array(["23KA002 - 7791 (70%)", "23KA002 - 9461 (85%)", "23KA002 - 10574 (95%)","23KA002 - 11687 (105%)"])




########################          Function Section     ###############################



def ReadCSV(Filename):
    Dataframe = np.loadtxt(Filename, delimiter=',')
    Flow = np.flip(Dataframe[:, 0])
    Head = np.flip(Dataframe[:, 1])
    return Flow, Head

def SpeedCurveInterpolation(Flow, Head, n=25):
    spl = sp.interpolate.CubicSpline(Flow, Head)
    Flow_n = np.linspace(Flow.min(), Flow.max(), n)
    return Flow, Head, Flow_n, spl(Flow_n)

def Plot_SpeedCurveInterpolation(Flow, Head, Flow_IntPol, Head_IntPol, Name = None):
    ax = plt.subplot(111)
    ax.scatter(Flow, Head, marker='1', alpha=1, color="lightsteelblue", label="Inputs")
    ax.plot(Flow_IntPol, Head_IntPol, color="steelblue", label="Outputs")
    plt.legend()
    if Name != None:
        ax.set_title(f"Cubic Spline fit: {Name}")
    else:
        ax.set_title("Cubic Spline fit")
    ax.set_ylabel("Head [kJ/kg]")
    ax.set_xlabel("Flow [m3/h]")
    plt.savefig(f"Speed Curve - {Name}.png")
    plt.close()
    return Head_IntPol

def DiscreteEfficiencyCurve(Flow, Head = None, Efficiency = None, n = 25):
    spl = sp.interpolate.CubicSpline(Flow, Efficiency)
    Flow_n = np.linspace(Flow.min(), Flow.max(), n)
    return Flow, Head, Flow_n, spl(Flow_n), Efficiency

def Plot_DiscreteEfficiencyCurve(Flow, Head, Flow_IntPol, Efficiency_IntPol, Efficiency, Name = None):
    ax = plt.subplot(111)
    ax.scatter(Flow, Efficiency, marker='1', alpha=1, color="sandybrown", label="Inputs")
    ax.plot(Flow_IntPol, Efficiency_IntPol, color="saddlebrown", label="Outputs")
    plt.legend()
    if Name != None:
        ax.set_title(f"Cubic Spline fit: {Name}")
    else:
        ax.set_title("Cubic Spline fit")
    ax.set_ylabel("Polytropic Efficiency [%]")
    ax.set_xlabel("Flow [m3/h]")
    plt.savefig(f"Efficiency Speed Curve - {Name}.png")
    plt.close()
    return Flow_IntPol, Efficiency_IntPol

def GetDataForUniSim(SpeedCurve_CSV, DiscreteEfficiencySpeedCurve_CSV, DiscreteEfficiencyPoints, Name):
    for SpeedCurve, EfficiencyCurve, (key, Efficiency), Name in zip(SpeedCurve_CSV, DiscreteEfficiencySpeedCurve_CSV, DiscreteEfficiencyPoints.items(), Name):
        Head_IntPol = Plot_SpeedCurveInterpolation(*SpeedCurveInterpolation(*ReadCSV(SpeedCurve)), Name)
        Flow_IntPol, Efficiency_IntPol = Plot_DiscreteEfficiencyCurve(*DiscreteEfficiencyCurve(*ReadCSV(EfficiencyCurve), np.flip(Efficiency)), Name)
        results = np.array([Flow_IntPol,
                            Head_IntPol,
                            Efficiency_IntPol]).T
        np.savetxt(f"{Name}.tsv", results, delimiter='\t', header=("Flow [m3/h] \t Head [kJ/kg] \t Efficiency [%]"))
    return 0

GetDataForUniSim(SpeedCurve_CSV, DiscreteEfficiencySpeedCurve, DiscreteEfficiencyPoints, Names)



