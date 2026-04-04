math = 88
english = 92
science = 76
scores = [math, english, science]
high = max(scores)
low = min(scores)
total = sum(scores)
count = len(scores)
average = round(total / count, 1)
total_str = str(total)
print("统计完成，总分为：" + total_str)