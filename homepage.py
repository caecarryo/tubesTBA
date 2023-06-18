import streamlit as st
from string import ascii_letters, digits
import re

SPACE, TAB, NEWLINE = (' ', '\t', '\n')

class LexicalAnalyzer:
    def __init__(self):
        self.transitions = {}
        self.accepted_states = set()
        self.init_state = None
        self.current_state = None
        self.current_token = ''

    def add_init_state(self, state):
        self.init_state = state
    
    def add_transition(self, state, read, target_state):
        for char in read:
            self.transitions[(state, char)] = target_state

    def add_accepted_state(self, state):
        self.accepted_states.add(state)
    
    def analyze(self, input_str, verbose=False):
        if not input_str.endswith('#'):
            input_str = input_str + '#'

        cursor_pos = 0
        self.current_state = self.init_state
        self.current_token = ''

        while cursor_pos < len(input_str):
            is_accepted = self.current_state in self.accepted_states

            if verbose:
                print({
                    'current_state': self.current_state,
                    'current_token': self.current_token,
                    'input': input_str[cursor_pos],
                    'is_accepted': is_accepted
                })

            if is_accepted and input_str[cursor_pos] in [NEWLINE, TAB, SPACE, '#'] and self.current_token:
                st.success(f'Current Token {self.current_token}')
                self.current_token = ''

            if input_str[cursor_pos] not in [NEWLINE, TAB, SPACE]:
                self.current_token += input_str[cursor_pos]

            self.current_state = self.transitions.get((self.current_state, input_str[cursor_pos]))
            
            if not self.current_state:
                st.error(f'Invalid: {input_str[cursor_pos]}')
                break

            cursor_pos += 1
            
        if self.current_state == 'accept':
            st.subheader("Your code is valid!")
            st.code(f'{input_str[:-1]}', language = 'python')


def main():
    lexical = LexicalAnalyzer()
    
    # add init state
    lexical.add_init_state('q0')
    
    # handle newline at first line
    lexical.add_transition('q0', NEWLINE, 'q0')
    
    # handle for 'while' statement
    lexical.add_transition('q0', 'w', 'q1')
    lexical.add_transition('q1', 'h', 'q2')
    lexical.add_transition('q2', 'i', 'q3')
    lexical.add_transition('q3', 'l', 'q4')
    lexical.add_transition('q4', 'e', 'q5')

    # space or tab after 'while' statement
    lexical.add_transition('q5', f'{SPACE}{TAB}', 'q5')

    lexical.add_accepted_state('q5')

    # Rule named variable python:
    #     1. Variable name must start with a letter or the underscore character
    
    # handle variable on while 'condition'
    lexical.add_transition('q5', ascii_letters + '_', 'a1')
    lexical.add_transition('a1', ascii_letters + digits + '_', 'a1')
    # handle space or tab
    lexical.add_transition('a1', f'{SPACE}{TAB}', 'a1')

    # handle comparison operator '<, >, =, !'
    lexical.add_transition('a1', '<>=!', 'a2')
    # handle space or tab
    lexical.add_transition('a2', f'{SPACE}{TAB}', 'a2')

    # handle comparison operator '<=, >=, ==, !=', add '=' at after '<, >, =, !'
    lexical.add_transition('a2', '=', 'a3')
    # handle space or tab
    lexical.add_transition('a3', f'{SPACE}{TAB}', 'a3')

    # handle variable on while 'condition'
    lexical.add_transition('a2', ascii_letters + '_', 'a4')
    lexical.add_transition('a3', ascii_letters + '_', 'a4')
    lexical.add_transition('a4', ascii_letters + digits + '_', 'a4')

    # handle space or tab after variable
    lexical.add_transition('a4', f'{SPACE}{TAB}', 'a5')
    lexical.add_transition('a5', f'{SPACE}{TAB}', 'a5')

    # accept state
    lexical.add_accepted_state('a5')

    # handle ':' after statement condition
    lexical.add_transition('a4', ':', 'b0')
    lexical.add_transition('a5', ':', 'b0')

    # handle space or tab ':'
    lexical.add_transition('b0', f'{SPACE}{TAB}', 'b0')

    # accept state
    lexical.add_accepted_state('b0')

    # newline after statement
    lexical.add_transition('b0', NEWLINE, 'b1')
    
    # handle newline without action
    lexical.add_transition('b1', NEWLINE, 'b1')
    
    # start 'action' statement
    lexical.add_transition('b1', f'{SPACE}{TAB}', 'b1')
    
    # 
    lexical.add_transition('b1', '#', 'accept')

    # handle variable on while 'condition'
    lexical.add_transition('b1', ascii_letters + '_', 'b2')
    lexical.add_transition('b2', ascii_letters + digits + '_', 'b2')

    # handle space or tab after variable
    lexical.add_transition('b2', f'{SPACE}{TAB}', 'b3')

    # assignment operator '='
    lexical.add_transition('b3', '=', 'b4')

    # handle space or tab after assignment operator
    lexical.add_transition('b4', f'{SPACE}{TAB}', 'b4')

    # handle variable after assignment operator
    lexical.add_transition('b4', ascii_letters + '_', 'b5')
    lexical.add_transition('b5', ascii_letters + digits + '_', 'b5')

    # handle space or tab after variable
    lexical.add_transition('b5', f'{SPACE}{TAB}', 'b5')

    # handle arithmetics operator '+, -, *'
    lexical.add_transition('b5', '+-', 'b6')
    lexical.add_transition('b6', f'{SPACE}{TAB}', 'b6')

    # handle arithmetics operator '/, //'
    lexical.add_transition('b5', '/', 'c1')
    lexical.add_transition('c1', '/', 'b7')
    lexical.add_transition('b7', f'{SPACE}{TAB}', 'b7')

    # handle arithmetics operator '*, **'
    lexical.add_transition('b5', '*', 'd1')
    lexical.add_transition('d1', '*', 'b10')
    lexical.add_transition('b10', f'{SPACE}{TAB}', 'b10')

    # handle integer
    lexical.add_transition('b6', digits, 'b9')
    lexical.add_transition('b7', digits, 'b9')
    lexical.add_transition('b10', digits, 'b9')

    # loop integer
    lexical.add_transition('b9', digits, 'b9')

    # handle variable on while 'condition'
    lexical.add_transition('b6', ascii_letters + '_', 'b8')
    lexical.add_transition('b7', ascii_letters + '_', 'b8')
    lexical.add_transition('b10', ascii_letters + '_', 'b8')
    lexical.add_transition('b8', ascii_letters + digits + '_', 'b8')
    
    lexical.add_transition('b8', f'{SPACE}{TAB}{NEWLINE}', 'b8') 
    lexical.add_accepted_state('b8')
    
    lexical.add_transition('b8', NEWLINE, 'b1')
    lexical.add_transition('b8', '#', 'accept')

    lexical.add_transition('b9', f'{SPACE}{TAB}', 'b9')
    lexical.add_accepted_state('b9')
    
    lexical.add_transition('b9', NEWLINE, 'b1')
    lexical.add_transition('b9', '#', 'accept')


    st.title("Python - Repeat Until")
    st.subheader("Kelompok 05 - IF4509")


    input_str = st.text_area("Input Condition", height=200)

    if st.button("Submit"):
        st.subheader("Submit Result")
        lexical.analyze(input_str, verbose=True)


if __name__ == "__main__":
    main()