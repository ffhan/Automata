"""
Defines methods that are commonly used in Generator classes.
"""

def split_factory(split_by=',', cast_to=list, remove_empty=True, strip = True):
    """
    Creates a uniform function split by a selected expression.

    :param str split_by: Splitting expression
    :param type cast_to: Result type
    :param bool remove_empty: Determines if empty strings should be added to the container
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

SPLIT_COMMA_SET = split_factory(',', set)
SPLIT_COMMA_LIST = split_factory(',', list)

SPLIT_NEWLINE_SET = split_factory('\n', set)
SPLIT_NEWLINE_LIST = split_factory('\n', list)

SPLIT_LINES_WITHOUT_REMOVAL = split_factory('\n', list, False)
