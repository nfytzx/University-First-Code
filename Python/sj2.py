def factorial(n):
    r = 1
    while n > 1:
        r *= n
        n -= 1
    return (r)

def fib(n):
    a, b = 1, 1
    while a < n:
        print(a, end=' ')
        a , b = b , a + b
