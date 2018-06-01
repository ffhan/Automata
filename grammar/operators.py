"""
Defines all operator abstractions and their respective default operators.
"""
#todo: write extensive tests for this module.
import abc
import automata.nfa as nfa
import form.generators as generator
import misc.errors as err

class Operator(abc.ABC):
    """
    Basic abstraction of Operator interface.
    Contains an operator which might later be used to scan Operators.
    Cannot be instantiated directly.
    """
    # a private static set that contains all valid input types.
    # if it's empty the operator takes in any type
    _item_types = set()

    def __init__(self, operator):
        self._operator = operator

    @property
    def valid_item_types(self):
        """
        Property that returns a static set of all valid item types.
        Exists so that it's not necessary to type in a class name and then
        set name and also to prevent changing valid item types in runtime.

        :return set: set of all valid item types
        """
        # print(self.__class__, self.__class__._item_types)
        return self.__class__._item_types

    def _check_type_err(self, item):
        """
        Raises an OperatorInputTypeError if item type is not acceptable.
        
        :param item: an item that raises the error.
        :return: 
        """
        if not self.valid_item_types:
            return
        valid_flag = False
        for valid_type in self.valid_item_types:
            if isinstance(item, valid_type):
                valid_flag = True

        if not valid_flag:
            raise err.OperatorInputTypeError('{} is an invalid input type!'.format(
                item.__class__.__name__))

    @abc.abstractmethod
    def execute(self)->nfa.EpsilonNFA:
        """
        Executes the Operator: returns an epsilon NFA that describes the operation results.

        :return EpsilonNFA: epsilon NFA that describes the operator results
        """
        pass

class UnaryOperator(Operator):
    """
    Defines an operator that takes in only one item.
    Cannot be instantiated directly.
    """
    def __init__(self, item, operator):
        self._check_type_err(item)
        super().__init__(operator)
        self._item = item
    def __repr__(self):
        return '{' + '{} {}{}'.format(self.__class__.__name__, self._item, self._operator) + '}'

class Single(UnaryOperator):
    """
    Defines a Single operator, meaning exactly one repetitions.
    It can take in a character or an already defined operator.

    Essentially does nothing.
    Example:
        'a' = 'a'
    """
    _item_types = {str, Operator}
    def __init__(self, item):
        super().__init__(item, '')

    def execute(self)->nfa.EpsilonNFA:
        if isinstance(self._item, str):
            enfa = nfa.EpsilonNFA.factory(
                """s0,s1;{0};s1;s0;s0,{0}->s1""".format(self._item),
            generator.StandardFormatSemicolonGenerator())
        elif isinstance(self._item, Operator):
            enfa = self._item.execute()
        return enfa

class BinaryOperator(Operator):#todo: implement operators that take more than 2 items.
    """
    Defines an operator that takes in two items.
    Cannot be instantiated directly.
    """
    def __init__(self, first, last, operator):
        super().__init__(operator)
        self._check_type_err(first)
        self._check_type_err(last)
        self._first = first
        self._last = last

    def __repr__(self):
        return '{' + '{} {}{}{}'.format(self.__class__.__name__,
                                            str(self._first).replace('\t', '\t'*2),
                                            self._operator,
                                            self._last) + '}'

class GeneralOperator(Operator):
    """
    Defines an operator that takes in multiple items.
    Cannot be instantiated directly.
    """
    def __init__(self, operator, *items):
        super().__init__(operator)
        item_list = []

        for item in items:
            self._check_type_err(item)
            if type(item) is self.__class__:
                for sub_item in item._items:
                    item_list.append(sub_item)
            else:
                item_list.append(item)
        self._items = item_list

    def __repr__(self):
        result = ''
        for item in self._items:
            result += (repr(item) if not isinstance(item, str) else item) + self._operator
        result = result[:-1]
        return '{' + '{} {}'.format(self.__class__.__name__, result) + '}'

class Collation(BinaryOperator):
    """
    Defines a collation operator which takes in two characters and returns all characters
    in between them.
    For example [a-z] returns all lowercase letters of the alphabet.

    Be careful with collation: [A-z] will NOT  return a valid response.
    For all alphabet characters use [A-Z]|[a-z] (union of two collations).
    For more info see Alternation.
    """
    _item_types = {str}
    def __init__(self, first_character: str, ending_character: str):
        super().__init__(first_character, ending_character, '-')

    @property
    def all_characters(self)->list:
        """
        Returns a list of all characters included in the collation.

        :return list: all characters included
        """
        return [chr(i) for i in range(ord(self._first), ord(self._last) + 1)]

    def execute(self)->nfa.EpsilonNFA:
        result = ''
        inputs = ''
        for char in self.all_characters:
            result += 'c0,{}->c1;'.format(char)
            inputs += char + ','
        result = result[:-1]
        inputs = inputs[:-1]

        enfa = nfa.EpsilonNFA.factory(
            """c0,c1;{};c1;c0;{}""".format(inputs, result),
        generator.StandardFormatSemicolonGenerator())
        return enfa

