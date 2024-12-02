from xml.etree.ElementTree import ElementTree, fromstring, Comment
from xml.etree.ElementTree import XMLParser as XML
from src.commented_tb import CommentedTreeBuilder

class XMLParser:
    """
    Класс для парсинга XML в словарь Python.
    """
    def parse(self, xml_data):
        """
        Преобразует XML-данные в словарь и собирает комментарии.
        """

        parser = XML(target=CommentedTreeBuilder())
        tree = ElementTree(fromstring(text=xml_data, parser=parser))
        data = {}
        comments = []

        def parse_element(element):
            for item in element:
                if item is Comment:
                    comments.append(item.text.strip())

            if len(element) == 0:
                return element.text.strip() if element.text else ""
            elif all(child.tag == "item" for child in element):
                return [parse_element(child) for child in element]
            else:
                return {child.tag: parse_element(child) for child in element}

        data[tree.getroot().tag] = parse_element(tree.getroot())
        return data, comments
