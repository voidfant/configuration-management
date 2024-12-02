import struct
import csv
import binascii

class UVMInterpreter:
    COMMANDS = {
        7: 'LOAD_CONST',
        49: 'READ_MEM',
        51: 'WRITE_MEM',
        55: 'UNARY_MINUS'
    }

    def __init__(self, memory_size=1024):
        self.memory = [0] * memory_size
        self.registers = [0] * 32  # 32 регистра

    def decode_instruction(self, instruction_bytes):
        print(f"Декодирование инструкции: {binascii.hexlify(instruction_bytes)}")
        
        # Дополнение до 4 байт
        if len(instruction_bytes) == 3:
            instruction_bytes = instruction_bytes + b'\x00'
        
        # Если по-прежнему не 4 байта, вызываем исключение
        if len(instruction_bytes) != 4:
            raise ValueError(f"Некорректная длина инструкции: {len(instruction_bytes)} байт")
        
        instruction = struct.unpack('<I', instruction_bytes)[0]
        print(f"Распакованная инструкция: {instruction:08x}")

        # Извлечение полей
        a = instruction & 0x3F
        b = (instruction >> 6) & 0x1F
        c = (instruction >> 11) & 0x1FFF

        print(f"Поля инструкции: A={a}, B={b}, C={c}")
        return a, b, c

    def execute(self, binary_file, output_file, start_range, end_range):
        with open(binary_file, 'rb') as f:
            binary_code = f.read()
        
        print(f"Размер бинарного файла: {len(binary_code)} байт")
        print(f"Содержимое файла (hex): {binascii.hexlify(binary_code)}")

        # Выполнение инструкций
        i = 0
        while i < len(binary_code):
            print(f"\nОбработка инструкции по смещению {i}")
            
            # Пытаемся извлечь 4 байта или оставшиеся байты
            instruction_bytes = binary_code[i:i+4]
            
            try:
                a, b, c = self.decode_instruction(instruction_bytes)
                
                if a == 7:  # LOAD_CONST
                    self.registers[b] = c
                    print(f"LOAD_CONST: Регистр {b} = {c}")
                elif a == 49:  # READ_MEM
                    self.registers[c] = self.memory[self.registers[b]]
                    print(f"READ_MEM: Регистр {c} = {self.registers[c]}")
                elif a == 51:  # WRITE_MEM
                    self.memory[c] = self.registers[b]
                    print(f"WRITE_MEM: Память[{c}] = {self.registers[b]}")
                elif a == 55:  # UNARY_MINUS
                    self.registers[b] = -self.memory[self.registers[c]]
                    print(f"UNARY_MINUS: Регистр {b} = {self.registers[b]}")
                else:
                    print(f"Неизвестная команда: {a}")
                    break
            except Exception as e:
                print(f"Ошибка при декодировании инструкции: {e}")
                break
            
            # Определяем шаг по размеру инструкции
            i += 4

        # Сохранение результата в диапазоне памяти
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Address', 'Value'])
            for addr in range(start_range, end_range + 1):
                writer.writerow([addr, self.memory[addr]])

