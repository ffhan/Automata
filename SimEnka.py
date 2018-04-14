import sys
from NFA import E_NFA, NFA


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

def sets(func):
    def wrapper(*args):
        return set(func(*args))
    return wrapper


def splitter(string, char):
    return string.split(char)

@sets
def set_splitter(string,char):
    return splitter(string, char)

def comma(*args):
    result = ''
    for arg in args:
        if arg != '':
            result += arg + ';'
    return result[:-1]

def printer(*args):
    for arg in args:
        print(arg)

def parse(string):
    lines = splitter(string, '\n')

    entries = splitter(lines[0], '|')
    states = set_splitter(lines[1], ',')
    inputs = set_splitter(lines[2], ',')
    final = set_splitter(lines[3], ',')
    start = lines[4]
    functions = comma(*lines[5:])

    #printer(entries, states, inputs, final, start, functions)

    nfa = E_NFA(states, inputs, functions, start, final)

    records = []

    for entry in entries:
        records.append(nfa.record(*entry.split(',')).copy())
        nfa.reset()
    # print(entries)
    # print(len(functions.replace(';', ';\n')))
    return records

def save(records):

    result = ''

    for record in records:
        r = list(record)
        for s in r:
            states = sorted(list(s))
            if len(states) == 0:
                result += '#' + '|'
                continue
            for state in states:
                result += state.name + ','
            result = result[:-1]
            result += '|'
        result = result[:-1]
        result += '\n'

    print(result)

#
# has_0_then_1 = DFA({'q0', 'q1', 'q2'}, {0,1},
#           '''
#           q0,0->q2;
#           q0,1->q0;
#           q2,1->q1;
#           q2,0->q2;
#           q1,0->q1;
#           q1,1->q1
#           ''',
#           'q0', {'q1'})

# print(has_0_then_1.enter('101'))

# equal01 = DFA({'botheven',
#                '1even0odd',
#                '1odd0even',
#                'bothodd'},
#               {'0', '1'},
#               '''
#               botheven,0->1even0odd;
#               botheven,1->1odd0even;
#               1even0odd,0->botheven;
#               1even0odd,1->bothodd;
#               1odd0even,0->bothodd;
#               1odd0even,1->botheven;
#               bothodd,0->1odd0even;
#               bothodd,1->1even0odd
#               ''', 'botheven', {'botheven'}, str)

# print(equal01.enter('10110010'))

# example of generating the upper function instruction string (FIS):

# print(create_function_string(newline=True,
#                              q0={0:'q1',1:'q2'},
#                              q1={0:'q0',1:'q3'},
#                              q2={0:'q3',1:'q0'},
#                              q3={0:'q2',1:'q1'}))

# nfa = NFA(
#     {'q0', 'q1', 'q2'},
#     {0,1},
#     '''
#     q0,0->q0,q1;
#     q0,1->q0;
#     q1,1->q2
#     ''',
#     'q0',
#     {'q2'}, str
# )
#
# print(nfa)

# print(nfa.output('110101'))
# print(nfa.output('0101'))
#
# enfa = E_NFA({'s', '0', '01'},
#              {0, 1},
#              '''
#              s,$->s;
#              s,0->0;
#              0,0->0;
#              0,1->01;
#              01,$->01
#              ''',
#              's',
#              {'00'})

# print(enfa.record('0','1','0','1'))

# example = '''a,pnp,a|pnp,lab2|pnp,a|pnp,lab2,utr,utr
# p5,s3,s4,st6,stanje1,stanje2
# a,lab2,pnp,utr
# p5
# stanje1
# s3,a->stanje2
# s3,lab2->p5,s4
# s4,$->st6
# s4,utr->p5,s3
# stanje1,a->stanje2
# stanje1,pnp->s3
# stanje2,$->st6
# stanje2,a->#
# '''
#
# save(parse(example))

inp = sys.stdin.readlines()

text = ''
for i in inp:
    text += i
# print(text)
save(parse(text))