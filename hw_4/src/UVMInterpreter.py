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
        # Распечатываем raw bytes для отладки
        print(f"Raw bytes: {instruction_bytes.hex()}")
        
        instruction = struct.unpack('<I', instruction_bytes)[0]
        
        # Подробная отладочная информация
        print(f"Raw instruction value: {instruction}")
        
        a = instruction & 0x3F  # Биты 0-5
        b = (instruction >> 6) & 0x1F  # Биты 6-10
        c = (instruction >> 11) & 0x1FFF  # Биты 11-23
        
        print(f"Decoded: A={a}, B={b}, C={c}")
        return a, b, c

    def execute(self, binary_file, output_file, start_range, end_range):
        with open(binary_file, 'rb') as f:
            binary_code = f.read()
        
        print(f"Total binary code length: {len(binary_code)} bytes")
        
        # Выполнение инструкций
        i = 0
        while i < len(binary_code):
            instruction_bytes = binary_code[i:i+4]
            
            print(f"\n--- Instruction at offset {i} ---")
            a, b, c = self.decode_instruction(instruction_bytes)
            
            if a == 7:  # LOAD_CONST
                self.registers[b] = c
                print(f"LOAD_CONST: R[{b}] = {c}")
            elif a == 49:  # READ_MEM
                self.registers[b] = self.memory[c]
                print(f"READ_MEM: R[{b}] = Memory[{c}] = {self.memory[c]}")
            elif a == 51:  # WRITE_MEM
                self.memory[c] = self.registers[b]
                print(f"WRITE_MEM: Memory[{c}] = R[{b}] = {self.registers[b]}")
            elif a == 55:  # UNARY_MINUS
                self.registers[b] = -self.registers[c]
                print(f"UNARY_MINUS: R[{b}] = -R[{c}] = {self.registers[b]}")
            
            # Используем фиксированный шаг 4 байта
            i += 4
        
        # Сохранение результата в диапазоне памяти
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Address', 'Value'])
            for addr in range(start_range, end_range + 1):
                writer.writerow([addr, self.memory[addr]])
                print(f"Memory[{addr}] = {self.memory[addr]}")
