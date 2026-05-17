import numpy as np
x0 = np.array([100, 121])
y0 = np.array([10,11])
q0 = lambda x:x-x0[1]
q1 = lambda x:x-x0[0]
y=q0(115)/q0(x0[0])*y0[0]+q1(115)/q1(x0[1])*y0[1]
print(np.round(y,4))