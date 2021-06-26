import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plot_g = True
plot_T = not plot_g

penData = np.genfromtxt('amplitude_decay.csv', delimiter=',')  #load pendulum data
penData[0][0] = 1.0  #reads as NaN for some reason

angData = np.array([
    (7752,   60),
    (12569,  55),
    (20548,  50),
    (33967,  45),
    (49556,  40),
    (65013,  35),
    (84959,  30),
    (103267, 25),
    (126763, 20),
    (163055, 15),
    (220342, 10),
    (302390, 5)
    ])

#gErr_b: fractional error in beta for angles 5-60 degrees, 5 degree increments
#gErr_L:  fractional error in L for L=0.5 meters

gErr_L = 0.4/57.1

#dx,dy=0.5cm :
#gErr_b = np.array([0.00064021, 0.0013533, 0.00211297, 0.00287934, 0.00361336, 0.00428106, 0.01820461, 0.01983049, 0.02085451, 0.02119163, 0.02079161, 0.01963446])

#dx,dy=0.2cm:
gErr_b = np.array([0.0002560821213531045, 0.00054131993281367, 0.0008451893844335845, 0.0011517359547736214, 0.001445344620687893, 0.0017124251083461604, 0.007281845190574477, 0.007932196593390246, 0.008341802804038682, 0.008476653276197618, 0.008316645179476747, 0.007853782136261046])

#dx,dy=0.1cm:
#gErr_b = np.array([0.0001383432149838611, 0.0003111839170148823, 0.0005118956708978375, 0.0007295857243386685, 0.0009524917478069212, 0.0011695474034259439, 0.005140126016876102, 0.005775272991413986, 0.006256352103029011, 0.006542966076320136, 0.006604394701349181, 0.006416757025444051])



#convert timestamp data to oscillation period
def getPeriods(data):
    times = np.array([(data[i]+data[i-2])/2. for i in range(2,len(data)-1)])
    periods = np.array([data[i]-data[i-2] for i in range(2,len(data)-1)])
    return times, periods

#remove outliers
def cleanData(data):
    for i in range(20,len(data)):
        if data[i] < 1400 or data[i] > 1700:
            data[i] = avg(data[i-20:i])
    return data

#standard average
def avg(vals):
    return sum(vals)/len(vals)

#boxcar average
def bcAvg(vals, n=2):
    newVals = []
    newVals.append(vals[0])
    for i in range(1,n):
        newVals.append(avg(vals[0:i]))
    for i in range(n,len(vals)+1):
        newVals.append(avg(vals[i-n:i]))
    return np.array(newVals)

#calculate gravitation acceleration (with 0.5m string and 39 quarters)
def calc_g(periods):
    L = 0.5707
    return 4*(np.pi**2)*L/(periods**2)

#not working, but should give better approximation
def calc_g_advanced(periods, angles):
    a = np.cos(angles*np.pi/180./2.)
    L = 0.5707
    g = 4*(np.pi**2)*(L/((periods/1000.)**2))*(np.log(a)/(1-a))**2
    return g



def plot_vs_time():
    sns.set()
    avgTimes = bcAvg(times, n=20)
    avgPeriods = bcAvg(periods, n=20)
    for i in range(angData.shape[0]):
        plt.plot([angData[i,0]/1000., angData[i,0]/1000.], [0, 20], 'C1:')
    if plot_T:
        plt.plot(avgTimes/1000., avgPeriods/1000.)
        plt.ylim(1.48, 1.63)
        plt.xlabel('Timestamp $(s)$')
        plt.ylabel('Period $(s)$')
        plt.title('Variation in pendulum period with respect to time')
    elif plot_g:
        plt.plot(avgTimes/1000., calc_g(avgPeriods/1000.))
        plt.ylim(8.5, 10.2)
        plt.ylabel('Calculated $g$ $(m/s^2)$')
        plt.title('Variation in calculated $g$ value with respect to time')
    plt.show()


