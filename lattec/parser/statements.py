import parsy as P
from . import general as G
from . import expressions as E
from . import types as T
from .. import ast, errors, prelude


@G.addpos
@P.generate
def brace_block():
    yield G.symbol("{")
    ret = yield (
        raw_statement
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
                [ast.decl_from_var_type(v, type)] +
                ([ast.Assignment(start=v.start, end=e.end, var=v, expr=e)] if e else [])
        )
        .sep_by(G.symbol(","), min=1)
    )
    yield G.symbol(";")
    return ast.InlinedBlock(statements=sum(decls, []))


assignment = G.addpos(
    P.seq(E.variable, G.symbol("=") >> E.expression)
    .combine(lambda v, e: ast.Assignment(var=v, expr=e)) << G.symbol(";")
)


free_expr = (E.expression << G.symbol(";")).map(
    lambda e: ast.FreeExpression(start=e.start, end=e.end, expr=e))


plusplus = G.addpos(
    (E.variable << G.symbol("++") << G.symbol(";")).map(lambda v: ast.Assignment(
        var=v,
        expr=ast.Application(
            function=E.var_from_op(prelude.binary_operator_map["+"]),
            args=[v, ast.IConstant(val=1)]
        )
    ))
)


minusminus = G.addpos(
    (E.variable << G.symbol("--") << G.symbol(";")).map(lambda v: ast.Assignment(
        var=v,
        expr=ast.Application(
            function=E.var_from_op(prelude.binary_operator_map["-"]),
            args=[v, ast.IConstant(val=1)]
        )
    ))
)


@G.addpos
@P.generate
def ret():
    yield G.rword("return")
    expr = yield E.expression.optional()
    yield G.symbol(";")
    return ast.Return(val=expr)


@G.addpos
@P.generate
def if_stmt():
    yield G.rword("if")
    cond = yield G.parens(E.expression)
    then_branch = yield statement
    else_branch = yield (G.rword("else") >> statement).optional()
    if (
        "generated" in then_branch.attrs
        and isinstance(then_branch.statements[0], ast.If)
        and then_branch.statements[0].else_branch is not None
    ):
        errors.add_error(errors.Error(
            start=then_branch.start,
            end=then_branch.end,
            kind=errors.ParseKind.AmbiguousIf,
            message="There is an ambiguous if-if-else construct."
        ))
    return ast.If(cond=cond, then_branch=then_branch, else_branch=else_branch)


@G.addpos
@P.generate
def while_stmt():
    yield G.rword("while")
    cond = yield G.parens(E.expression)
    body = yield statement
    return ast.While(cond=cond, body=body)


raw_statement = P.alt(
    brace_block,
    declaration,
    assignment,
    plusplus,
    minusminus,
    ret,
    if_stmt,
    while_stmt,
    free_expr
)


@G.addpos
@P.generate
def statement():
    st = yield raw_statement
    if not isinstance(st, ast.Block):
        bl = ast.Block(statements=[st])
        bl.attrs["generated"] = True
        return bl
    return st
