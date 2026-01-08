#课忘去了不知道怎么要求的可能是错的
n = int(input("请输入一个正整数 n: "))
i = 1
while i <= n:
    if i % 3 == 0:
        print("*")
    else:
     print(i)
    i += 1
#上面的是需要自己输入n的取值的，下面的是指定n取值的
n = 100
i = 1
while i <= n:
        if i % 3 == 0:
            print("*")
        else:
            print(i)
        i += 1