def plot_vs_angle():
    angles_x = []
    angles_y = []
    
    for i in range(1, angData.shape[0]):
        t0 = angData[i-1,0]
        t1 = angData[i,0]
        t0_index = None
        t1_index = None
    
        for j in range(len(times)):
            if times[j] >= t0 and t0_index == None:
                t0_index = j
            if times[j] >= t1 and t1_index == None:
                t1_index = j
                break

        angles_x.extend(np.linspace(angData[i-1,1], angData[i,1], t1_index-t0_index))
        angles_y.extend(periods[t0_index:t1_index])

    angles_x = bcAvg(angles_x, 10)
    angles_y = bcAvg(angles_y, 10)

    sns.set()
    if plot_T:
        plt.plot(angles_x, angles_y/1000., 'C0')
        plt.xlabel('Amplitude $($degrees$)$')
        plt.ylabel('Period $(s)$')
        plt.title('Variation in pendulum period with respect to amplitude')
    elif plot_g:

        thVals = np.flip(angles_x)
        gErr_b_interp = np.array([]) #interpolated error values for beta
        i_start = 0
        i_end = 0
        interval = 0
        for i,th in enumerate(thVals):
            if th >= 5*(interval+1):
                i_end = i
                num = i_end - i_start + 1
                gErr_b_interp = np.append(gErr_b_interp, np.linspace(gErr_b[interval], gErr_b[interval+1], num, endpoint=False))
                i_start = i_end
                interval += 1
            if interval+1 == len(gErr_b):
                break

        # I have an off-by-one error somewhere, just duplicating last value
        gErr_b_interp = np.append(gErr_b_interp, gErr_b_interp[-1])
        gErr_b_interp = np.flip(gErr_b_interp)  #angles_x is flipped, who fuckin' knows why

        print("Length of angles_x: {}".format(angles_x.size))
        print("Length of test: {}".format(gErr_b_interp.size))
        print(gErr_b_interp)

        shift_T = 8.8 #(ms) Period shift, attempt to correct for error due to wind

        g_simple   = calc_g((angles_y+shift_T)/1000.)
        g_advanced = calc_g_advanced(angles_y+shift_T, angles_x)

        #shift = 0#.192   #Used to correct for systematic error introduced by wind
        
        plt.fill_between(angles_x, g_simple*(1+gErr_L), g_simple*(1-gErr_L), color=(0.122, 0.467, 0.706, 0.2))
        plt.fill_between(angles_x, g_advanced*(1+gErr_b_interp+gErr_L), g_advanced*(1-gErr_b_interp-gErr_L), color=(1.0, 0.498, 0.055, 0.2))
        plt.plot(angles_x, g_simple, label='Small angle approx.')
        plt.plot(angles_x, g_advanced, label='Lima and Arun')
        
        plt.ylim(8.53, 10.27)
        plt.legend(loc=6)
        plt.xlabel('Amplitude $(\degree)$')
        plt.ylabel('Calculated $g$ $(m/s^2)$')
        plt.suptitle('Calculated value of $g$ at different amplitudes')
        plt.title('(Corrected)')
    plt.show()


    # Plot small-angle error as fraction of Lima-Arun approximation
    p_diff = (g_advanced - g_simple) / g_advanced * 100
    plt.plot(angles_x, p_diff)
    plt.xlabel('Amplitude $(\degree)$')
    plt.ylabel('Percent difference $(\%)$')
    plt.suptitle('Percent difference of small angle vs Lima-Arun approximations')
    plt.show()

    #print(np.array(list(zip(angles_x, angles_y/1000.))))

    g_filter = (angles_x >= 10)*(angles_x <= 30)  #used to pick out g values between 10 and 30 degrees amplitude
    g_estimate = np.sum(g_advanced*g_filter) / np.sum(g_filter)
    err_estimate = np.sum((gErr_L + gErr_b_interp)*g_filter) / np.sum(g_filter) * g_estimate
    print('Best estimate of g: {}+-{} m/s^2'.format(g_estimate, err_estimate))
    


def plot_vs_length():
    lenData = np.genfromtxt('length_vs_g.csv', delimiter=',')  #load length data
    lenData[0][0] = 0.2  #reads as NaN for some reason

    lengths = lenData[:,0]
    g_vals = lenData[:,1:] * 1.009  #beta factor for Lima-Arun approximation
    g_avgs = np.mean(g_vals, axis=1)
    g_errs = (0.004/lengths + 0.000845) * g_avgs  #add error for Lima-Arun

    sns.set()
    for i in range(5):
        plt.errorbar(lengths[i], g_avgs[i], yerr=g_errs[i], fmt='o')
    plt.xlabel('Pendulum length $(m)$')
    plt.ylabel('Calculated g $(m/s^2)$')
    plt.suptitle('Effect of length on calculated $g$ value')
    plt.show()


def plot_vs_mass():
    massData = np.genfromtxt('mass_vs_g.csv', delimiter=',')
    massData[0,0] = 39
    
    masses = massData[:,0]*5.644 + 11.2 #convert to grams, add bottle mass
    g_vals = massData[:,1:]

    sns.set()
    for i in range(3):
        plt.scatter(masses[i]*np.ones(5), g_vals[i,:])
    plt.xlim(0,250)
    plt.xlabel('Pendulum mass $(g)$')
    plt.ylabel('Calculated g $(m/s^2)$')
    plt.suptitle('Effect of mass on calculated $g$ value')
    plt.show()


timestamps = penData[:,1]
times, periods = getPeriods(timestamps)
periods = cleanData(periods)


#plot_vs_time()
#plot_vs_angle()
plot_vs_length()
#plot_vs_mass()
