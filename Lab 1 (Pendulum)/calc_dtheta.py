import numpy as np
"""
Goal: do a bunch of nasty math to get uncertainty in theta and ultimately beta.

y:  vertical distance between angle markings and pivot point (two values)
x:  horizontal distance between angle markings and pivot point (depends on angle)
r:  ratio x/y used to calculate theta (theta = arctan(r))
th: angle between string and vertical (depends on r)
a:  quantity used to correct for amplitude in g calculation (depends on th)
b:  correction factor beta used in g calculation (depends on a)
d_: uncertainty in quantity _ (such as dx, dth, etc.)

"""



y1 = 18.4
y2 = 4.9
dy = 0.2  #Originally 0.5cm

x1 = np.array([1.61, 3.24, 4.93, 6.70, 8.58, 10.62]) #5-30, increments of 5 degrees
x2 = np.array([3.43, 4.11, 4.90, 5.84, 7.00, 8.49]) #30-60, increments of 5 degrees
dx = 0.01  #Originally 0.5cm

dth_str = "np.array(["
db_str  = "np.array(["

for i in range(2):
    if i == 0:
        x = x1
        y = y1
    elif i == 1:
        x = x2
        y = y2
        
    r  = x/y
    dr = (x/y)*(dx/x + dy/y)

    th  = np.arctan(r)
    dth = (1/(1+r**2))*dr

    a  = np.cos(th/2.)
    da = np.sin(th/2.)/2.*dth

    b  = (np.log(a)/(1-a))**2
    db = 2*np.log(a)/((1-a)**3)*(np.log(a)+1/a-1)*da

    for val in dth*180/np.pi:
        dth_str += str(val) + ", "
    for val in db/b:
        db_str  += str(-1*val) + ", "

dth_str = dth_str[:-2] + "])"
db_str  =  db_str[:-2] + "])"
print(dth_str)
print(db_str)
