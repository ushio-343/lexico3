from flask import Flask, render_template, request
import ply.lex as lex

app = Flask(__name__)

# Definición de palabras reservadas para cada lenguaje
reserved_words = {
    'Python': {'if', 'else', 'while', 'for', 'return', 'def', 'class', 'try', 'except', 'import', 'from', 'as',
               'pass', 'break', 'continue', 'with', 'assert', 'lambda', 'yield', 'raise', 'global', 'nonlocal',
               'del', 'not', 'or', 'and', 'in', 'is'},
    'Java': {'if', 'else', 'while', 'for', 'return', 'class', 'try', 'catch', 'import', 'package', 'public', 'private',
             'protected', 'static', 'final', 'void', 'int', 'float', 'double', 'boolean', 'char', 'new', 'null', 'true',
             'false', 'break', 'continue', 'this', 'super', 'extends', 'implements', 'interface', 'abstract',
             'synchronized', 'volatile', 'native', 'strictfp', 'transient', 'instanceof', 'assert', 'enum', 'goto'},
    'JavaScript': {'if', 'else', 'while', 'for', 'return', 'function', 'class', 'try', 'catch', 'import', 'export', 'let',
                   'const', 'var', 'this', 'new', 'null', 'true', 'false', 'break', 'continue', 'switch', 'case', 'default',
                   'throw', 'async', 'await', 'yield', 'delete', 'typeof', 'instanceof', 'void', 'with', 'do', 'in', 'of'}
}

all_reserved = {word: lang for lang, words in reserved_words.items() for word in words}

# Lista de nombres de tokens
tokens = [
    'ID', 'PLUS', 'EQUAL', 'ACENTO', 'ERROR',
    'OPEN_PAREN', 'CLOSE_PAREN', 'OPEN_BRACE', 'CLOSE_BRACE', 'COMMA', 'SEMICOLON',
    'RESERVED', 'IDENTIFIER'
]

# Reglas de expresión regular para tokens simples
t_PLUS = r'\+'
t_EQUAL = r'='
t_OPEN_PAREN = r'\('
t_CLOSE_PAREN = r'\)'
t_OPEN_BRACE = r'\{'
t_CLOSE_BRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'
t_ACENTO = r'"'
t_ignore = ' \t\n\r'

# Regla de expresión regular para identificadores y palabras reservadas
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9]*'
    t.type = 'RESERVED' if t.value in all_reserved else 'ID'
    return t

# Manejo de errores
def t_error(t):
    t.type = 'ERROR'
    t.value = f"Illegal character '{t.value[0]}'"
    t.lexer.skip(1)
    return t

# Construcción del lexer
lexer = lex.lex()

@app.route('/', methods=['GET', 'POST'])
def index():
    token_data = []
    totals = {
        'errors': 0, 'open_paren': 0, 'close_paren': 0, 'open_brace': 0, 'close_brace': 0,
        'comma': 0, 'semicolon': 0, 'equal': 0, 'identifiers': 0, 'reserved': 0
    }
    reserved_seen = set()

    if request.method == 'POST':
        code = request.form.get('code', '')
        lexer.input(code)
        while (tok := lexer.token()) is not None:
            if tok.type == 'ERROR':
                totals['errors'] += 1
            elif tok.type == 'OPEN_PAREN':
                totals['open_paren'] += 1
            elif tok.type == 'CLOSE_PAREN':
                totals['close_paren'] += 1
            elif tok.type == 'OPEN_BRACE':
                totals['open_brace'] += 1
            elif tok.type == 'CLOSE_BRACE':
                totals['close_brace'] += 1
            elif tok.type == 'COMMA':
                totals['comma'] += 1
            elif tok.type == 'SEMICOLON':
                totals['semicolon'] += 1
            elif tok.type == 'EQUAL':
                totals['equal'] += 1
            elif tok.type == 'ID':
                totals['identifiers'] += 1
            elif tok.type == 'RESERVED':
                if tok.value not in reserved_seen:
                    reserved_seen.add(tok.value)
                    token_data.append({
                        'token': tok.value, 'reserved': 'X', 'identifier': '', 'symbol': '', 'error': '',
                        'languages': ', '.join([lang for lang, words in reserved_words.items() if tok.value in words])
                    })
                totals['reserved'] += 1

            if tok.type != 'RESERVED' or tok.value not in reserved_seen:
                token_data.append({
                    'token': tok.value, 'reserved': 'X' if tok.type == 'RESERVED' else '',
                    'identifier': 'X' if tok.type == 'ID' else '',
                    'symbol': 'X' if tok.type in {'PLUS', 'EQUAL', 'OPEN_PAREN', 'CLOSE_PAREN', 'OPEN_BRACE', 'CLOSE_BRACE', 'COMMA', 'SEMICOLON', 'ACENTO'} else '',
                    'error': 'X' if tok.type == 'ERROR' else '',
                    'languages': ', '.join([lang for lang, words in reserved_words.items() if tok.value in words]) if tok.type == 'RESERVED' else 'None'
                })

    return render_template('web.html', token_data=token_data, totals=totals)

if __name__ == "__main__":
    app.run(debug=True)
