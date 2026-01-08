colors=['red','bull','green']
print(colors[1])
colors[1] = 'yellow'
print(colors[1])
colors.append('white')
print(colors)
colors.remove('red')
print(colors)
print(len(colors))
t1=(1,2,3)
t2=(4,5,6)
print(t1[1])
print(t2)
t3=t1+t2
print(t3)
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
a = 231
b = 465
c = a+b
print(c)

