"""
Defines a Parser used for a laboratory exercise.
"""
def parser(text):
    output = ''
    text_input = ''
    def set_input(text):
        nonlocal text_input
        text_input = text.strip()

    def add_output(character):
        nonlocal output
        output += character

    def printer(char, state):
        print("In {} using {}, remaining {}".format(state, char, text_input))

    def get_input(length: int = 1):
        """
        Extracts the first symbol from a text.

        :param str text: string of text
        :param int length: length of extracted characters
        :return: tuple with first element being the character
        and second the rest of the text.
        """
        if text_input:
            character = text_input[0:length]
            set_input(text_input[length:])
            return character
        else:
            return ''

    def S()->bool:
        add_output('S')
        character = get_input()
        # printer(character, 'S')
        if not character:
            return False
        if character == 'a':
            if A():
                return B()
        elif character == 'b':
            if B():
                return A()
        return False

    def A()->bool:
        character = get_input()
        add_output('A')
        # printer(character, 'A')
        if not character:
            return False
        if character == 'b':
            return C()
        elif character == 'a':
            return True
        return False

    def B()->bool:
        character = get_input()
        add_output('B')
        # printer(character, 'B')
        if not character:
            return True
        if character == 'c':
            char2 = get_input()
            character += char2
            if character == 'cc':
                if S():
                    character = get_input(2)
                    if character == 'bc':
                        return True
        else:
            # print('Adding back {}'.format(character))
            set_input(character + text_input)
            return True
        return False

    def C()->bool:
        # character = get_input()
        add_output('C')
        # if not character:
        #     return False
        # printer('nothing', 'C')
        if A() and A():
            return True
        return False
    set_input(text)
    out = S()
    result = output + '\n' + ('DA' if out and not bool(text_input) else 'NE')
    return result
# set_input('bccaabcbaa')
# out = S()
# print(output)
# print('DA' if out else 'NE')
