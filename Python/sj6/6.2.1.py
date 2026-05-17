import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# 原始数据
# 时间点 (小时): 0, 3, 6, 9, 12, 15, 18, 21,24
time_points = np.array([0, 3, 6, 9, 12, 15, 18, 21, 24])
# 对应的游客人数 (百人)
visitors = np.array([1, 1, 2, 8, 15, 18, 12, 5, 1])

# 创建三次样条插值函数
# kind='cubic' 表示三次样条插值
spline_interp = interp1d(time_points, visitors, kind='cubic', fill_value='extrapolate')

# 生成更密集的时间点 (每隔0.1小时，从0到24)
time_dense = np.arange(0, 24, 0.1)

# 计算插值结果
visitors_dense = spline_interp(time_dense)

# 预测 14:00 和 18:00 的客流量
time_predict = np.array([14, 18])
visitors_predict = spline_interp(time_predict)

# 打印预测结果
print("=" * 50)
print("大雁塔景区客流预测结果")
print("=" * 50)
for t, v in zip(time_predict, visitors_predict):
    hour = int(t)
    minute = int((t - hour) * 60)
    print(f"{hour:02d}:{minute:02d}  →  {v:.0f} 百人 (约 {v*100:.0f} 人)")
print("=" * 50)

# 绘图
plt.figure(figsize=(12, 6), dpi=100)

# 绘制原始离散数据点 (红色圆点)
plt.scatter(time_points, visitors, color='red', s=80, label='原始数据点', zorder=5)

# 绘制平滑曲线 (蓝色线条)
plt.plot(time_dense, visitors_dense, color='blue', linewidth=2, label='三次样条插值曲线')

# 标记预测点
plt.scatter(time_predict, visitors_predict, color='green', s=100,
            marker='D', label='预测点', zorder=5, edgecolors='darkgreen', linewidth=1.5)

# 添加预测点的标注
for t, v in zip(time_predict, visitors_predict):
    plt.annotate(f'{t}:00\n{v:.0f}百人',
                 xy=(t, v),
                 xytext=(t+0.5, v+1.5),
                 fontsize=9,
                 arrowprops=dict(arrowstyle='->', color='gray'))

# 设置图表属性
plt.title('大雁塔景区客流可视化 - 基于三次样条插值', fontsize=16, fontweight='bold')
plt.xlabel('时间 (小时)', fontsize=12)
plt.ylabel('游客人数 (百人)', fontsize=12)
plt.xticks(np.arange(0, 25, 3),
           [f'{h}:00' if h <= 24 else '' for h in np.arange(0, 25, 3)])
plt.xlim(-0.5, 23.5)
plt.ylim(0, max(visitors_predict.max(), visitors.max()) + 3)
plt.grid(True, alpha=0.3, linestyle='--')
plt.legend(loc='upper left', fontsize=11)

# 添加背景色区域 (白天/夜晚区分)
plt.axvspan(6, 18, alpha=0.05, color='yellow', label='白天 (6:00-18:00)')
plt.axvspan(18, 24, alpha=0.05, color='blue', label='夜晚 (18:00-24:00)')
plt.axvspan(0, 6, alpha=0.05, color='blue')

# 显示图表
plt.tight_layout()
plt.savefig('dayanta_passenger_flow.png', dpi=150, bbox_inches='tight')
plt.show()