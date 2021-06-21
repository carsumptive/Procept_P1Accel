import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
from scipy.interpolate import make_interp_spline


def parse_fixture():

    #read the important columns from table
    #data = pd.read_csv(r"C:\Users\c.lansdowne\Box\My Cloud - c.lansdowne\_Desktop\FH_TracyQI19Fixture.csv", usecols = ['Time', 'ExtR'])
    data = pd.read_csv(r"C:\Users\c.lansdowne\Box\My Cloud - c.lansdowne\_Desktop\21C00201-001try.csv",
                       usecols=['Time', 'ExtR'])

    #clean data
    data.dropna(subset = ['ExtR'], inplace=True)

    #initialize decel and accel time lists
    accel_times = []
    decel_times = []

    #initialize empty radial velocity list
    ExtRVel = []

    #set sensitivity
    #look ahead & tolerance range
    nominal = 720
    decel_margin = .35 #what % decrease of nominal (720) counts as starting deceleration
    accel_margin = .2 #what % decrease of nominal counts as fully accelerated?
    zero_margin = .17 #what does the filter consider to be the turnaround point?
    lookahead = 3 #how many data points ahead does the filter sample?
    threshold = .1

    #Zero R and find Velocity list
    initialR = data.iat[0,1]
    i = 0
    for row in data.index:
        r = data['ExtR'][row]
        if row == 0: #handle first r case
            ExtRVel.append(0)
            continue
        Vel = (r-data['ExtR'][row-1])/(data['Time'][row]-data['Time'][row-1])
        ExtRVel.append(Vel)

    data['ExtRVel'] = ExtRVel
    data['ExtRVelreg'] = ExtRVel #non abs vel data
    data['ExtRVel'] = data['ExtRVel'].abs()
    # Main_spline = make_interp_spline(data['Time'],data['ExtRVelreg'])
    # x_ = np.linspace(data['Time'].min(), data['Time'].max(), 1000)
    # y_ = Main_spline(x_)
    plt.plot(data['Time'], data['ExtRVel'])

    fig, (ax1, ax2, ax3) = plt.subplots(3)
    #ax1.plot(data['Time'], data['ExtRVel'])

    #initialize filter variables
    vel = []
    turnaround = []
    decel_start = 0
    accel_start = 0
    decel_end = 0
    accel_end = 0

    #filter algorithm
    ##Takes absolute value data and forward steps the average and checks for deceleration within lookahead span
    ##if decel is found, decel span is measured and accel span immediately follows
    ##if acceleration ends, reset measurement and add to turnaround array
    ##turnaround is summed accel and decel times

    #tune what the filter consideres a decel start, accel end, and zero (decel completed) above

    for row in data.index:
        if row + lookahead < len(data['Time']):
            isdecel = False
            #print("range:", row)
            if decel_start == 0:
                vel = []
                for i in range(lookahead-1):
                    vel.append(data['ExtRVel'][row + i + 1])
                    if vel[i] <= nominal*zero_margin:
                        isdecel = True
            ave_vel = sum(vel)/len(vel)
            #print("average", ave_vel)
            #print("data, ", data['ExtRVel'][row])
            # print("extRvel", data['ExtRVel'][row])
            # print("extRvel1", vel[0])
            # print(isdecel)
            if ave_vel < nominal*(1-decel_margin) and data['ExtRVel'][row] >= nominal*(1-decel_margin) and vel[1] <= nominal*(1-decel_margin) and isdecel:
                decel_start = data['Time'][row]
                #print(data['ExtRVel'][row])
            if data['ExtRVel'][row] <= nominal*zero_margin and decel_start != 0:
                decel_end = data['Time'][row]
                accel_start = data['Time'][row]
                #print("decel end", decel_end)
            if decel_end != 0 and decel_start != 0:
                #print("decel time", decel_end - decel_start)
                decel_times.append(decel_end - decel_start)
                decel_end = 0
                decel_start = 0
            if accel_start != 0 and data['ExtRVel'][row] >= nominal*(1-accel_margin):
                accel_end = data['Time'][row]
                accel_times.append(accel_end - accel_start)
                turnaround.append(accel_times[-1] + decel_times[-1])
                #print("accel time", accel_end - accel_start)
                accel_start = 0
                decel_end = 0

    decel_times = [x for x in decel_times if x <= threshold]
    accel_times = [x for x in accel_times if x <= threshold]
    turnaround = [x for x in turnaround if x <= threshold]

    #plot decel times
    ax1.plot(decel_times, 'o')
    plt.ylabel('Deceleration time (s)')
    plt.xlabel('Turn #')
    ax1.set_title('Plot of all Deceleration times')
    #plot accel times
    ax2.plot(accel_times, 'o')
    plt.ylabel('Acceleration time (s)')
    plt.xlabel('Turn #')
    ax2.set_title('Plot of all Acceleration times')
    #plot accel times
    ax3.plot(turnaround, 'o')
    plt.ylabel('Turnaround time (s)')
    plt.xlabel('Turn #')
    ax3.set_title('Plot of all Turnaround times')

    #write to csv
    with open('C:/Users/c.lansdowne/Documents/GitHub/P1Accel/decel_times1.csv', 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["Decel times"])
        csvwriter.writerow(decel_times)
        csvwriter.writerow(["Accel times"])
        csvwriter.writerow(accel_times)

    plt.show()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parse_fixture()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
