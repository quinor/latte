import typing
import attr
from . import colors


# GENERAL


@attr.s(auto_attribs=True)
class AttrObject:
    type:           typing.Any = None
    ignore_names:   typing.Any = None
    generated:      typing.Any = None
    returns:        typing.Any = None
    value:          typing.Any = None
    quad_gen:       typing.Any = None


@attr.s(frozen=True, auto_attribs=True, kw_only=True, repr=False)
class Position:
    line: int
    column: int

    def __repr__(self):
        return f"{colors.white(str(self.line))}:{colors.white(str(self.column))}"


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Node:
    start: typing.Optional[Position] = attr.ib(cmp=False, default=None)
    end: typing.Optional[Position] = attr.ib(cmp=False, default=None)
    attrs: AttrObject = attr.ib(factory=AttrObject)


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Operator(Node):
    symbol: str
    name: str
    precedence: int
    associativity: str  # "left" or "right"


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Nothing(Node):
    pass


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class NewVariable(Node):
    var: str


# TYPES


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Type(Node):
    pass


@attr.s(frozen=True, auto_attribs=True, kw_only=True, repr=False)
class UndefinedType(Type):
    def __repr__(self):
        return colors.white("<Undefined>")


@attr.s(frozen=True, auto_attribs=True, kw_only=True, repr=False)
class Int(Type):
    def __repr__(self):
        return colors.white("int")


@attr.s(frozen=True, auto_attribs=True, kw_only=True, repr=False)
class Bool(Type):
    def __repr__(self):
        return colors.white("boolean")


@attr.s(frozen=True, auto_attribs=True, kw_only=True, repr=False)
class String(Type):
    def __repr__(self):
        return colors.white("string")


@attr.s(frozen=True, auto_attribs=True, kw_only=True, repr=False)
class Void(Type):
    def __repr__(self):
        return colors.white("void")


@attr.s(frozen=True, auto_attribs=True, kw_only=True, repr=False)
class Function(Type):
    params: typing.List[Type]
    ret: Type

    def __repr__(self):
        return colors.white(f"{self.ret}({', '.join(str(e) for e in self.params)})")


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class TypeAlternative(Type):
    alt: typing.List[Type]


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
    function: Variable
    args: typing.List[Expression]


# STATEMENTS


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Statement(Node):
    pass


def _blck_convert(l: typing.List[Statement]) -> typing.List[Statement]:
    return sum(
        (e.statements if isinstance(e, InlinedBlock) else [e] for e in l),
        []
    )


@attr.s(frozen=True, kw_only=True)
class Block(Statement):
    # unroll inlined blocks in converter
    statements = attr.ib(type=typing.List[Statement], converter=_blck_convert)


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
    var: NewVariable


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
    then_branch: Block
    else_branch: Block


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class While(Statement):
    cond: Expression
    body: Block


# TOPLEVEL


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class FunctionDeclaration(Node):
    type: Type
    name: str
    params: typing.List[Declaration]
    body: Block


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class Program(Node):
    decls: typing.List[FunctionDeclaration]


def newvar_from_var(v: Variable) -> NewVariable:
    return NewVariable(start=v.start, end=v.end, var=v.var)


def decl_from_var_type(v: Variable, t: Type) -> Declaration:
    return Declaration(start=v.start, end=v.end, type=t, var=newvar_from_var(v))


def pprint(tree: Node, prefix: str = "") -> None:
    d = attr.asdict(tree, recurse=False)
    print(f"{tree.__class__.__name__}")
    for k, v in d.items():
        if k not in ["start", "end", "attrs"]:
            print(f"{prefix}{k}: ", end="")
            if isinstance(v, list):
                print()
                for i, e in enumerate(v):
                    print(f"{prefix}  {i}: ", end="")
                    if isinstance(e, Node):
                        pprint(e, prefix+"    ")
                    else:
                        print(f"{v}")
            elif isinstance(v, Node):
                pprint(v, prefix+"  ")
            else:
                print(f"{v}")


undef_t = UndefinedType()
