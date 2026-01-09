num = 1
count = 0
print("1到20之间的偶数：")
while num <= 20:
    if num % 2 == 0:
        print(num, end=" ")
        count += 1
    num += 1
print(f"总共找到了 {count} 个偶数")