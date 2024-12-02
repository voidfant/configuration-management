import struct
import csv

class UVMAssembler:
    COMMANDS = {
        'LOAD_CONST': 7,    # Загрузка константы
        'READ_MEM': 49,     # Чтение из памяти
        'WRITE_MEM': 51,    # Запись в память
        'UNARY_MINUS': 55   # Унарный минус
    }

    def __init__(self):
        self.symbol_table = {}
        self.code = []
        self.log_entries = []

    def parse_line(self, line):
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        parts = line.split()
        if not parts:
            return None

        # Распознавание команд
        command = parts[0].upper()
        
        if command == 'LOAD_CONST':
            return self._parse_load_const(parts)
        elif command == 'READ_MEM':
            return self._parse_read_mem(parts)
        elif command == 'WRITE_MEM':
            return self._parse_write_mem(parts)
        elif command == 'UNARY_MINUS':
            return self._parse_unary_minus(parts)
        
        raise ValueError(f"Неизвестная команда: {command}")

    def _parse_load_const(self, parts):
        # LOAD_CONST B C A
        if len(parts) != 4:
            raise ValueError("Неверное количество аргументов для LOAD_CONST")
        
        b = int(parts[1])
        c = int(parts[2])
        a = self.COMMANDS['LOAD_CONST']
        
        # Упаковка инструкции (4 байта)
        instruction = (a & 0x3F) | ((b & 0x1F) << 6) | ((c & 0x1FFF) << 11)
        raw_bytes = struct.pack('<I', instruction)
        
        log_entry = {
            'operation': 'LOAD_CONST',
            'A': a, 'B': b, 'C': c,
            'raw_bytes': raw_bytes.hex()
        }
        self.log_entries.append(log_entry)
        
        return raw_bytes

    def _parse_read_mem(self, parts):
        # READ_MEM B C A
        if len(parts) != 4:
            raise ValueError("Неверное количество аргументов для READ_MEM")
        
        b = int(parts[1])
        c = int(parts[2])
        a = self.COMMANDS['READ_MEM']
        
        # Упаковка инструкции (4 байта с дополнением)
        instruction = (a & 0x3F) | ((b & 0x1F) << 6) | ((c & 0x1F) << 11)
        raw_bytes = struct.pack('<I', instruction)
        
        log_entry = {
            'operation': 'READ_MEM',
            'A': a, 'B': b, 'C': c,
            'raw_bytes': raw_bytes.hex()
        }
        self.log_entries.append(log_entry)
        
        return raw_bytes

    def _parse_write_mem(self, parts):
        # WRITE_MEM B C A
        if len(parts) != 4:
            raise ValueError("Неверное количество аргументов для WRITE_MEM")
        
        b = int(parts[1])
        c = int(parts[2])
        a = self.COMMANDS['WRITE_MEM']
        
        # Упаковка инструкции (4 байта)
        instruction = (a & 0x3F) | ((b & 0x1F) << 6) | ((c & 0x1FFF) << 11)
        raw_bytes = struct.pack('<I', instruction)
        
        log_entry = {
            'operation': 'WRITE_MEM',
            'A': a, 'B': b, 'C': c,
            'raw_bytes': raw_bytes.hex()
        }
        self.log_entries.append(log_entry)
        
        return raw_bytes

    def _parse_unary_minus(self, parts):
        # UNARY_MINUS B C A
        if len(parts) != 4:
            raise ValueError("Неверное количество аргументов для UNARY_MINUS")
        
        b = int(parts[1])
        c = int(parts[2])
        a = self.COMMANDS['UNARY_MINUS']
        
        # Упаковка инструкции (4 байта с дополнением)
        instruction = (a & 0x3F) | ((b & 0x1F) << 6) | ((c & 0x1F) << 11)
        raw_bytes = struct.pack('<I', instruction)
        
        log_entry = {
            'operation': 'UNARY_MINUS',
            'A': a, 'B': b, 'C': c,
            'raw_bytes': raw_bytes.hex()
        }
        self.log_entries.append(log_entry)
        
        return raw_bytes

    def assemble(self, input_file, output_file, log_file):
        with open(input_file, 'r') as f:
            lines = f.readlines()

        binary_code = bytearray()
        for line in lines:
            instruction = self.parse_line(line)
            if instruction:
                binary_code.extend(instruction)

        with open(output_file, 'wb') as f:
            f.write(binary_code)

        # Запись лога
        with open(log_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['operation', 'A', 'B', 'C', 'raw_bytes'])
            writer.writeheader()
            writer.writerows(self.log_entries)

