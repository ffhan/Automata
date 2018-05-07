def split_factory(split_by = ',', cast_to = list, remove_empty = True):
    """
    Creates a uniform function split by a selected expression.

    :param str split_by: Splitting expression
    :param type cast_to: Result type
    :param bool remove_empty: Determines if empty strings should be added to the container
    :return function: Splitting function
    """

    try:
        assert type(cast_to) is type
    except AssertionError:
        raise RuntimeError('cast_to has to be a type. For example, use set instead of set().')

    def wrapper(text):
        """
        Resulting function of split_factory. Splits text by a predefined expression.

        :param str text:
        :return:
        """

        container = list()

        for part in text.split(split_by):
            if remove_empty:
                if part.strip() != '':
                    container.append(part.strip())
            else:
                container.append(part.strip())

        return cast_to(container)

    return wrapper

split_coma_set = split_factory(',', set)
split_coma_list = split_factory(',', list)

split_newline_set = split_factory('\n', set)
split_newline_list = split_factory('\n', list)

split_lines_without_removal = split_factory('\n', list, False)