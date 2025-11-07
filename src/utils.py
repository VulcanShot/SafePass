import os
import regex

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def change_working_dir():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    
def underline_text(txt):
    return "\033[4m" + str(txt) + "\033[0m"

def remove_control_chars(string):
    return regex.sub(r'\p{C}', '', string)

def write_binary(file: str, salt: bytes):
    with open(file, 'wb') as f:
        return f.write(salt)
    
def yes_no_question(prompt):
    yes = ['y', 'yes']
    choice = input(prompt).lower()
    return choice in yes