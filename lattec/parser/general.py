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


pos = P.line_info.combine(lambda l, c: ast.Position(line=l+1, column=c))


def addpos(p):
    @P.generate
    def addpos_impl():
        beg = yield pos
        obj = yield p
        end = yield pos
        assert isinstance(obj, ast.Node)
        return attr.evolve(obj, start=beg, end=end)
    return addpos_impl


sc = P.alt(
    P.regex(r"\s+", P.re.MULTILINE),
    P.regex(r"/\*.*?\*/", P.re.MULTILINE | P.re.DOTALL),
    P.regex(r"//.*\n"),
    P.regex(r"#.*\n"),
).desc("whitespace").many()


def lexeme(p):
    return p << sc


def symbol(str):
    return lexeme(P.string(str))


def rword(str):
    @lexeme
    @P.generate
    def rword_impl():
        yield P.string(str)
        yield identifier.should_fail("too long identifier")
    return rword_impl


def parens(p):
    return symbol("(") >> p << symbol(")")


number = lexeme(P.regex(r'(0|[1-9][0-9]*)')).map(int).desc("integer")


@P.generate
def identifier_impl():
    lex = yield lexeme(P.regex(r"[_a-zA-Z][_'a-zA-Z0-9]*"))
    if lex in reserved:
        return P.fail("<not a reserved identifier>")
    return lex


identifier = identifier_impl.desc("identifier")
