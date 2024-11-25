import re


class ConfigGenerator:
    def __init__(self):
        self.operators = {
            '+': lambda x, y: x + y,
        }
        self.functions = {
            'concat': lambda *args: ''.join(map(str, args)),
        }

    def generate(self, data, comments=None):
        """
        Генерирует конфигурацию, включая комментарии.
        """
        def serialize(value):
            if isinstance(value, dict):
                return f"table([{', '.join(f'{k} = {serialize(v)}' for k, v in value.items())}])"
            elif isinstance(value, list):
                return f"array({', '.join(serialize(v) for v in value)})"
            elif isinstance(value, str):
                if value.startswith('^{') and value.endswith('}'):
                    return self._evaluate_expression(value[2:-1])
                return f'"{value}"'
            elif isinstance(value, (int, float)):
                return str(value)
            else:
                raise ValueError(f"Неизвестный тип данных: {type(value)}")

        result = []

        # Добавляем комментарии
        if comments:
            for comment in comments:
                if "\n" in comment:
                    result.append(f"/*\n{comment}\n*/")
                else:
                    result.append(f"# {comment}")

        for key, value in data.items():
            result.append(f"global {key} = {serialize(value)};")
        return "\n".join(result)


    def _evaluate_expression(self, expr):
        """
        Вычисляет выражение, поддерживая сложение и функции, такие как concat().
        """
        # Простой пример: вычисление инфиксных выражений
        match = re.match(r'(\w+)\s*([+])\s*(\w+)', expr)
        if match:
            left, op, right = match.groups()
            if op in self.operators:
                return str(self.operators[op](self._parse_operand(left), self._parse_operand(right)))

        # Обработка функций, например, concat()
        func_match = re.match(r'(\w+)\(([^)]+)\)', expr)
        if func_match:
            func_name, args = func_match.groups()
            args = [self._parse_operand(arg.strip()) for arg in args.split(',')]
            if func_name in self.functions:
                return '\"' + str(self.functions[func_name](*args)) + '\"'

        raise ValueError(f"Некорректное выражение: {expr}")

    def _parse_operand(self, operand):
        """
        Преобразует операнд (строку или число) в подходящий тип.
        """
        if operand.isdigit():
            return int(operand)
        elif operand.startswith('"') and operand.endswith('"'):
            return operand.strip('"')
        raise ValueError(f"Некорректный операнд: {operand}")
