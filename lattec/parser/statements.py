import parsy as P
from . import general as G
from . import expressions as E
from . import types as T
from .. import ast


@G.addpos
@P.generate
def block():
    yield G.rword("{")
    ret = yield (
        (statement << G.rword(";").optional())
        .many()
        .map(lambda l: ast.Block(statements=l))
    )
    yield G.rword("}")
    return ret


@G.addpos
@P.generate
def declaration():
    type = yield T.type
    decls = yield (
        P.seq(E.variable, (G.rword("=") >> E.expression).optional())
        .combine(
            lambda v, e:
                [ast.Declaration(start=v.start, end=v.end, type=type, var=v)] +
                ([ast.Assignment(start=v.start, end=e.end, var=v, expr=e)] if e else [])
        )
        .at_least(1)
    )
    return ast.InlinedBlock(statements=sum(decls, []))


assignment = G.addpos(
    P.seq(E.variable, G.rword("=") >> E.expression)
    .combine(lambda v, e: ast.Assignment(var=v, expr=e))
)


free_expr = E.expression.map(lambda e: ast.FreeExpression(start=e.start, end=e.end, expr=e))


plusplus = G.addpos(
    (E.variable << G.rword("++")).map(lambda v: ast.Assignment(
        var=v,
        expr=ast.Application(
            function=E.binary_operator_map["+"],
            args=[v, ast.IConstant(val=1)]
        )
    ))
)


minusminus = G.addpos(
    (E.variable << G.rword("--")).map(lambda v: ast.Assignment(
        var=v,
        expr=ast.Application(
            function=E.binary_operator_map["-"],
            args=[v, ast.IConstant(val=1)]
        )
    ))
)


ret = G.addpos((G.rword("ret") >> E.expression.optional()).map(lambda v: ast.Return(val=v)))


@G.addpos
@P.generate
def if_stmt():
    yield G.rword("if")
    cond = yield G.parens(E.expression)
    then_branch = yield statement
    else_branch = yield (G.rword("else") >> statement).optional()
    return ast.If(cond=cond, then_branch=then_branch, else_branch=else_branch)


@G.addpos
@P.generate
def while_stmt():
    yield G.rword("while")
    cond = yield G.parens(E.expression)
    body = yield statement
    return ast.While(cond=cond, body=body)


statement = P.alt(
    block,
    declaration,
    assignment,
    plusplus,
    minusminus,
    ret,
    if_stmt,
    while_stmt,
    free_expr
)
