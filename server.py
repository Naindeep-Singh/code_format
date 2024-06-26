from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import re
import google.generativeai as genai
from graphviz import Source
import os
from pycparser import c_parser

api_key = os.environ.get("API_KEY")
app = Flask(__name__)
CORS(app)

TOKEN_TYPES = {
    "KEYWORD": r"\b(cout|cin|if|else|while|for|return|do|switch|case|default|break|continue|int|float|double|char|void|struct|typedef|enum|union)\b",
    "INLINE_COMMENT": r"\/\/.*$",
    "STD": r"(std\:\:)",
    "IDENTIFIER": r"[a-zA-Z_][a-zA-Z0-9_]*",
    "STRING_LITERAL": r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'',
    "STREAM_INSERTION": r"<<",
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
    print(tokens)
    return tokens


def format_code(tokens):
    indent_level = 0
    formatted_code = ""

    try:
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
                formatted_code += value + "\n" + "\t" * indent_level
            elif token_type == "OPERATOR":
                formatted_code += " " + value + " "
            elif value == "}":
                indent_level -= 1
                if i < len(tokens) - 1:
                    if tokens[i + 1][0] == "KEYWORD" and tokens[i + 1][1] != "else":
                        formatted_code += (
                            "\n"
                            + "\t" * indent_level
                            + value
                            + "\n"
                            + "\t" * indent_level
                        )
                        continue
                if tokens[i - 1][0] == "NUMBER":
                    formatted_code += value
                    continue
                formatted_code += "\n" + "\t" * indent_level + value
            elif value == ";":
                if (
                    tokens[i + 1][0] == "STRING_LITERAL"
                    or tokens[i + 1][0] == "PUNCTUATION"
                    or (
                        tokens[i + 1][0] == "IDENTIFIER"
                        and (
                            tokens[i - 1][0] == "NUMBER"
                            or tokens[i - 1][0] == "IDENTIFIER"
                        )
                        and tokens[i - 3][0] == "IDENTIFIER"
                    )
                ) and tokens[i + 1][1] != "printf":
                    formatted_code += value
                    continue
                formatted_code += value + "\n" + "\t" * indent_level
            elif value == "[" or value == "]":
                formatted_code += value
            # elif value in ["if", "else", "for", "while", "do"]:
            #     formatted_code += " " + value + " "
            elif token_type == "PUNCTUATION" and tokens[i + 1][0] == "PUNCTUATION":
                formatted_code += value
            elif token_type in ["OPERATOR", "PUNCTUATION"]:
                if tokens[i - 1][0] == "KEYWORD":
                    formatted_code += value
                    continue
                formatted_code += " " + value + " "
            elif token_type == "IDENTIFIER" and (
                tokens[i - 1][1] == "KEYWORD" or tokens[i - 1][1] == "*"
            ):
                formatted_code += value + " "  # Add space after identifiers
            elif token_type == "IDENTIFIER":
                if tokens[i + 1][0] == "IDENTIFIER":
                    formatted_code += value + " "
                    continue
                formatted_code += value  # Add space after identifiers
            elif token_type == "KEYWORD":
                formatted_code += value + " "
            # new rule
            elif token_type == "STD" and tokens[i + 1][0] == "STREAM_INSERTION":
                if tokens[i + 2][0] == "STRING_LITERAL":
                    formatted_code += (
                        "\t" * indent_level
                        + value
                        + tokens[i + 1][1]
                        + tokens[i + 2][1]
                    )
                    i += 2  # Skip next two tokens
                    continue
                else:
                    formatted_code += value + tokens[i + 1][1]
            elif value == ">" and (
                tokens[i + 1][0] == "KEYWORD" or tokens[i + 1][1] == "#"
            ):
                formatted_code += value + "\n"
            else:
                formatted_code += value

        return formatted_code.strip()
    except:
        print("not nice")
        return formatted_code.strip()


def createAstText(code):
    parser = c_parser.CParser()
    ast = parser.parse(code)
    return ast


def createAst(code):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(
        """From a C code I want to create an AST which is converted to dot code for GRAPHVIZ please do that for me (IMPORTANT:- Give me the simple dot code). Example:- (code: -#include<stdio.h> void main(){int c=1;printf("lol");} diagraph:- 
        digraph G {
            node[shape=box]

            0 [label="main"]
            1 [label="c=1"]
            2 [label="printf(\"lol\")"]

            0 -> 1
            1 -> 2
        }
        . Important:- I only wanted the DOT code and nothing else as this is an api call (Make sure to not include any other words other than the code i have asked for and if you have to return quotes \" or \' you need to return it with a backslash character) .Now this is the original c code -> """
        + code
    )
    print(response.text)
    # listR = response.text.split("```")
    # listR2 = listR[1].split("dot")
    # print(listR2)
    with open("input.dot", "w") as f:
        f.write(response.text)
    # Print the JSON response
    print(response.text)
    # print(response.text)
    with open("input.dot", "r") as f:
        dot_code = f.read()

    # Create a Graphviz object from the Dot code
    graph = Source(dot_code)

    # Render the graph to a PNG file
    graph.render("output", format="png", cleanup=True)


@app.route("/formatCode", methods=["POST"])
def format_code_endpoint():
    data = request.json
    source_code = data.get("source_code", "")
    tokens = tokenize(source_code)
    formatted_code = format_code(tokens)
    response = jsonify({"formatted_code": formatted_code})
    return response


@app.route("/generateAST", methods=["POST"])
def generateAST_endpoint():
    data = request.json
    print("Received data:", data)
    code = data.get("code", "")
    createAst(code)
    return send_file("output.png", mimetype="image/png")


@app.route("/generateasttext", methods=["POST"])
def generateASTText_endpoint():
    data = request.json
    print("Received data:", data)
    code = data.get("code", "")
    astCode = createAstText(code)
    response = jsonify({"ast_code": str(astCode)})
    return response


if __name__ == "__main__":
    app.run(debug=True)
