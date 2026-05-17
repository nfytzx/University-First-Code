#程序文件ex2_49.py
import matplotlib.pyplot as plt
import numpy as np
x=np.linspace(-4,4,100);
x,y=np.meshgrid(x,x)#生成网格坐标矩阵
z=50*np.sin(x+y);
ax=plt.axes(projection='3d')# 使用 plot_surface 方法绘制曲面
ax.plot_surface(x, y, z, color='y')
plt.show()
