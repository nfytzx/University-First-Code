import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
x0=np.arange(1,13)
y0=np.array([5,8,9,15,25,29,31,30,22,25,27,24])
x1 =np.linspace(1, 12, 101) #插值点
f1=interp1d(x0,y0)#默认插值方法是linear
y1=f1(x1)
f2=interp1d(x0,y0,'cubic')
y2=f2(x1)
x2=np.array([3.2,5.6,7.8,11.51])
yh1=f1(x2)    #计算线性插值的预测值
yh2=f2(x2)     #计算三次样条插值的预测值
print('分段插值的预测值:',yh1)
print('三次样条插值的预测值',np.round(yh2, 4))
plt. rc('font',size=16)
plt.rc('font', family='SimHei')
plt.subplot(1,2,1)
plt.plot(x1,y1)
plt.xlabel("(A)分段线性插值")
plt.subplot(1,2,2)
plt. plot(x1,y2)
plt.xlabel("(B) 三次样条插值")
plt.show()