"""
Defines methods that are commonly used in Generator classes.
"""

def split_factory(split_by=',', cast_to=list, remove_empty=True, strip = True):
    """
    Creates a uniform function split by a selected expression.

    :param str split_by: Splitting expression
    :param type cast_to: Result type
    :param bool remove_empty: Determines if empty strings should be added to the container
    :param bool strip: Determines if the input is going to be stripped
    of special characters and whitespaces
    :return function: Splitting function
    """

    try:
        assert isinstance(cast_to, type)
    except AssertionError:
        raise RuntimeError('cast_to has to be a type. For example, use set instead of set().')

    def wrapper(text):
        """
        Resulting function of split_factory. Splits text by a predefined expression.

        :param str text:
        :return:
        """

        container = list()

        if strip:
            processor = lambda t : t.strip()
        else:
            processor = lambda t : t

        for part in text.split(split_by):
            if remove_empty:
                if processor(part) != '':
                    container.append(processor(part))
            else:
                container.append(processor(part))

        return cast_to(container)

    return wrapper

def split_factory2(delimiter: str = ',', cast_to: type = list):
    """
    Separates a text by a specific delimiter into separate sub-lists.

    Returns a FUNCTION that can then process the text accordingly.

    It DOES NOT ignore whitespaces.
    *-------------------------------------------------------------*
    ESCAPING ESCAPES *ONLY* A SINGLE CHARACTER AFTER ESCAPE SYMBOL.

    IF YOU HAVE TO ESCAPE MORE THAN ONE CHARACTER THEN ESCAPE EVERY
    SINGLE ONE INDIVIDUALLY.
    *-------------------------------------------------------------*

    Created because the original split factory had a huge flaw where
    the vocabulary of a splitter did not accept delimiters and newlines.

    :param str delimiter: separates individual objects
    :param type cast_to: defines the type of iterable that the item container is
    going to be
    :return function: a function that does the separation
    """
    def wrapper(text, remove_empty: bool = False)->list:
        """
        Return-function that actually processes the text.

        :param str text: text to process
        :param bool remove_empty: defines if empty items are going to be removed or not
        :return list: a list of split lines and items
        """
        def list_to_str(this: list)->str:
            """
            Concatenates all items from a list to a single string.

            :param list this: a list of items
            :return str: concatenated string
            """
            res = ''
            for item in this:
                res = item if isinstance(item, str) else repr(item)
            return res

        def add_to_result(line: str):
            """
            Adds a line to the result

            :param line: a line
            :return:
            """
            if remove_empty:
                if line:
                    result.append(line)
            else:
                result.append(line)

        result = []

        text = list(text)

        current_item = ''

        while text:
            char = text.pop(0)
            if char == '\\':
                new_char = text.pop(0)
                current_item += char + new_char
            elif char == delimiter[0]:
                if char + list_to_str(text[:len(delimiter) - 1]) == delimiter:
                    add_to_result(current_item)
                    current_item = ''
                    del(text[:len(delimiter) - 1])
            else:
                current_item += char
        add_to_result(current_item)
        return cast_to(result)
    return wrapper

SPLIT_COMMA_SET = split_factory(',', set)
SPLIT_COMMA_LIST = split_factory(',', list)

SPLIT_NEWLINE_SET = split_factory('\n', set)
SPLIT_NEWLINE_LIST = split_factory('\n', list)

SPLIT_LINES_WITHOUT_REMOVAL = split_factory('\n', list, False)

NEW_SPLIT_COMMA = split_factory2()
NEW_SPLIT_NEWLINE = split_factory2('\n')