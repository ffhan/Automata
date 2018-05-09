import abc
import automata

class Compositor(abc.ABC):

    def __init__(self, automaton):
        """
        Takes in a valid FA object.

        :param FA automaton: A valid automaton
        """

        self.automaton = automaton

    @abc.abstractmethod
    def composite_output(self):
        pass

    @abc.abstractmethod
    def composite_automaton(self):
        pass

class StandardCompositor(Compositor):

    def composite_output(self):
        result = ''

        for entry in self.automaton.records:
            for group in entry:
                for value in sorted(list(group)):

                    result += repr(value) + ','
                result = result[:-1] + '|'
                if len(group) == 0:
                    result += '#|'
                    continue
            result = result[:-1] + '\n'
        return result[:-1].strip()

    def composite_automaton(self):
        def general_it(iterable, symbol=','):
            res = ''
            for iter in iterable:
                res += '{}{}'.format(iter, symbol)
            return res[:-1] + '\n'

        def coma_it(iterable):
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

class StandardPushDownCompositor(Compositor): #could inherit Standard compositor but doesn't matter.

    def composite_output(self):

        def handle_stack(stack):
            res = ''
            for val in stack:
                res += val
            return res[::-1]

        result = ''
        print(self.automaton.records)
        for entry in self.automaton.records:
            for value in entry:
                #value is an InputPack
                state, stack = value.pack
                result += repr(state) + '#'
                if state != self.automaton.failed_symbol:
                    result += handle_stack(stack) + ','
                result = result[:-1] + '|'
                if len(entry) == 0:
                    result += '#|'
                    continue
            result = result[:-1] + '\n' #todo: FA accepted (not accepted_states) property.
        return result[:-1].strip()

    def composite_automaton(self):
        raise NotImplementedError
