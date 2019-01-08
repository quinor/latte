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


def _constant(v: ast.Variable, t: ast.Type) -> ast.Expression:
    if isinstance(t, ast.Bool):
        return ast.BConstant(val=False)
    if isinstance(t, ast.Int):
        return ast.IConstant(val=0)
    if isinstance(t, ast.String):
        return ast.SConstant(val="")

    errors.add_error(errors.Error(
        start=v.start,
        end=v.end,
        kind=errors.ParseKind.NoDefaultValue,
        message="There is an empty variable with no inferable default value."
    ))
    return ast.Nothing()  # type: ignore


@G.addpos
@P.generate
def declaration():
    type = yield T.type
    raw_decls = yield (
        P.seq(E.variable, (G.symbol("=") >> E.expression).optional())
        .sep_by(G.symbol(","), min=1)
    )
    decls = []
    vnames = [v.var for v, e in raw_decls]
    for v, e in raw_decls:
        decls.append(ast.decl_from_var_type(v, type))
    for v, e in raw_decls:
        if e:
            decls.append(ast.Assignment(start=v.start, end=e.end, var=v, expr=e))
        else:
            decls.append(ast.Assignment(start=v.start, end=v.end, var=v, expr=_constant(v, type)))
        decls[-1].expr.attrs.ignore_names = vnames
    yield G.symbol(";")
    ret = ast.InlinedBlock(statements=decls)
    return ret


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
        then_branch.attrs.generated is not None
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
        bl.attrs.generated = True
        return bl
    return st
