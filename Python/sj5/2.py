import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

fruits = ['苹果', '香蕉', '橙子', '葡萄', '西瓜']
sales = [30, 45, 20, 15, 10]# 销售数量
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff6666']# 颜色设置

plt.figure(figsize=(10, 5))#设置画布大小为 宽10英寸，高5英寸
plt.subplot(1, 2, 1)#表示将画布分为 1行2列，当前选中第1个位置
plt.pie(sales, labels=fruits, colors=colors, startangle=90, autopct='%1.1f%%')
plt.title('水果销售占比 (饼图)', fontsize=14) # 设置标题
plt.subplot(1, 2, 2)#表示将画布分为 1行2列，当前选中第2个位置
plt.bar(fruits, sales, color=colors)
plt.title('水果销售数量 (柱形图)', fontsize=14) # 设置标题
plt.xlabel('水果种类') # X轴标签
plt.ylabel('销售数量') # Y轴标签

plt.tight_layout() # 自动调整子图间距，防止重叠
plt.show()