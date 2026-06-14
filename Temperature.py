import csv
from datetime import datetime

dates = []
temps = []

with open("temperature.csv", encoding="utf-8") as file: #Загружаем данные из файла
    reader = csv.DictReader(file)

    for row in reader:
        dates.append(row["date"])
        temps.append(float(row["temperature"]))


# Префиксные суммы

def pref(arr):
    prefix = [0] * len(arr)
    prefix[0] = arr[0]

    for i in range(1, len(arr)):
        prefix[i] = prefix[i - 1] + arr[i]

    return prefix


def prefix_sum(prefix, l, r):
    if l == 0:
        return prefix[r]
    return prefix[r] - prefix[l - 1]


def average_temp(prefix, l, r):
    return prefix_sum(prefix, l, r) / (r - l + 1)


prefix = pref(temps)

# Средняя температура за любой период
print( "Средняя температура за период:", round((average_temp(prefix, 8, 18)), 2))

# Вычисление средних температур каждого месяца

months = {}

for i, date in enumerate(dates):
    month = datetime.strptime(date, "%Y-%m-%d").month #Пользуясь функционалом библиотеки datetime заполняем наш словарь по месяцам

    if month not in months:
        months[month] = []

    months[month].append(i)

monthly_avg = {}

for month, indices in months.items(): # Вычисляем с помощью префиксных сумм среднюю температуру для каждого месяца
    left = indices[0]
    right = indices[-1]

    avg = average_temp(prefix, left, right)
    monthly_avg[month] = avg

print("Средняя температура по месяцам:")

for month, avg in monthly_avg.items():
    print(f"Месяц {month}: {avg:.2f}")



# линейный поиск


max_temp = temps[0]
min_temp = temps[0]

max_date = dates[0]
min_date = dates[0]

for i in range(len(temps)):

    if temps[i] > max_temp:
        max_temp = temps[i]
        max_date = dates[i]

    if temps[i] < min_temp:
        min_temp = temps[i]
        min_date = dates[i]

print("Самый теплый день:", max_date, max_temp)


print("Самый холодный день:", min_date, min_temp)


# сортировка
sorted_months = sorted(
    monthly_avg.items(),
    key=lambda x: x[1],
    reverse=True
)

print("\nМесяцы по убыванию температуры:")

for month, avg in sorted_months:
    print(f"Месяц {month}: {avg:.2f}")


# Класс бинарного дерева для быстрого поиска дней с температурой выше заданной
class BSTTemp:
    def __init__(self, temp, date):
        self.temp = temp
        self.dates = [date]   # Список дат с одинаковой температурой
        self.left = None
        self.right = None


def bst_insert(tree, temp, date): # Функция для построения дерева
    if tree is None:
        return BSTTemp(temp, date)
    if temp < tree.temp: # Если меньше - добавляем в левое поддерево
        tree.left = bst_insert(tree.left, temp, date)
    elif temp > tree.temp: # Если больше - добавляем в правое поддерево
        tree.right = bst_insert(tree.right, temp, date)
    else:  # Если равная температура, то добавляем дату в существующий узел
        tree.dates.append(date)
    return tree


# Функция для сбора всех дат из поддерева (без проверки температуры)
def collect_all_dates(tree, result):
    if tree is None:
        return
    result.extend(tree.dates)
    collect_all_dates(tree.left, result)
    collect_all_dates(tree.right, result)

# Функция для поиска дат из дерева
def search_above_threshold(tree, threshold, result):
    if tree is None:
        return
    if tree.temp > threshold:  # Если текущий узел подходит, то добавляем его даты
        result.extend(tree.dates)

        search_above_threshold(tree.left, threshold, result) # Проверяем левую ветвь

        # Правое поддерево подходит полностью – добавляем все даты без проверок
        collect_all_dates(tree.right, result)
    else: # Левое поддерево можно полностью пропустить, так как меньше порога
        search_above_threshold(tree.right, threshold, result)


