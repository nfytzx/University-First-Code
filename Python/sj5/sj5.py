import pandas as pd             # 导入 Pandas 库，用于处理 Excel 数据和表格操作
import matplotlib.pyplot as plt # 导入 Matplotlib 的绘图模块，用于画图
import numpy as np              # 导入 Numpy 库，用于生成数字坐标和数值计算

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
df = pd.read_excel("data.xlsx", index_col=0) # 读取名为 "data.xlsx" 的 Excel 文件，并将第一列（索引列）作为行索引
arr = df.to_numpy()                          # 将 DataFrame 数据转换为 Numpy 数组，方便后续数值提取
x = np.arange(1, 7)                          # 生成一个从 1 到 6 的整数数组 [1, 2, 3, 4, 5, 6]，作为 X 轴的坐标点
y = arr[0:2].astype(float)
months = df.columns # 获取 Excel 表格的列名（如 '1月', '2月' 等），用于后续显示在 X 轴上
plt.plot(x, y[0], '-*b', label='钻石')
plt.plot(x, y[1], '--dr', label='铂金')
plt.xlabel('月份')        # 设置 X 轴的名称为“月份”
plt.ylabel('每月销量')    # 设置 Y 轴的名称为“每月销量”
plt.legend(loc='upper left')
plt.xticks(x, months)
plt.grid()    # 显示网格线，方便观察数据点
plt.show()    # 显示绘制好的图像窗口
