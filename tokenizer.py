import re
import tkinter as tk
from pycparser import c_parser

TOKEN_TYPES = {
    "KEYWORD": r"\b(if|else|while|for|return|do|switch|case|default|break|continue|int|float|double|char|void|struct|typedef|enum|union)\b",
    "INLINE_COMMENT": r"\/\/.*$",
    "IDENTIFIER": r"[a-zA-Z_][a-zA-Z0-9_]*",
    "STRING_LITERAL": r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
    "PUNCTUATION": r"[\(\)\[\]\{\};,]",
    "SYMBOL": r"[^\s\w]+",
    "NUMBER": r"\d+(\.\d*)?",
    "LITERAL": r"true|false",
    "COMMENT": r"\/\/.*|\/\*[\s\S]*?\*\/",  
    "WHITESPACE": r"\s+",
    "MAIN_FUNCTION": r"int\s+main\s*\(",
    "OPERATOR": r"\+|\-|\*|\/|==|!=|>|<|>=|<=|&&|\|\||%|!",
    "ASSIGNMENT": r"=|\+=|-=|\*=|\/=",
    "INCREMENT": r"\+\+",
    "DECREMENT": r"\-\-",
}


def tokenize(source_code):
    tokens = []
    lines = source_code.split("\n")
    for line in lines:
        tokens.extend(tokenize_line(line))
    return tokens


def tokenize_line(line):
    tokens = []
    while line:
        match = None
        for token_type, pattern in TOKEN_TYPES.items():
            regex = re.compile(pattern)
            match = regex.match(line)
            if match:
                value = match.group(0)
                if token_type != "WHITESPACE":
                    tokens.append((token_type, value))
                line = line[len(value) :]
                break
        if not match:
            raise ValueError(f"Invalid token: {line}")
    return tokens


def format_code(tokens):
    indent_level = 0
    formatted_code = ""

    for i, (token_type, value) in enumerate(tokens):
        if value == "{" and tokens[i + 1][0] != "STRING_LITERAL":
            indent_level += 1
            if tokens[i + 1][0] == "NUMBER":
                formatted_code += value
                continue
            formatted_code += value + "\n" + "\t" * indent_level
        elif value == "(" and (
            tokens[i + 1][0] == "IDENTFIER" or tokens[i + 1][0] == "STRING_LITERAL"
        ):
            formatted_code += value
        elif value == "=" or value == "==" or value == "/":
            formatted_code += " " + value + " "
        elif token_type == "INLINE_COMMENT":
            formatted_code += "\n"
        elif token_type == "OPERATOR":
            formatted_code += " " + value + " "
        elif value == "}":
            indent_level -= 1
            if i < len(tokens) - 1:
                if tokens[i + 1][0] == "KEYWORD" and tokens[i + 1][1] != "else":
                    formatted_code += "\n" + "\t" * indent_level + value + "\n"
                    continue
            if tokens[i - 1][0] == "NUMBER":
                formatted_code += value
                continue
            formatted_code += "\n" + "\t" * indent_level + value
        elif value == ";":
            if (
                tokens[i + 1][0] == "STRING_LITERAL"
                or tokens[i + 1][0] == "PUNCTUATION"
                or tokens[i + 1][0] == "IDENTIFIER"
            ) and tokens[i + 1][1] != "printf":
                formatted_code += value
                continue
            formatted_code += value + "\n" + "\t" * indent_level
        elif value == "[" or value == "]":
            formatted_code += value
        elif value in ["if", "else", "for", "while", "do"]:
            formatted_code += " " + value + " "
        elif token_type == "PUNCTUATION" and tokens[i + 1][0] == "PUNCTUATION":
            formatted_code += value
        elif token_type in ["OPERATOR", "PUNCTUATION"]:
            formatted_code += " " + value + " "
        elif token_type == "IDENTIFIER" and (
            tokens[i - 1][1] == "KEYWORD" or tokens[i - 1][1] == "*"
        ):
            formatted_code += value + " "  # Add space after identifiers
        elif token_type == "IDENTIFIER":
            formatted_code += value  # Add space after identifiers
        elif token_type == "KEYWORD":
            formatted_code += value + " "
        elif value == ">" and (
            tokens[i + 1][0] == "KEYWORD" or tokens[i + 1][1] == "#"
        ):
            formatted_code += value + "\n"
        else:
            formatted_code += value

    return formatted_code.strip()


def format_source_code(event=None):
    source_code = input_text.get("1.0", tk.END)
    tokens = tokenize(source_code)
    formatted_code = format_code(tokens)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, formatted_code)

    # Parsing and displaying AST
    ast = parse_formatted_code(formatted_code)
    ast_text.delete("1.0", tk.END)
    ast_text.insert(tk.END, str(ast))

def parse_formatted_code(code):
    # Parse the formatted code using pycparser
    parser = c_parser.CParser()
    ast = parser.parse(code)
    return ast

def clear_blocks(event=None):
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)
    ast_text.delete("1.0", tk.END)


root = tk.Tk()
root.title("C Code Formatter")

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)


input_frame = tk.Frame(main_frame)
input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
input_label = tk.Label(input_frame, text="Input Code:")
input_label.pack()

input_scroll = tk.Scrollbar(input_frame, orient=tk.HORIZONTAL)
input_text = tk.Text(input_frame, height=20, width=50, wrap="none", xscrollcommand=input_scroll.set)
input_scroll.config(command=input_text.xview)
input_scroll.pack(side=tk.BOTTOM, fill=tk.X)
input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


output_frame = tk.Frame(main_frame)
output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
output_label = tk.Label(output_frame, text="Formatted Code:")
output_label.pack()

output_scroll = tk.Scrollbar(output_frame, orient=tk.HORIZONTAL)
output_text = tk.Text(output_frame, height=20, width=50, wrap="none", xscrollcommand=output_scroll.set)
output_scroll.config(command=output_text.xview)
output_scroll.pack(side=tk.BOTTOM, fill=tk.X)
output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


ast_frame = tk.Frame(root)
ast_frame.pack(fill=tk.BOTH, expand=True)

ast_label = tk.Label(ast_frame, text="Abstract Syntax Tree (AST):")
ast_label.pack()

ast_scroll = tk.Scrollbar(ast_frame, orient=tk.HORIZONTAL)
ast_text = tk.Text(ast_frame, height=10, wrap="none", xscrollcommand=ast_scroll.set)
ast_scroll.config(command=ast_text.xview)
ast_scroll.pack(side=tk.BOTTOM, fill=tk.X)
ast_text.pack(fill=tk.BOTH, expand=True)


button_frame = tk.Frame(root)
button_frame.pack(pady=5)


format_button = tk.Button(root, text="Format", command=format_source_code)
format_button.pack(padx=5, pady=5)

clear_button = tk.Button(root, text="Clear", command=clear_blocks)
clear_button.pack(padx=5, pady=5)

# Bind keyboard shortcuts
root.bind("<Control-f>", format_source_code)
root.bind("<Control-c>", clear_blocks)

root.mainloop()
