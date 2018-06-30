"""
Defines all operator abstractions and their respective default operators.
"""
import abc
import automata.nfa as nfa
import automata.dfa as dfa
import form.generators as generator
import misc.errors as err
import misc.helper as helper
import automata.cast_api as api

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
    def _assemble(self)->nfa.EpsilonNFA:
        """
        Assembles the operator into an Epsilon NFA

        :return:
        """
        pass

    def execute(self)->dfa.DFA:
        """
        Executes the Operator: returns a DFA that describes the operation results.

        :return DFA: minimised DFA
        """
        # import misc.visual as vis
        # vis.save_graph(self._assemble())
        dfa_output = api.epsilon_nfa_to_dfa(self._assemble())
        dfa_output.minimize()
        return dfa_output

    @property
    @abc.abstractmethod
    def min_length(self)->int:
        """
        Property that returns a minimum length for a defined operator.

        For example Kleene star has minimum length 0, while Single 'ab' has length 2.

        :return int: minimum length of an operator
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

    def _assemble(self)->nfa.EpsilonNFA:
        if isinstance(self._item, str):
            enfa = nfa.EpsilonNFA.factory(
                """s0,s1
{0}
s1
s0
s0,{0}->s1""".format(*helper.escape_string(self._item)),
            generator.StandardFormatGenerator())
        elif isinstance(self._item, Operator):
            enfa = self._item._assemble()
        return enfa
    @property
    def min_length(self):
        if isinstance(self._item, str):
            return len(self._item)
        elif isinstance(self._item, Operator):
            return self._item.min_length
        raise TypeError('Item type is not accepted by {}'.format(self.__class__.__name__))

class BinaryOperator(Operator):
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

    def _assemble(self)->nfa.EpsilonNFA:
        result = ''
        inputs = ''
        for char in self.all_characters:
            result += 'c0,{}->c1\n'.format(*helper.escape_string(char))
            inputs += char + ','
        result = result[:-1]
        inputs = inputs[:-1]

        enfa = nfa.EpsilonNFA.factory(
            """c0,c1
{}
c1
c0
{}""".format(inputs, result),
        generator.StandardFormatGenerator())
        return enfa

    @property
    def min_length(self):
        return 1

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

    def _assemble(self)->nfa.EpsilonNFA:
        enfas = []
        for item in self._items:
            if isinstance(item, str):
                enfas.append(nfa.EpsilonNFA.factory(
                    """u0,u1
{0}
u1
u0
u0,{0}->u1""".format(*helper.escape_string(item)),
                generator.StandardFormatGenerator()))
            elif isinstance(item, Operator):
                enfas.append(item._assemble())

        result = enfas[0]
        for i in range(1, len(enfas)):
            result = result + enfas[i]
        return result

    @property
    def min_length(self):
        lengths = []
        for item in self._items:
            if isinstance(item, str):
                lengths.append(len(item))
            elif isinstance(item, Operator):
                lengths.append(item.min_length)
            else:
                raise TypeError
        return min(lengths)

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

    def _assemble(self)->nfa.EpsilonNFA:
        enfas = []
        for item in self._items:
            if isinstance(item, str):
                enfas.append(nfa.EpsilonNFA.factory(
                    """c0,c1
{0}
c1
c0
c0,{0}->c1""".format(*helper.escape_string(item)),
                    generator.StandardFormatGenerator()))
            elif isinstance(item, Operator):
                enfas.append(item._assemble())

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

    @property
    def min_length(self):
        length = 0
        for item in self._items:
            if isinstance(item, str):
                length += len(item)
            elif isinstance(item, Operator):
                length += item.min_length
            else:
                raise TypeError
        return length

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

    def _assemble(self)->nfa.EpsilonNFA:
        if isinstance(self._item, str):
            item_enfa = nfa.EpsilonNFA.factory(
                """ks0,ks1
{0}
ks1
ks0
ks0,{0}->ks1""".format(*helper.escape_string(self._item)),
            generator.StandardFormatGenerator())
        elif isinstance(self._item, Operator):
            item_enfa = self._item._assemble()
        return item_enfa.kleene_operator()

    @property
    def min_length(self):
        return 0

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

    def _assemble(self)->nfa.EpsilonNFA:
        if isinstance(self._item, str):
            # todo: don't call it through this.
            enfa = nfa.EpsilonNFA.factory(
                """kp0,kp1
{0}
kp1
kp0
kp0,{0}->kp1""".format(*helper.escape_string(self._item)),
            generator.StandardFormatGenerator())
        elif isinstance(self._item, Operator):
            enfa = self._item._assemble()
        # else is not needed because OperatorInputTypeError would already have been raised
        # if item is not a string or an Operator.
        return enfa.deepcopy() * enfa.kleene_operator()

    @property
    def min_length(self):
        if isinstance(self._item, str):
            return len(self._item)
        elif isinstance(self._item, Operator):
            return self._item.min_length
        raise TypeError

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

    def _assemble(self)->nfa.EpsilonNFA:
        if isinstance(self._item, str):
            item_enfa = nfa.EpsilonNFA.factory(
                """qm0,qm1
{0}
qm1
qm0
qm0,{0}->qm1
qm0,$->qm1""".format(*helper.escape_string(self._item)),
            generator.StandardFormatGenerator())
        elif isinstance(self._item, Operator):
            start_enfa = nfa.EpsilonNFA.factory(
                """qm\n\nqm\nqm\n""",
            generator.StandardFormatGenerator())
            end_enfa = start_enfa.deepcopy()
            item_enfa = start_enfa*end_enfa + self._item._assemble()
        return item_enfa

    @property
    def min_length(self):
        return 0
