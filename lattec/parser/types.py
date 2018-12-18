from . import general as G
from .. import ast


int_t = G.addpos(G.rword("int").map(lambda e: ast.Int()))


boolean_t = G.addpos(G.rword("boolean").map(lambda e: ast.Int()))


string_t = G.addpos(G.rword("string").map(lambda e: ast.Int()))


void_t = G.addpos(G.rword("void").map(lambda e: ast.Int()))


type = int_t | boolean_t | string_t | void_t
