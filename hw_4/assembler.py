import argparse
from src.UVMAssembler import UVMAssembler

def main():
    parser = argparse.ArgumentParser(description='UVM Assembler')
    parser.add_argument('input', help='Входной файл с исходным кодом')
    parser.add_argument('output', help='Выходной бинарный файл')
    parser.add_argument('--log', help='Файл лога', default='uvm_assembly.csv')
    
    args = parser.parse_args()
    
    assembler = UVMAssembler()
    assembler.assemble(args.input, args.output, args.log)
    print(f"Ассемблирование завершено. Результат в {args.output}")

if __name__ == '__main__':
    main()