# LL(1) Parser Generator
[![Build Status](https://travis-ci.org/BreakingBugs/LL1-parser.svg?branch=master)](https://travis-ci.org/BreakingBugs/LL1-parser)

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
# Generar tabla de análisis predictivo
$ python parse.py "A -> hola | mundo"

# Especificar marcador EOF and símbolo vacío
$ python parse.py "A -> hola | mundo | vacio" --epsilon vacio --eof $

# Generar tabla y mostrar pasos intermedios
$ python parse.py "A -> hola | mundo" -v

# Leer gramática(s) de un archivo de texto y escribir en otro archivo
$ python parse.py -i grammar.txt -o table.txt

# Mostrar mensaje de ayuda
$ python parse.py --help
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

# Calcula la tabla de analisis predictivo, sin realizar preprocesamiento
table, ambiguous = g.parsing_table()
pprint_table(g, table)

# Realiza preprocesamiento (factor comun y recursion por izquierda)
table, ambiguous = g.parsing_table(is_clean=False)
pprint_table(g, table)
```


### Especificacion de Gramática

Se utiliza "->" para separar el no-terminal y el cuerpo de la produccion.
Las producciones siguen el siguiente formato:

```
# Comentarios se ignoran
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

Finalmente, ingrese desde su navegador a [http://localhost:5000](http://localhost:5000).

![screen1](http://i.imgur.com/SzITp1I.png)
![screen2](http://imgur.com/Y8DZsKk.png)

## Team
- Jordan Ayala [jmayalag](https://github.com/jmayalag)
- Guillermo Peralta [voluntadpear](https://github.com/voluntadpear)

## Contributing

#### Bug Reports & Feature Requests

Usar el [issue tracker](https://github.com/BreakingBugs/LL1-parser/issues) para reportar bugs o sugerir algún feature.