# Построение дерева
tree = None
for data, temp in zip(dates, temps):
    tree = bst_insert(tree, temp, data)

# Ввод порога с проверкой данных
def search_by_query():
    while True:
        try:
            threshold = float(input("Введите порог температуры: "))
            break
        except ValueError:
            print("Ошибка: введите число (например, 25.0 или -5). Попробуйте снова.")

    dates_above = []
    search_above_threshold(tree, threshold, dates_above)
    print(f"Всего дней с температурой выше {threshold} градусов: {len(dates_above)}")
    print(f"Дни с температурой выше {threshold} градусов:")
    if dates_above:
        for data in dates_above:
            print(data)
    else:
        print("Нет таких дней.")


class Queue: # Класс очереди для сглаживания ряда
    def __init__(self):
        self.items = []

    # Метод добавления элемента в очередь
    def push(self, value):
        self.items.append(value)

    # Метод, который удаляет и возвращает первый элемент очереди
    def pop(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    # Метод проверки очереди на наличие элементов
    def is_empty(self):
        return len(self.items) == 0

    # Метод, возвращающий все элементы очереди
    def get_all(self):
        return self.items[:]


def smooth_with_queue(temps, window=7):
    """
    Возвращает новый список, сглаженный центрированным скользящим средним.
    Для краёв (первые и последние window//2 дней) оставляются исходные значения.
    """
    n = len(temps)
    half = window // 2
    smoothed = temps[:] # Создаем копию элементов
    smooth_queue = Queue()
    window_sum = 0

    # Заполняем очередь первыми window элементами
    for i in range(window):
        smooth_queue.push(temps[i])
        window_sum += temps[i]

    # Проходим по индексам от half до n-half-1
    for i in range(half, n - half):
        if i > half:
            # Удаляем выходящий элемент слева
            elem_out = smooth_queue.pop()
            window_sum -= elem_out

            # Добавляем новый элемент справа
            new_elem = temps[i + half]
            smooth_queue.push(new_elem)
            window_sum += new_elem
        smoothed[i] = window_sum / window

    return smoothed


history_stack = [] # Сохраняем предыдущие состояния температур

# Функция сглаживания
def apply_smoothing():
    global temps # Создаем глобальную переменную

    # Сохраняем в стек и сглаживаем данные
    history_stack.append(temps[:])
    temps = smooth_with_queue(temps)
    print("Сглаживание применено")


# Функция удаления последнего сглаживания
def undo_smoothing():
    global temps # Работаем с глобальной переменной
    if history_stack:
        temps = history_stack.pop() # Возвращаем предыдущее состояние
        print("Последнее сглаживание отменено")
    else:
        print("Нет операций для отмены")


# Функция для показа произвольного количества данных
def show_temperatures(count):
    if count > len(temps):
        count = len(temps)
    # Выводим список температур, округлённых до 2 знаков
    temps_list = [round(temps[i], 2) for i in range(count)]
    print(f"Температура за первые {count} дней: {temps_list}")


# Меню для взаимодействия
def main():
    print("\nДоступные команды:")
    print("1 — показать первые N дней")
    print("2 — применить сглаживание (скользящее среднее, окно 7)")
    print("3 — отменить последнее сглаживание")
    print("4 — поиск дней в изначальных данных с температурой выше заданной")
    print("0 — выход")


    while True:
        num = input("\nВведите команду (0-4): ").strip()
        if num == "0":
            print("Выход из программы.")
            break
        elif num == "1":
            # Запрашиваем количество дней
            count = int(input("Сколько первых дней показать? "))
            if count <= 0:
                print("Введите положительное число.")
            else:
                show_temperatures(count)
        elif num == "2":
            apply_smoothing()
        elif num == "3":
            undo_smoothing()
        elif num == "4":
            search_by_query()
        else:
            print("Неизвестная команда. Введите 0, 1, 2, 3 или 4.")

if __name__ == "__main__":
    main()