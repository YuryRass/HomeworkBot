"""На вход подается целочисленное значение n. Используя его, получите решение для следующего выражения:

"""
from math import sqrt
def count_expression(n: int) -> float:
    return round(sqrt(n + sqrt(n**n)) / 7)
