import unittest
from src.config_generator import ConfigGenerator
from src.xml_parser import XMLParser


class TestXMLParser(unittest.TestCase):
    def setUp(self):
        self.parser = XMLParser()

    def test_simple_xml(self):
        xml_input = "<config><name>Test</name><version>1.0</version></config>"
        expected = {"config": {"name": "Test", "version": "1.0"}}
        result = self.parser.parse(xml_input)[0]
        self.assertEqual(result, expected)

    def test_nested_xml(self):
        xml_input = "<root><settings><option1>true</option1><option2>false</option2></settings></root>"
        expected = {"root": {"settings": {"option1": "true", "option2": "false"}}}
        result = self.parser.parse(xml_input)[0]
        self.assertEqual(result, expected)

    def test_parse_with_comments(self):
        xml = """<?xml version="1.0"?>
        <root>
            <!-- Комментарий внутри -->
            <name>Test</name>
            <version>1.0</version>
        </root>
        """
        data, comments = self.parser.parse(xml)
        expected_data = {"root": {"comment_0": "Комментарий внутри", "name": "Test", "version": "1.0"}}
        expected_comments = ["Комментарий внутри"]
        self.assertEqual(data, expected_data)
        self.assertEqual(comments, expected_comments)


class TestConfigGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ConfigGenerator()

    def test_generate_with_comments(self):
        data = {"config": {"name": "Test", "version": "1.0"}}
        comments = ["Это пример комментария", "Другой комментарий"]
        result = self.generator.generate(data, comments=comments)
        expected = (
            "# Это пример комментария\n"
            "# Другой комментарий\n"
            'global config = table([name = "Test", version = "1.0"]);'
        )
        self.assertEqual(result, expected)

    def test_generate_simple_config(self):
        data = {"config": {"name": "Test", "version": "1.0"}}
        expected = 'global config = table([name = "Test", version = "1.0"]);'
        result = self.generator.generate(data)
        self.assertEqual(result, expected)

    def test_generate_nested_config(self):
        data = {"root": {"settings": {"option1": "true", "option2": "false"}}}
        expected = 'global root = table([settings = table([option1 = "true", option2 = "false"])]);'
        result = self.generator.generate(data)
        self.assertEqual(result, expected)

    def test_evaluate_addition(self):
        data = {"result": "^{5 + 10}"}
        expected = 'global result = 15;'
        result = self.generator.generate(data)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
