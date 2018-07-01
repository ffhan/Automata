"""
Defines a Compositor interface (abstract class) and all
concrete implementations.

In the other words, it defines all input formats.
"""
import abc

class Compositor(abc.ABC):

    """
    An abstract Compositor. Defines an interface that all following Compositors should follow.
    """

    def __init__(self, automaton):
        """
        Takes in a valid FA object.

        :param FA automaton: A valid automaton
        """

        self.automaton = automaton

    @abc.abstractmethod
    def composite_output(self) -> str:
        """
        Returns outputs of an automaton.

        :return str: outputs of an automaton.
        """
        pass

    @abc.abstractmethod
    def composite_automaton(self) -> str:
        """
        Returns a string automaton representation.

        :return str: automaton representation
        """
        pass

class StandardCommandTestCompositor(Compositor):

    """
    Standard form Compositor.
    """

    def composite_output(self):
        result = ''


        for entry in self.automaton.records:
            for group in entry:
                group = group.unpack
                group = group[0]
                for value in sorted(list(group)):
                    # value, accepted = value.unpack
                    result += repr(value) + ','
                result = result[:-1] + '|'
                if not group: # same as len(group == 0)
                    result += '#|'
                    continue
            result = result[:-1] + '\n'
        return result[:-1].strip()

    def composite_automaton(self):
        def general_it(iterable, symbol=','):
            """
            Puts a symbol between every item from iterable.
            :param iterable: a collection of items
            :param str symbol: symbol to be added
            :return str: result string
            """
            res = ''
            for single_item in iterable:
                res += '{}{}'.format(single_item, symbol)
            return res[:-1] + '\n'

        def coma_it(iterable):
            """
            Adds a comma between each item in an iterable.
            See general_it for further details.
            :param iterable: a collection of items
            :return str: result string
            """
            return general_it(iterable)
        states = list(sorted(self.automaton.states.values()))
        inputs = list(sorted(self.automaton.inputs))
        final = list(sorted(self.automaton.accepted_states))
        start_state = self.automaton.start_state
        functions = self.automaton.functions
        # print(states,inputs,final,start_state,functions)

        result = ''

        result += coma_it(states)
        result += coma_it(inputs)
        result += coma_it(final)
        result += str(start_state)
        result += '\n' + functions

        return result.strip().strip('\n').strip()

class StandardCompositor(Compositor):
    """
    Standard form Compositor.
    """
    def composite_output(self):
        result = ''


        for entry in self.automaton.records:
            for group in entry:
                group = group.unpack
                group = group[0]
                for value in sorted(list(group)):
                    # value, accepted = value.unpack
                    result += repr(value) + ','
                result = result[:-1] + '|'
                if not group: # same as len(group == 0)
                    result += '#|'
                    continue
            result = result[:-1] + '\n'
        return result[:-1].strip()

    def composite_automaton(self):
        def general_it(iterable, symbol=',', add_before: bool = False):
            """
            Puts a symbol between every item from iterable.

            :param iterable: a collection of items
            :param str symbol: symbol to be added
            :param bool add_before: add symbol before the first item
            :return str: result string
            """
            res = ''
            before = symbol if add_before else ''
            for single_item in iterable:
                res += '{}{}'.format(single_item, symbol)
            return before + res[:-1] + '\n'

        def coma_it(iterable):
            """
            Adds a comma between each item in an iterable.
            See general_it for further details.

            :param iterable: a collection of items
            :return str: result string
            """
            return general_it(iterable)
        states = list(map(lambda t : general_it(repr(t), '\\', True)[:-1], sorted(self.automaton.states.values())))
        inputs = list(map(lambda t : general_it(t, '\\', True)[:-1], sorted(self.automaton.inputs)))
        final = list(map(lambda t : general_it(repr(t), '\\', True)[:-1], sorted(self.automaton.accepted_states)))
        start_state = general_it(repr(self.automaton.start_state), '\\', True)[:-1]
        # functions = self.automaton.functions
        functions = ''
        for state in sorted(self.automaton.states.values()):
            for single_input in sorted(self.automaton.inputs):
                for end in sorted(state.forward(single_input)):
                    # print(state, single_input, end)
                    assert end in self.automaton.states
                    functions += '{},{}->{}\n'.format(general_it(repr(state), '\\', True)[:-1],
                                                    general_it(single_input, '\\', True)[:-1],
                                                    general_it(repr(end), '\\', True)[:-1])
        # print(states,inputs,final,start_state,functions)

        result = ''

        result += coma_it(states)
        result += coma_it(inputs)
        result += coma_it(final)
        result += str(start_state)
        result += '\n' + functions

        return result.strip().strip('\n').strip()

class StandardPushDownCompositor(Compositor): #could inherit Standard compositor but doesn't matter.

    """
    Standard form Compositor for Push down automata.
    """

    def composite_output(self):

        def handle_stack(stck):
            """
            Puts a comma between each stack item.

            :param Stack stck: a stack
            :return str: result string
            """
            res = ''
            if stck.size > 0:
                res = repr(stck)
                res = res[1:-1].replace(',', '').replace("'", '')
            else:
                res = self.automaton.empty_symbol
            return res[::-1]

        result = ''
        # print(self.automaton.records)
        for record in self.automaton.records:
            for entry in record:
                # print(entry, *entry.unpack)
                state, accepted, stack = entry.unpack
                #value is an InputPack
                result += repr(state) + '#'
                if state != self.automaton.failed_state:
                    result += handle_stack(stack) + ','
                result = result[:-1] + '|'
            result += ('1' if accepted else '0') + '|'
            result = result[:-1] + '\n'

        return result[:-1].strip()

    def composite_automaton(self):
        raise NotImplementedError

class StandardTuringMachineCompositor(Compositor):
    def composite_automaton(self):
        raise NotImplementedError
    def composite_output(self):
        result = repr(self.automaton.current) + '|' + repr(self.automaton.tape._index) + '|'
        for item in self.automaton.tape._container:
            result += (item if isinstance(item, str) else repr(item))
        result += '|' + ('1' if self.automaton.accepted else '0')
        return result
