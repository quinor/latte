import typing
import attr
from . import ast


@attr.s(frozen=True, auto_attribs=True, repr=False)
class RegType:
    pass


@attr.s(frozen=True, auto_attribs=True, repr=False)
class I1(RegType):
    def __repr__(self):
        return "i1"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class I8(RegType):
    def __repr__(self):
        return "i8"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class I32(RegType):
    def __repr__(self):
        return "i32"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class String(RegType):
    def __repr__(self):
        return "String"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class Void(RegType):
    def __repr__(self):
        return "void"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class Ptr(RegType):
    type: RegType

    def __repr__(self):
        return f"{self.type}*"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class Array(RegType):
    cnt: int
    type: RegType

    def __repr__(self):
        return f"[{self.cnt} x {self.type}]"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class FunctionPtr(RegType):
    ret: RegType
    args: typing.List[RegType]

    def __repr__(self):
        return f"{self.ret} ({', '.join(map(str, self.args))})"


@attr.s(frozen=True, auto_attribs=True)
class Val:
    type: RegType


@attr.s(frozen=True, auto_attribs=True, repr=False)
class Var(Val):
    name: str

    def __repr__(self):
        return f"%{self.name}"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class GlobalVar(Val):
    name: str

    def __repr__(self):
        return f"@{self.name}"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class SConstant(Val):
    value: str

    def __repr__(self):
        return f"{self.value}"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class Constant(Val):
    value: int

    def __repr__(self):
        return f"{self.value}"


@attr.s(frozen=True, auto_attribs=True)
class Quad:
    pass


@attr.s(frozen=True, auto_attribs=True)
class Declaration(Quad):
    var: Var


@attr.s(frozen=True, auto_attribs=True, repr=False)
class Label(Quad):
    name: str

    def __repr__(self):
        return f"%{self.name}"


@attr.s(frozen=True, auto_attribs=True)
class Function(Quad):
    ret: RegType
    name: str
    params: typing.List[Var]
    body: typing.List[Quad]


@attr.s(frozen=True, auto_attribs=True)
class Call(Quad):
    target: typing.Optional[Var]  # None if void
    function: Val
    params: typing.List[Val]


@attr.s(frozen=True, auto_attribs=True)
class CondBranch(Quad):
    cond: Val
    target_true: Label
    target_false: Label


@attr.s(frozen=True, auto_attribs=True)
class Branch(Quad):
    target: Label


@attr.s(frozen=True, auto_attribs=True)
class Return(Quad):
    val: typing.Optional[Val]


def from_ast_type(t: ast.Type) -> RegType:
    if isinstance(t, ast.Int):
        return I32()
    elif isinstance(t, ast.Bool):
        return I1()
    elif isinstance(t, ast.String):
        return String()
    elif isinstance(t, ast.Void):
        return Void()
    elif isinstance(t, ast.Function):
        return FunctionPtr(
            from_ast_type(t.ret),
            list(map(from_ast_type, t.params))
        )
    else:
        print(t)
        raise Exception("Type not supported")


def identity(t: RegType) -> GlobalVar:
    return GlobalVar(FunctionPtr(t, [t]), name="__builtin__id")


var_cnt: int = 0
label_cnt: int = 0


quad_list: typing.List[Quad] = []
defer_stack: typing.List[typing.List[Quad]] = []


def gather() -> typing.List[Quad]:
    ret = quad_list[:]
    quad_list.clear()
    return ret


def reset_counters() -> None:
    global var_cnt
    global label_cnt
    var_cnt = 0
    label_cnt = 0


def new_var(t: RegType) -> Var:
    global var_cnt
    name = f"v{var_cnt}"
    var_cnt += 1
    return Var(t, name)


def new_label() -> Label:
    global label_cnt
    name = f"L{label_cnt}"
    label_cnt += 1
    return Label(name)


def add_quad(q: Quad) -> None:
    quad_list.append(q)


def add_defer(q: Quad) -> None:
    defer_stack[-1].append(q)


def open_defer_scope() -> None:
    defer_stack.append([])


def close_defer_scope() -> typing.List[Quad]:
    return defer_stack.pop()
