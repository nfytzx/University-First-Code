str1 = 'abc abc abc abc'
print(str1.rfind('bc'))
print(str1.find('e'))
print(str1.index('b'))
print(str1.rindex('bc'))
print(str1.count('ab'))
print(str1.split())
print(str1.rsplit('c'))
str2 = '2026'
print('-'.join(str2))
print(str1.strip('a'))
print(str1.rstrip('c'))
print(str1.lstrip('a'))
print(str1.startswith('b'))
l = ['1.2','as',123,True]
print(l[-1])
l[-1] = 'or'
print(l)
l[2:4] = []
print(l)
#用列表推导式实现嵌套列表的平铺
#列表推导式=对元素的操作 for
a = [[1,2,3],[4,5,6],[7,8,9]]
d = [c for b in a for c in b]
print(d)
ad = set('adfgad')
print(ad)
p = {'name':'nfy','age':18}
print(p)
name = p.get('name')
print(name)
age = p.get('age')
print(age)
p.update({'name':'sx','age':19})
print(p)
p.pop('name')
print(p)
p.pop('age')
print(p)