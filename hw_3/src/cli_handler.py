import traceback

from src.xml_parser import XMLParser
from src.config_generator import ConfigGenerator

class CLIHandler:
    """
    Класс для работы с командной строкой и управления процессом.
    """
    def __init__(self):
        self.parser = XMLParser()
        self.generator = ConfigGenerator()

    def process(self, input_data, output_file):
        try:
            parsed_data, comments = self.parser.parse(input_data)

            config_text = self.generator.generate(parsed_data, comments=comments)

            with open(output_file, "w") as f:
                f.write(config_text)

            print(f"Конфигурация успешно записана в файл {output_file}")
        except SyntaxError:
            print(f"Синтаксическая ошибка: {traceback.format_exc()}")
        except Exception:
            print(f"Ошибка: {traceback.format_exc()}")
