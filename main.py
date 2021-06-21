import pandas as pd
import matplotlib.pyplot as plt


def parse_fixture():

    #read the important columns from table
    data = pd.read_csv(r"C:\Users\c.lansdowne\Box\My Cloud - c.lansdowne\_Desktop\FH_TracyQI19Fixture.csv", usecols = ['Time', 'ExtR'])
    print(data.iat[0,1])

    #clean data
    data.dropna(subset = ['ExtR'], inplace=True)

    #initialize decel and accel time lists
    accel_times = []
    decel_times = []

    #set sensitivity
    #look ahead & tolerance range
    decel_margin = .15
    zero_margin = .1
    lookahead = 3
    threshold = .1 #ms

    #Zero R and find Velocity list
    initialR = data.iat[0,1]
    # initialrtol = .15
    # count = 0 #count the number of measurements in initial R

    ExtRVel = []

    i = 0
    for row in data.index:
        r = data['ExtR'][row]
        if row == 0: #handle first r case
            ExtRVel.append(0)
            continue
        Vel = (r-data['ExtR'][row-1])/(data['Time'][row]-data['Time'][row-1])
        ExtRVel.append(Vel)

    print(ExtRVel)
    data['ExtRVel'] = ExtRVel
    #plt.plot(data['Time'], data['ExtRVel'])
    data['ExtRVel'] = data['ExtRVel'].abs()
    print()

    #plt.plot(data['Time'], data['ExtRVel'])


    #find decel time
    #look ahead to check decel range
    vel = []
    decel_start = 0
    decel_end = 0

    print(len(data['Time']))

    for row in data.index:
        if row + lookahead < len(data['Time']):
            isdecel = False
            #print("range:", row)
            if decel_start == 0:
                vel = []
                for i in range(lookahead-1):
                    vel.append(data['ExtRVel'][row + i + 1])
                    if vel[i] <= 720*zero_margin:
                        isdecel = True
                    #print(vel)
                #print("writing vel")
            # vel[1] = data['ExtR'][row + 2]
            # vel[2] = data['ExtR'][row + 3]
            # vel[3] = data['ExtR'][row + 4]
            # vel[4] = data['ExtR'][row + 5]
            ave_vel = sum(vel)/len(vel)
            print("average", ave_vel)
            # print("extRvel", data['ExtRVel'][row])
            # print("extRvel1", vel[0])
            # print(isdecel)
            if ave_vel < 720*(1-decel_margin)  and data['ExtRVel'][row] >= 720*(1-decel_margin) and vel[0] <= 720*(1-decel_margin) and isdecel:
                decel_start = data['Time'][row]
                print(data['ExtRVel'][row])
                print("yes", decel_start)
                print("no", decel_end)
            if data['ExtRVel'][row] <= 720*zero_margin and decel_start != 0:
                decel_end = data['Time'][row]
                print("decel end", decel_end)
            if decel_end != 0 and decel_start != 0:
                print("decel time", decel_end - decel_start)
                decel_times.append(decel_end - decel_start)
                #print("decel Time", decel_times)
                decel_end = 0
                decel_start = 0

    print(decel_times)
    plt.plot(decel_times, 'o')
    plt.ylabel('Deceleration time (s)')
    plt.xlabel('Turn #')
    plt.title('Plot of all Deceleration times')

    plt.show()


    #find accel time

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parse_fixture()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
