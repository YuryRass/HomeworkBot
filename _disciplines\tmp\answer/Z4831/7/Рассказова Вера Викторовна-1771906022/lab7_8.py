"""Соединить первое и последнее введенные слова"""


def app():
    my_list = list(map(int, input().split()))
    print(my_list[0] + my_list[-1])


if __name__ == "__main__":
    app()
