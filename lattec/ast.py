import typing
import attr
from . import types


# GENERAL


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Position:
    line: int
    column: int


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Node:
    start: typing.Optional[Position] = None
    end: typing.Optional[Position] = None


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Operator(Node):
    symbol: str
    name: str
    precedence: int
    associativity: str  # "left" or "right"


# EXPRESSIONS


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Expression(Node):
    pass


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Variable(Expression):
    var: str


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class IConstant(Expression):
    val: int


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class BConstant(Expression):
    val: bool


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class SConstant(Expression):
    val: str


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Application(Expression):
    function: str  # TODO: type?
    arguments: typing.List[Expression]


# STATEMENTS


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Statement(Node):
    pass


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Assignment(Statement):
    var: str
    expr: Expression


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Block(Statement):
    statements: typing.List[Statement]


# TOPLEVEL


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Function(Node):
    type: types.Type
    name: str
    params: typing.List[str]
    body: Block


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Program(Node):
    decls: typing.List[Function]


def pprint(tree: Node, prefix: str = "") -> None:
    d = attr.asdict(tree, recurse=False)
    print(f"{tree.__class__.__name__}")
    for k, v in d.items():
        if k not in ["start", "end"]:
            print(f"{prefix}{k}: ", end="")
            if isinstance(v, list):
                print()
                for i, e in enumerate(v):
                    print(f"{prefix}  {i}: ", end="")
                    pprint(e, prefix+"    ")
            elif isinstance(v, Node):
                pprint(v, prefix+"  ")
            else:
                print(f"{v}")
