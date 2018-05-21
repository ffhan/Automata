"""
Defines all types that check if a string is a particular token
"""
# from form.lexers import StandardFormatLexer
# from automata.nfa import EpsilonNFA
#
# def check_integer(text):
#
#     lex = StandardFormatLexer()
#     fa = EpsilonNFA(
#         """s0,s1,s2
#         0,1,2,3,4,5,6,7,8,9
#         s1
#         s0
#         s0,0->s1
#         s0,1->s1
#         s0,2->s1
#         s0,3->s1
#         s0,4->s1
#         s0,5->s1
#         s0,6->s1
#         s0,7->s1
#         s0,8->s1
#         s0,9->s1
#         s0,$->s2
#         s2,$->s2
#         s1,$->s1""", lex)
#
#     for char in text:
#         fa.enter(char)
#
#     return fa.accepted
#
# print(check_integer('1001'))
# print(check_integer('12345'))
# print(check_integer('124e5'))