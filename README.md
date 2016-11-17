# LL(1) Parser Generator

Genera un Analizador Predictivo para Gramáticas LL(1).


## Features

- Escrito en Python3
- No requiere otras dependencias (sí para interfaz web)
- Interfaz Web desarrollada con [Flask](http://flask.pocoo.org/)

## Installation

```bash
$ git clone git@github.com:BreakingBugs/LL1-parser.git
$ python parse.py "A -> hola | mundo"
```


## CLI Usage
```bash
# Generate parsing table
$ python parse.py "A -> hola | mundo"

# Generate parsing table and display intermediate process
$ python parse.py "A -> hola | mundo" -v

# Read grammar from file and write output to file
$ python parse.py -i grammar.txt -o table.txt
```

![cli](http://imgur.com/3vDx2Hq.png)

## API

```python
from parser.functions import parse_bnf, remove_left_recursion, remove_left_factoring, pprint_table

# Analiza la cadena de entrada para crear una Gramática
g = parse_bnf(grammar_text) 
print(g)

# Eliminar recursión por izquierda
g = remove_left_recursion(g)

# Elimina factor común por izquierda
g = remove_left_factoring(g) 

# Calcula el conjunto FIRST del símbolo de inicio
first = g.first(g.start)

# Calcula el conjunto FOLLOW del símbolo de inicio
follow = g.follow(g.start)

# Calcula la tabla de analisis predictivo
table, __ = g.parsing_table()
pprint_table(g, table)
```


### Especificacion de Gramática

Se utiliza "->" para separar el no-terminal y el cuerpo de la produccion.
Las producciones siguen el siguiente formato:

```
Start -> A
A -> ( A ) | Two
Two -> a
Two -> b
```

Se puede utilizar EBNF, donde:
```
x -> y | z
```

y

```
x -> y
x -> z
```
son equivalentes.

Importante: Cada cadena sin espacios se considera un símbolo gramatical.

Ej.: id se interpreta como un el símbolo 'id', i d se interpreta como 'i' y 'd'.


## Web Interface

Para usar la interfaz web, es necesario instalar **Flask**
```bash
$ cd web
$ pip install Flask
```

Luego se ejecuta el servidor de desarrollo de Flask
```bash
$ python web.py
```

![screen1](http://i.imgur.com/SzITp1I.png)
![screen2](http://imgur.com/Y8DZsKk.png)

## Contributing

#### Bug Reports & Feature Requests

Usar el [issue tracker](https://github.com/BreakingBugs/LL1-parser/issues) para reportar bugs o sugerir algún feature.