import typing
import attr


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


# TYPES


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Type(Node):
    pass


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Int(Type):
    pass


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Bool(Type):
    pass


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class String(Type):
    pass


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Function(Type):
    params: typing.List[Type]
    ret: Type


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
    function: typing.Union[Variable, Operator]
    args: typing.List[Expression]


# STATEMENTS


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Statement(Node):
    pass


def _stmt_convert(l: typing.List[Statement]) -> typing.List[Statement]:
    return sum(
        (e.statements if isinstance(e, InlinedBlock) else [e] for e in l),
        []
    )


@attr.s(frozen=True, kw_only=True)
class Block(Statement):
    # unroll inlined blocks in converter
    statements = attr.ib(type=typing.List[Statement], converter=_stmt_convert)


# InlinedBlock does not generate separate scope, it is to be inlined in the parent block
@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class InlinedBlock(Statement):
    statements: typing.List[Statement]


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class FreeExpression(Statement):
    expr: Expression


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Declaration(Statement):
    type: Type
    var: Variable


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Assignment(Statement):
    var: Variable
    expr: Expression


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Return(Statement):
    val: typing.Optional[Expression]


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class If(Statement):
    cond: Expression
    then_branch: Statement
    else_branch: Statement


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class While(Statement):
    cond: Expression
    body: Statement


# TOPLEVEL


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class FunctionDeclaration(Node):
    type: Type
    name: str
    params: typing.List[Variable]
    body: Statement


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Program(Node):
    decls: typing.List[FunctionDeclaration]


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