class Alternation(GeneralOperator):
    """
    Defines a union of two items. Those items can be a string or already defined operators.
    For example it's possible to do a union of a character 'a' and a collation of [b-z].

    Example:
        'a|b' = 'a', 'b'
    """
    _item_types = {str, Operator}
    def __init__(self, *items):
        super().__init__('|', *items)

    def execute(self)->nfa.EpsilonNFA:
        enfas = []
        for item in self._items:
            if isinstance(item, str):
                enfas.append(nfa.EpsilonNFA.factory(
                    """u0, u1;{0};u1;u0;u0,{0}->u1""".format(item),
                generator.StandardFormatSemicolonGenerator()))
            elif isinstance(item, Operator):
                enfas.append(item.execute())

        result = enfas[0]
        for i in range(1, len(enfas)):
            result = result + enfas[i]
        return result

class Concatenation(GeneralOperator):
    """
    Defines a concatenation of two items. Those items can be a string or already defined operators.
    For example it's possible to do a union of a character 'a' and a collation of [b-z].

    Example:
        'ab' - 'ab'
        'a(b|c)' - 'ab', 'ac'
    """
    _item_types = {str, Operator}

    def __init__(self, *items):
        super().__init__('', *items)

    def execute(self)->nfa.EpsilonNFA:
        enfas = []
        for item in self._items:
            if isinstance(item, str):
                enfas.append(nfa.EpsilonNFA.factory(
                    """c0, c1;{0};c1;c0;c0,{0}->c1""".format(item),
                    generator.StandardFormatSemicolonGenerator()))
            elif isinstance(item, Operator):
                enfas.append(item.execute())

        result = enfas[0]
        for i in range(1, len(enfas)):
            result = result * enfas[i]
        return result

    def __repr__(self):
        result = ''
        for item in self._items:
            result += str(item) if not isinstance(item, str) else item
        # result = result[:-1]
        return '{' + '{} {}'.format(self.__class__.__name__, result) + '}'


class KleeneStar(UnaryOperator):
    """
    Defines a Kleene star operator, meaning zero or more repetitions.
    It can take in a character or an already defined operator.
    For example (a|b|cd)* is a valid input because (a|b|cd) wil be a single operator and the whole
    response is going to be an operator.

    Example:
        'a*' = '', 'a', 'aa', 'aaa', ...
    """
    _item_types = {str, Operator}

    def __init__(self, item):
        super().__init__(item, '*')

    def execute(self)->nfa.EpsilonNFA:
        if isinstance(self._item, str):
            item_enfa = nfa.EpsilonNFA.factory(
                """ks0,ks1;{0};ks1;ks0;ks0,{0}->ks1""".format(self._item),
            generator.StandardFormatSemicolonGenerator())
        elif isinstance(self._item, Operator):
            item_enfa = self._item.execute()
        return item_enfa.kleene_operator()

class KleenePlus(UnaryOperator):
    """
    Defines a Kleene plus operator, meaning one or more repetitions.
    It can take in a character or an already defined operator.
    For example (a|b|cd)* is a valid input because (a|b|cd) wil be a single operator and the whole
    response is going to be an operator.

    Example:
        'a+' = 'a', 'aa', 'aaa', 'aaaa', ...
    """
    _item_types = {str, Operator}

    def __init__(self, item):
        super().__init__(item, '+')

    def execute(self)->nfa.EpsilonNFA:
        if isinstance(self._item, str):
            enfa = nfa.EpsilonNFA.factory(
                """kp0,kp1;{0};kp1;kp0;kp0,{0}->kp1""".format(self._item),
            generator.StandardFormatSemicolonGenerator())
        elif isinstance(self._item, Operator):
            enfa = self._item.execute()
        # else is not needed because OperatorInputTypeError would already have been raised
        # if item is not a string or an Operator.
        return enfa.deepcopy() * enfa.kleene_operator()

class QuestionMark(UnaryOperator):
    """
    Defines a question mark (?) operator, meaning zero or one repetitions.
    I couldn't find its' official name.
    It can take in a character or an already defined operator.
    For example (a|b|cd)? is a valid input because (a|b|cd) wil be a single operator and the whole
    response is going to be an operator.

    Example:
        'a?' = '', 'a'
    """
    _item_types = {str, Operator}

    def __init__(self, item):
        super().__init__(item, '?')

    def execute(self)->nfa.EpsilonNFA:
        if isinstance(self._item, str):
            item_enfa = nfa.EpsilonNFA.factory(
                """qm0,qm1;{0};qm1;qm0;qm0,{0}->qm1;qm0,$->qm1""".format(self._item),
            generator.StandardFormatSemicolonGenerator())
        elif isinstance(self._item, Operator):
            start_enfa = nfa.EpsilonNFA.factory(
                """qm;;qm;qm;""",
            generator.StandardFormatSemicolonGenerator())
            end_enfa = start_enfa.deepcopy()
            item_enfa = start_enfa*end_enfa + self._item.execute()
        #todo: check if this is correct.
        return item_enfa
