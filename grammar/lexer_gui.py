"""
Defines a gui that helps playing with lexers and regular expressions.
"""
import tkinter as tk
import grammar.lexers as lex
import grammar.regular_expressions as regex

class TextWithVar(tk.Text):
    '''A text widget that accepts a 'textvariable' option'''
    def __init__(self, parent, *args, **kwargs):
        try:
            self._textvariable = kwargs.pop("textvariable")
        except KeyError:
            self._textvariable = None

        tk.Text.__init__(self, parent, *args, **kwargs)

        # if the variable has data in it, use it to initialize
        # the widget
        if self._textvariable is not None:
            self.insert("1.0", self._textvariable.get())

        # this defines an internal proxy which generates a
        # virtual event whenever text is inserted or deleted
        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # if the contents changed, generate an event we can bind to
                if {([lindex $args 0] in {insert replace delete})} {
                    event generate $widget <<Change>> -when tail
                }
                # return the result from the real widget command
                return $result
            }
            ''')

        # this replaces the underlying widget with the proxy
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))

        # set up a binding to update the variable whenever
        # the widget changes
        self.bind("<<Change>>", self._on_widget_change)

        # set up a trace to update the text widget when the
        # variable changes
        if self._textvariable is not None:
            self._textvariable.trace("wu", self._on_var_change)

    def _on_var_change(self, *args):
        '''Change the text widget when the associated textvariable changes'''

        # only change the widget if something actually
        # changed, otherwise we'll get into an endless
        # loop
        text_current = self.get("1.0", "end-1c")
        var_current = self._textvariable.get()
        if text_current != var_current:
            self.delete("1.0", "end")
            self.insert("1.0", var_current)

    def _on_widget_change(self, event=None):
        '''Change the variable when the widget changes'''
        if self._textvariable is not None:
            self._textvariable.set(self.get("1.0", "end-1c"))

cols = {'class':'gold', 'define':'sandy brown', 'undefined':'red',
        'integer':'lawn green', 'float':'deep pink',
        'except':'dark khaki', 'try':'dark khaki',
        'in':'orange', 'variable':'peach puff',
        'while':'SlateGray1', 'for':'LightPink1',
        'with':'goldenrod2', 'return':'SpringGreen2',
        'assign':'cornsilk2', 'equal':'azure2',
        'inequal':'SteelBlue1', 'as':'sky blue'}

def lexer_gui():
    def process(*args):
        out = lexer.scan(text.get())
        output.set('')
        for item in out:
            tok_type = item.token_type.name if isinstance(item.token_type, regex.RegEx) else item.token_type
            if tok_type.lower() in cols:
                text_output.insert('end', tok_type + ' ', tok_type.lower())
            else:
                text_output.insert('end', tok_type + ' ')
            if item.token_value == '\n':
                text_output.insert('end', '\n')
            elif item.token_value == '\t':
                text_output.insert('end', '\t')
    lexer = lex.StandardLexer()

    root = tk.Tk()
    frame = tk.Listbox(root)

    text = tk.StringVar()
    text.trace_add('write', process)

    output = tk.StringVar()

    text_input = TextWithVar(frame, height=8, width=30, textvariable=text,
                             background='gray', foreground='white smoke')

    text_output = TextWithVar(frame, height=8, width=30, textvariable=output,
                              background='gray', foreground='white smoke')
    for name, color in cols.items():
        text_output.tag_config(name, foreground=color)

    frame.pack(fill=tk.BOTH)
    text_input.pack(fill=tk.BOTH)
    text_output.pack(fill=tk.BOTH)

    tk.mainloop()
if __name__ == '__main__':
    lexer_gui()
