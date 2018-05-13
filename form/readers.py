"""
Defines all readers.
"""
import sys

class Reader:
    """
    Used in handling reading input.
    """

    @staticmethod
    def read_file(file_path):
        """
        Reads a file and outputs it in a single string.

        :param str file_path: File pathname.
        :return str: File content in a string
        """

        text = ''
        with open(file_path, 'r') as file:
            for line in file.readlines():
                text += line
        return text

    @staticmethod
    def read_input():
        """
        Reads a direct input.
        An input ends with CTRL+D.

        Enables inputting from a file through command prompt.

        :return str: Concatenated string of inputs
        """

        read = sys.stdin.readlines()

        text = ''
        for line in read:
            text += line

        return text
