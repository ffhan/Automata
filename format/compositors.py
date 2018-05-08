import abc

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
        # print(self.automaton.records)
        # for records in self.automaton.records:
        #     for group in records:
        #         #print(group)
        #         string = str(sorted(list(group)))[1:-1]
        #         result += string + '|'
        #     result = result[:-1] + '\n'
        # return result.strip()
        for entry in self.automaton.records:
            line = ''
            for group in entry:
                for value in sorted(list(group)):

                    line += repr(value) + ','
                line = line[:-1] + '|'
                if len(group) == 0:
                    line += '#|'
                    continue
            result += line[:-1] + '\n'
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