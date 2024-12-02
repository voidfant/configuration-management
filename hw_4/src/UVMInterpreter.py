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
        # Гарантированно используем 4 байта для распаковки
        if len(instruction_bytes) < 4:
            instruction_bytes = instruction_bytes + b'\x00' * (4 - len(instruction_bytes))
        
        instruction = struct.unpack('<I', instruction_bytes)[0]

        # Извлечение полей с учетом битовых масок
        a = instruction & 0x3F  # Биты 0-5
        b = (instruction >> 6) & 0x1F  # Биты 6-10
        c = (instruction >> 11) & 0x1FFF  # Биты 11-23

        return a, b, c

    def execute(self, binary_file, output_file, start_range, end_range):
        with open(binary_file, 'rb') as f:
            binary_code = f.read()

        # Выполнение инструкций
        i = 0
        while i < len(binary_code):
            # Пытаемся извлечь следующие 4 байта
            instruction_bytes = binary_code[i:i+4]
            
            a, b, c = self.decode_instruction(instruction_bytes)
            
            if a == 7:  # LOAD_CONST
                self.registers[b] = c
            elif a == 49:  # READ_MEM
                self.registers[c] = self.memory[self.registers[b]]
            elif a == 51:  # WRITE_MEM
                self.memory[c] = self.registers[b]
            elif a == 55:  # UNARY_MINUS
                self.registers[b] = -self.memory[self.registers[c]]
            
            # Используем фиксированный шаг 4 байта
            i += 4

        # Сохранение результата в диапазоне памяти
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Address', 'Value'])
            for addr in range(start_range, end_range + 1):
                writer.writerow([addr, self.memory[addr]])
