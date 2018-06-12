"""
Defines an endpoint for user input
"""
import form.readers as rs
import form.preformat as pf
import form.compositors as cm

turing = pf.get_turing(rs.Reader.read_input())
print(cm.StandardTuringMachineCompositor(turing).composite_output())