import typing
import attr
from . import ast


# TYPES


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
        return "%struct.S*"


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


# VALUES


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
        r = new_str_const(self.value.replace('"', '\\"'))
        return f"{r}"


@attr.s(frozen=True, auto_attribs=True, repr=False)
class Constant(Val):
    value: int

    def __repr__(self):
        return f"{int(self.value)}"


# QUADS


@attr.s(frozen=True, auto_attribs=True)
class Quad:
    pass


@attr.s(frozen=True, auto_attribs=True, repr=False)
class Label(Quad):
    name: str

    def __repr__(self):
        return f"%{self.name}"


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


@attr.s(frozen=True, auto_attribs=True)
class Assign(Quad):
    target: Var
    source: Val


@attr.s(frozen=True, auto_attribs=True)
class Alloc(Quad):
    target: Var


@attr.s(frozen=True, auto_attribs=True)
class Load(Quad):
    target: Var
    source: Val


@attr.s(frozen=True, auto_attribs=True)
class Store(Quad):
    source: Val
    target: Var


# TOPLEVEL


@attr.s(frozen=True, auto_attribs=True)
class Function:
    ret: RegType
    name: str
    params: typing.List[Var]
    body: typing.List[Quad]


Program = typing.List[Function]


# UTILITY


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
string_cnt: int = 0
is_returned: bool = False


quad_list: typing.List[Quad] = []
defer_stack: typing.List[typing.List[Quad]] = []
string_const_list: typing.List[str] = []


def gather() -> typing.List[Quad]:
    ret = quad_list[:]
    quad_list.clear()
    return ret


def new_var(t: RegType) -> Var:
    global var_cnt
    name = f"v{var_cnt}"
    var_cnt += 1
    return Var(t, name)


def new_str_const(value: str) -> GlobalVar:
    global string_cnt
    name = f"s{string_cnt}"
    string_cnt += 1

    vl = len(value)+1
    string_const_list.append(
        f"@_{name} = internal constant [{vl} x i8] c\"{value}\\00\"\n"
        f"@{name} = global %struct.S {'{'} i8* getelementptr inbounds ([{vl} x i8], [{vl} x i8]* @_{name}, i32 0, i32 0), i32 1000000000 {'}'}\n"  # noqa
    )
    return GlobalVar(String(), name)


def get_string_consts() -> typing.List[str]:
    ret = string_const_list[:]
    string_const_list.clear()
    return ret


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
