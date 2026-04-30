import numpy as np
A = np.array([[5, 1, 1],[1, 5, 1],[1, 1, 5]])
print("系数矩阵 A：")
print(A)
b = np.array([6, 12, 18])
print("\n常数向量 b：")
print(b)

det_A = np.linalg.det(A)
print(f"\n行列式值 det(A) = {det_A}")

row_norms = np.linalg.norm(A, axis=1, ord=2)
col_norms = np.linalg.norm(A, axis=0, ord=2)

print("\n行向量的 2 范数（保留 3 位小数）：")
print(np.round(row_norms, 3))

print("\n列向量的 2 范数（保留 3 位小数）：")
print(np.round(col_norms, 3))

x = np.linalg.solve(A, b)
print("\n方程组的解 x：")
print(x)