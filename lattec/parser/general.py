import parsy as P
import attr
from .. import ast


reserved = [
    "if",
    "else",
    "while",
    "return",
    "int",
    "string",
    "boolean",
    "void",
    "true",
    "false",
]


pos = P.line_info.combine(lambda l, c: ast.Position(line=l, column=c))


def addpos(p):
    @P.generate
    def addpos_impl():
        beg = yield pos
        obj = yield p
        end = yield pos

        if not isinstance(obj, ast.Node):
            raise Exception("Internal error: expected a ast.Node, got {}".format(type(obj)))

        return attr.evolve(obj, start=beg, end=end)
    return addpos_impl


sc = P.alt(
    P.regex(r"\s+", P.re.MULTILINE),
    P.regex(r"/\*.*?\*/", P.re.MULTILINE | P.re.DOTALL),
    P.regex(r"//.*\n"),
    P.regex(r"#.*\n"),
).many()


def lexeme(p):
    return p << sc


def rword(str):
    return lexeme(P.string(str))


def parens(p):
    return rword("(") >> p << rword(")")


number = lexeme(P.regex(r'(0|[1-9][0-9]*)')).map(int)


@P.generate
def identifier():
    lex = yield lexeme(P.regex(r"[_a-zA-Z][_'a-zA-Z0-9]*"))
    if lex in reserved:
        # TODO: soft error into some kind of a global structure
        return P.fail("<not a reserved identifier>")
    return lex
