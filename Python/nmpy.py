import numpy as np
l2 = [[1,2,3],[4,5,6],[7,8,9]]
arrz = np.array(l2)
print(arrz)
arr3 = np.arange(0,10,2)
print(arr3)
arr4 = np.linspace(1,9,5)
print(arr4)
arr5 = np.logspace(5,11,3,base=2)
print(arr5)


a = np.ones(4,dtype=int)
print(a)
b = np.ones((4,1),dtype=int)
print(b)
c = np.eye(4)
print(c)
d = np.zeros((4,4),dtype=int)
print(d)
e = np.eye(N=3, k=1)
print(e)
f = np.zeros_like(np.eye(5))
print(f)