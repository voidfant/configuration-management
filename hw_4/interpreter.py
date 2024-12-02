import argparse
from src.UVMInterpreter import UVMInterpreter

def main():
    parser = argparse.ArgumentParser(description='UVM Interpreter')
    parser.add_argument('input', help='Входной бинарный файл')
    parser.add_argument('output', help='Выходной файл результатов')
    parser.add_argument('start', type=int, help='Начало диапазона памяти')
    parser.add_argument('end', type=int, help='Конец диапазона памяти')
    
    args = parser.parse_args()
    
    interpreter = UVMInterpreter()
    interpreter.execute(args.input, args.output, args.start, args.end)
    print(f"Интерпретация завершена. Результат в {args.output}")

if __name__ == '__main__':
    main()