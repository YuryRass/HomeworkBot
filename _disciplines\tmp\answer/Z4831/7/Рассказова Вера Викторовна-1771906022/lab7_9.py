"""Сложить второе число со средним"""


def app():
    my_list = list(map(int, input().strip().split()))
    mid = len(my_list) // 2
    print(my_list[1] + my_list[mid])


if __name__ == "__main__":
    app()
