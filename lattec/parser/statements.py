import parsy as P
from . import general as G
from . import expressions as E
from . import types as T
from .. import ast


@G.addpos
@P.generate
def block():
    yield G.symbol("{")
    ret = yield (
        statement
        .many()
        .map(lambda l: ast.Block(statements=l))
    )
    yield G.symbol("}")
    return ret


@G.addpos
@P.generate
def declaration():
    type = yield T.type
    decls = yield (
        P.seq(E.variable, (G.symbol("=") >> E.expression).optional())
        .combine(
            lambda v, e:
                [ast.Declaration(start=v.start, end=v.end, type=type, var=v)] +
                ([ast.Assignment(start=v.start, end=e.end, var=v, expr=e)] if e else [])
        )
        .at_least(1)
    )
    return ast.InlinedBlock(statements=sum(decls, []))


assignment = G.addpos(
    P.seq(E.variable, G.symbol("=") >> E.expression)
    .combine(lambda v, e: ast.Assignment(var=v, expr=e))
)


free_expr = E.expression.map(lambda e: ast.FreeExpression(start=e.start, end=e.end, expr=e))


plusplus = G.addpos(
    (E.variable << G.symbol("++")).map(lambda v: ast.Assignment(
        var=v,
        expr=ast.Application(
            function=E.binary_operator_map["+"],
            args=[v, ast.IConstant(val=1)]
        )
    ))
)


minusminus = G.addpos(
    (E.variable << G.symbol("--")).map(lambda v: ast.Assignment(
        var=v,
        expr=ast.Application(
            function=E.binary_operator_map["-"],
            args=[v, ast.IConstant(val=1)]
        )
    ))
)


@G.addpos
@P.generate
def ret():
    yield G.rword("return")
    expr = yield E.expression.optional()
    print(expr)
    if not expr:
        yield G.symbol(";")
    return ast.Return(val=expr)


@G.addpos
@P.generate
def if_stmt():
    yield G.rword("if")
    cond = yield G.parens(E.expression)
    then_branch = yield statement
    else_branch = yield (G.rword("else") >> statement).optional()
    print(else_branch)
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
) << G.symbol(";").optional()
