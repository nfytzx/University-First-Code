def calc_shipping(weight):
    if weight <= 1:
        return 5.0
    else:
        return 5 + (weight - 1) * 2

weights = [0.5, 3, 12]

for x in weights:
    cost = calc_shipping(x)
    print(f"{x:.2f}kg: {cost:.2f}元")