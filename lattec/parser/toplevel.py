import parsy as P
from . import general as G
from . import expressions as E
from . import statements as S
from . import types as T
from .. import ast
from .. import errors


@G.addpos
@P.generate
def function():
    hd_beg = yield G.pos
    ret = yield T.type
    name = yield G.identifier
    params = yield G.parens(P.seq(T.type, E.variable).sep_by(G.symbol(",")))
    hd_end = yield G.pos
    body = yield S.statement
    types = [e[0] for e in params]
    vars = [ast.decl_from_var_type(v, t) for t, v in params]
    type = ast.Function(start=hd_beg, end=hd_end, params=types, ret=ret)
    return ast.FunctionDeclaration(type=type, name=name, params=vars, body=body)


@G.addpos
@P.generate
def program():
    decls = yield G.sc >> function.many()
    return ast.Program(decls=decls)


def program_parser(prog: str) -> ast.Node:
    try:
        result = program.parse(prog)
        return result
    except P.ParseError as e:
        l, c = P.line_info_at(e.stream, e.index)
        errors.add_error(errors.Error(
            start=ast.Position(line=l+1, column=c),
            end=ast.Position(line=l+1, column=c),
            kind=errors.ParseKind.ParserError,
            message=str(e)
        ))
        return ast.Nothing()
