from labos1.DFA import DFA
from labos1.NFA import NFA

def create_function_string(newline = False, **rules):
    '''
    Creates function string from parameters. This enables the programmer to use both string-type functional input or direct programming.

    Example:
        create_function_string(q0={0:'q0', 1:'q1'}, q1={0:'q0', 1:'q1'})
    :param bool newline: defines if FIS is going to have each function defined in its' own row
    :param dict rules: dictionary with keys (str) being inputs and values (str) being state names
    :return: Function instruction string
    '''
    result = ''

    for start, value_and_end in rules.items():
        for value, end in value_and_end.items():
            result += start + ',' + str(value) + '->' + end + ';' + ('\n' if newline else '')
    return result

has_0_then_1 = DFA({'q0', 'q1', 'q2'}, {0,1},
          '''
          q0,0->q2;
          q0,1->q0;
          q2,1->q1;
          q2,0->q2;
          q1,0->q1;
          q1,1->q1
          ''',
          'q0', {'q1'})

# has_0_then_1.enter('101')

equal01 = DFA({'botheven',
               '1even0odd',
               '1odd0even',
               'bothodd'},
              {'0', '1'},
              '''
              botheven,0->1even0odd;
              botheven,1->1odd0even;
              1even0odd,0->botheven;
              1even0odd,1->bothodd;
              1odd0even,0->bothodd;
              1odd0even,1->botheven;
              bothodd,0->1odd0even;
              bothodd,1->1even0odd
              ''', 'botheven', {'botheven'}, str)

#print(equal01.enter('10110010'))

# example of generating the upper function instruction string (FIS):

# print(create_function_string(newline=True,
#                              q0={0:'q1',1:'q2'},
#                              q1={0:'q0',1:'q3'},
#                              q2={0:'q3',1:'q0'},
#                              q3={0:'q2',1:'q1'}))

nfa = NFA(
    {'q0','q1', 'q2'}, {0, 1},
    '''
    q0,0->q0;
    q0,1->q1;
    q1,0->q0;
    q1,1->q1;
    q1,1->q2
    ''', 'q0', {'q2'})

print(nfa)

print(nfa.enter('11'))