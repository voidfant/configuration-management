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
                if item.tag is Comment:
                    comments.append(item.text.strip())
            print(element.tag)
            if len(element) == 0:
                return element.text.strip() if element.text else ""
            elif len(set(child.tag for child in element)) == 1:
                return [parse_element(child) for child in element]
            else:
                result = {}
                comments_count = 0
                for child in element:
                    element_tag = ''
                    if child.tag is Comment:
                        element_tag = f'comment_{comments_count}'
                        comments_count += 1
                    else:
                        element_tag = child.tag
                    result[element_tag] = parse_element(child)
                return result

        data[tree.getroot().tag] = parse_element(tree.getroot())
        return data, comments
