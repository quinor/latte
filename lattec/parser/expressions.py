import parsy as P
from . import general as G
from .. import ast
from .general import * # noqa


variable = G.addpos(G.identifier.map(lambda v: ast.Variable(var=v)))


int_literal = G.addpos(G.number.map(lambda v: ast.IConstant(val=v)))


bool_literal = G.addpos(
    (G.rword("true").result(True) | G.rword("false").result(False))
    .map(lambda v: ast.BConstant(val=v))
)


string_literal = G.addpos(P.regex(r'".*?"').map(lambda s: ast.SConstant(val=s)))


unary_operator_map = {
    "-": ast.Operator(symbol="-", name="unary_minus", precedence=3, associativity="right"),
    "!": ast.Operator(symbol="!", name="unary_not", precedence=3, associativity="right"),
}

binary_operator_map = {
    "%": ast.Operator(symbol="%", name="mod", precedence=5, associativity="left"),
    "*": ast.Operator(symbol="*", name="mul", precedence=5, associativity="left"),
    "/": ast.Operator(symbol="/", name="div", precedence=5, associativity="left"),
    "+": ast.Operator(symbol="+", name="add", precedence=6, associativity="left"),
    "-": ast.Operator(symbol="-", name="sub", precedence=6, associativity="left"),
    "<":  ast.Operator(symbol="<",  name="lt", precedence=9, associativity="left"),
    "<=": ast.Operator(symbol="<=", name="le", precedence=9, associativity="left"),
    ">":  ast.Operator(symbol=">",  name="gt", precedence=9, associativity="left"),
    ">=": ast.Operator(symbol=">=", name="ge", precedence=9, associativity="left"),
    "==": ast.Operator(symbol="==", name="eq", precedence=10, associativity="left"),
    "!=": ast.Operator(symbol="!=", name="ne", precedence=10, associativity="left"),
    "&&": ast.Operator(symbol="&&", name="and", precedence=14, associativity="left"),
    "||": ast.Operator(symbol="||", name="or", precedence=15, associativity="left"),
}

unary_operator = G.addpos(P.alt(*map(
    lambda k: G.rword(k).result(unary_operator_map[k]),
    unary_operator_map.keys()
)))


binary_operator = G.addpos(P.alt(*map(
    lambda k: G.rword(k).result(binary_operator_map[k]),
    binary_operator_map.keys()
)))


@P.generate
def single_expression():
    start = yield G.pos
    unary = yield unary_operator.optional()
    elt = yield variable | int_literal | bool_literal | string_literal | G.parens(expression)
    end = yield G.pos
    if unary is not None:
        return ast.Application(start=start, end=end, function=unary, arguments=[elt])
    else:
        return elt


@P.generate
def expression():
    fst = yield single_expression
    rest = yield P.seq(binary_operator, single_expression).map(tuple).many()

    val_stack = [fst]
    op_stack = []

    def apply_op():
        h2 = val_stack.pop()
        h1 = val_stack.pop()
        o = op_stack.pop()
        val_stack.append(ast.Application(
            start=h1.start,
            end=h2.end,
            function=o,
            arguments=[h1, h2]
        ))

    for op, val in rest:
        while len(op_stack) != 0 and (
            op_stack[-1].precedence < op.precedence or
            (op_stack[-1].precedence == op.precedence and op_stack[-1].associativity == "left")
        ):
            apply_op()
        op_stack.append(op)
        val_stack.append(val)

    while len(op_stack) != 0:
        apply_op()
    assert len(val_stack) == 1 and len(op_stack) == 0

    return val_stack[-1]
