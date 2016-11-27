import traceback

from flask import Flask
from flask import render_template
from flask import request
from parser.functions import parse_bnf, remove_left_recursion, remove_left_factoring, InvalidGrammar
from parser.rule import InvalidProduction

app = Flask(__name__)


def just_do_it(req):
    errors = []
    g = None
    grammar_not_recursive = None
    grammar_not_factor = None
    parsing_table = None

    try:
        g = parse_bnf(req.form['bnf'], epsilon=req.form['epsilon'], eof=req.form['eof'])
        grammar_not_recursive = remove_left_recursion(g)
        grammar_not_factor = remove_left_factoring(grammar_not_recursive)
        table, ambiguous = grammar_not_factor.parsing_table()

        if ambiguous:
            errors.append('El lenguaje de entrada no es LL(1) debido a que se encontraron ambigüedades.')

        parsing_table = {'table': table,
                         'terminals': sorted(set(g.terminals) - {g.epsilon}) + [g.eof],
                         'nonterminals': [nt for nt in grammar_not_factor.nonterminals]}

    except InvalidGrammar:
        errors.append('Gramática inválida. Revise las especificaciones de BNF.')
    except InvalidProduction as e:
        errors.append('Produccion invalida: {}.'.format(e.production))

    return render_template('results.html', grammar=g, no_recursion=grammar_not_recursive, no_factor=grammar_not_factor,
                           parsing_table=parsing_table, errors=errors)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        return just_do_it(request)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    app.run()
