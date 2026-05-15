import math


class BaseSimulator:
    def __init__(self):
        self.history = []

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history.clear()


class AbacusSimulator(BaseSimulator):
    """Эмулятор римского абака / русских счетов"""
    def __init__(self, wires_count=7):
        super().__init__()
        self.wires_count = wires_count
        self.rows = {i: 0 for i in range(wires_count)}  # {разряд: количество костяшек}

    def reset(self):
        for i in self.rows:
            self.rows[i] = 0
        self.history.append("Сброс абака")

    def set_value(self, value: int):
        if value < 0 or value >= 10 ** self.wires_count:
            raise ValueError("Число не помещается на счетах")
        self.reset()
        val_str = str(value).zfill(self.wires_count)[::-1]
        for i, digit in enumerate(val_str):
            self.rows[i] = int(digit)
        self.history.append(f"Установлено значение: {value}")

    def get_value(self) -> int:
        value = 0
        for i in range(self.wires_count):
            value += self.rows[i] * (10 ** i)
        return value

    def add_beads(self, wire_index: int, count: int):
        if wire_index not in self.rows:
            raise IndexError("Неверный индекс разряда")
        current = self.rows[wire_index]
        if current + count > 9:
            self.rows[wire_index] = (current + count) % 10
            self.history.append(f"Перенос из разряда {wire_index}")
            self.add_beads(wire_index + 1, (current + count) // 10)
        else:
            self.rows[wire_index] += count


class PascalinaSimulator(BaseSimulator):
    """Эмулятор суммирующей машины Блеза Паскаля (Pascaline)"""
    def __init__(self, wheels_count=6):
        super().__init__()
        self.wheels_count = wheels_count
        self.wheels = [0] * wheels_count  # Колеса от младшего к старшему

    def get_state(self):
        return "".join(map(str, self.wheels[::-1]))

    def add_number(self, number: int):
        if number < 0:
            raise ValueError("Паскалина поддерживает только сложение положительных чисел")
        self.history.append(f"Прибавление числа {number} к текущему состоянию {self.get_state()}")
        
        num_str = str(number).zfill(self.wheels_count)[::-1]
        carry = 0
        
        for i in range(self.wheels_count):
            digit = int(num_str[i]) if i < len(num_str) else 0
            total = self.wheels[i] + digit + carry
            self.wheels[i] = total % 10
            carry = total // 10
            
            if digit > 0 or carry > 0:
                self.history.append(f"Колесо {i} повернулось. Текущее значение: {self.wheels[i]}")
        
        if carry > 0:
            self.history.append("Переполнение старшего разряда машины!")


class ArithmometerSimulator(BaseSimulator):
    """Эмулятор механического арифмометра Однера (Вилгодта Однера)"""
    def __init__(self):
        super().__init__()
        self.setting_mechanism = 0  # Рычаги установки
        self.accumulator_register = 0  # Основной счетчик результатов
        self.counting_register = 0  # Счетчик оборотов рукоятки
        self.carriage_position = 0  # Сдвиг каретки (0 - единицы, 1 - десятки и т.д.)

    def set_levers(self, value: int):
        if 0 <= value <= 999999:
            self.setting_mechanism = value
            self.history.append(f"Рычаги установлены на: {value}")
        else:
            raise ValueError("Недопустимое значение на рычагах")

    def shift_carriage(self, direction: int):
        if direction not in [-1, 1]:
            return
        new_pos = self.carriage_position + direction
        if 0 <= new_pos <= 4:
            self.carriage_position = new_pos
            self.history.append(f"Каретка сдвинута в позицию: {self.carriage_position}")

    def turn_handle_forward(self):
        added_value = self.setting_mechanism * (10 ** self.carriage_position)
        self.accumulator_register += added_value
        self.counting_register += 1 * (10 ** self.carriage_position)
        self.history.append(f"Вращение вперед. Добавлено: {added_value}")

    def turn_handle_backward(self):
        subbed_value = self.setting_mechanism * (10 ** self.carriage_position)
        self.accumulator_register -= subbed_value
        self.counting_register -= 1 * (10 ** self.carriage_position)
        self.history.append(f"Вращение назад. Вычтено: {subbed_value}")

    def clear_registers(self, accum=True, count=True):
        if accum:
            self.accumulator_register = 0
        if count:
            self.counting_register = 0
        self.history.append(f"Сброс регистров (Результат: {accum}, Обороты: {count})")


class RpnCalculatorB334(BaseSimulator):
    """Эмулятор советского программируемого калькулятора Электроника Б3-34 (Микро-ЭВМ)"""
    def __init__(self):
        super().__init__()
        self.stack = [0.0, 0.0, 0.0, 0.0]  # Регистры X, Y, Z, T
        self.memory = {f"RG{i}": 0.0 for i in range(10)}  # Регистры памяти 0-9
        self.program = []  # Список команд для автоматического режима
        self.pc = 0  # Указатель команды (Program Counter)

    def push_stack(self, value: float):
        self.stack[3] = self.stack[2]
        self.stack[2] = self.stack[1]
        self.stack[1] = self.stack[0]
        self.stack[0] = value

    def enter(self):
        """Клавиша 'ПП^' (Ввод числа в стек)"""
        self.push_stack(self.stack[0])
        self.history.append("Стек сдвинут (команда Ввод)")

    def execute_operation(self, op: str):
        self.history.append(f"Выполнение операции: {op}")
        if op == "+":
            res = self.stack[1] + self.stack[0]
            self.stack[0] = res
            self.stack[1] = self.stack[2]
            self.stack[2] = self.stack[3]
        elif op == "-":
            res = self.stack[1] - self.stack[0]
            self.stack[0] = res
            self.stack[1] = self.stack[2]
            self.stack[2] = self.stack[3]
        elif op == "*":
            res = self.stack[1] * self.stack[0]
            self.stack[0] = res
            self.stack[1] = self.stack[2]
            self.stack[2] = self.stack[3]
        elif op == "/":
            if self.stack[0] == 0:
                self.stack[0] = "ЕГГ"  # Знаменитая ошибка Б3-34 ("ЕГГОГ")
                return
            res = self.stack[1] / self.stack[0]
            self.stack[0] = res
            self.stack[1] = self.stack[2]
            self.stack[2] = self.stack[3]
        elif op == "XY":
            self.stack[0], self.stack[1] = self.stack[1], self.stack[0]
        elif op == "CX":
            self.stack[0] = 0.0

    def store_memory(self, reg_index: int):
        reg_key = f"RG{reg_index}"
        if reg_key in self.memory:
            self.memory[reg_key] = self.stack[0]
            self.history.append(f"Значение {self.stack[0]} сохранено в {reg_key}")

    def load_memory(self, reg_index: int):
        reg_key = f"RG{reg_index}"
        if reg_key in self.memory:
            self.push_stack(self.memory[reg_key])
            self.history.append(f"Значение из {reg_key} загружено в стек X")

    def load_program(self, instructions: list):
        self.program = instructions
        self.pc = 0
        self.history.append(f"Загружена программа из {len(instructions)} шагов")

    def step_program(self):
        if self.pc >= len(self.program):
            return False
        cmd = self.program[self.pc]
        if cmd in ["+", "-", "*", "/"]:
            self.execute_operation(cmd)
        elif cmd.startswith("P"):  # Запись в регистр
            self.store_memory(int(cmd[1]))
        elif cmd.startswith("I"):  # Чтение из регистра
            self.load_memory(int(cmd[1]))
        self.pc += 1
        return True