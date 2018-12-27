from . import ast


unary_bool = ast.Function(params=[ast.Bool()], ret=ast.Bool())
unary_int = ast.Function(params=[ast.Int()], ret=ast.Int())
binary_bool = ast.Function(params=[ast.Bool(), ast.Bool()], ret=ast.Bool())
binary_int = ast.Function(params=[ast.Int(), ast.Int()], ret=ast.Int())
binary_int_bool = ast.Function(params=[ast.Int(), ast.Int()], ret=ast.Bool())
binary_string_bool = ast.Function(params=[ast.String(), ast.String()], ret=ast.Bool())
binray_string = ast.Function(params=[ast.String(), ast.String()], ret=ast.String())

prelude_types = [
    ("printInt", ast.Function(params=[ast.Int()], ret=ast.Void())),
    ("printString", ast.Function(params=[ast.String()], ret=ast.Void())),
    ("error", ast.Function(params=[], ret=ast.Void())),
    ("readInt", ast.Function(params=[], ret=ast.Int())),
    ("readString", ast.Function(params=[], ret=ast.String())),
    ("__builtin__unary_minus", unary_int),
    ("__builtin__unary_not", unary_bool),
    ("__builtin__mod", binary_int),
    ("__builtin__mul", binary_int),
    ("__builtin__div", binary_int),
    ("__builtin__add", ast.TypeAlternative(alt=[binary_int, binray_string])),
    ("__builtin__sub", binary_int),
    ("__builtin__le", binary_int_bool),
    ("__builtin__lt", binary_int_bool),
    ("__builtin__ge", binary_int_bool),
    ("__builtin__gt", binary_int_bool),
    ("__builtin__eq", ast.TypeAlternative(alt=[binary_int_bool, binary_string_bool, binary_bool])),
    ("__builtin__ne", ast.TypeAlternative(alt=[binary_int_bool, binary_string_bool, binary_bool])),
    ("__builtin__and", binary_bool),
    ("__builtin__or", binary_bool),
]


unary_operator_map = {
    "-": ast.Operator(
        symbol="-", name="__builtin__unary_minus", precedence=3, associativity="right"),
    "!": ast.Operator(
        symbol="!", name="__builtin__unary_not", precedence=3, associativity="right"),
}


# operator order such that prefixes are parsed after their supersets (ie. <= and <)
binary_operator_map = {
    "%": ast.Operator(symbol="%", name="__builtin__mod", precedence=5, associativity="left"),
    "*": ast.Operator(symbol="*", name="__builtin__mul", precedence=5, associativity="left"),
    "/": ast.Operator(symbol="/", name="__builtin__div", precedence=5, associativity="left"),
    "+": ast.Operator(symbol="+", name="__builtin__add", precedence=6, associativity="left"),
    "-": ast.Operator(symbol="-", name="__builtin__sub", precedence=6, associativity="left"),
    "<=": ast.Operator(symbol="<=", name="__builtin__le", precedence=9, associativity="left"),
    "<":  ast.Operator(symbol="<",  name="__builtin__lt", precedence=9, associativity="left"),
    ">=": ast.Operator(symbol=">=", name="__builtin__ge", precedence=9, associativity="left"),
    ">":  ast.Operator(symbol=">",  name="__builtin__gt", precedence=9, associativity="left"),
    "==": ast.Operator(symbol="==", name="__builtin__eq", precedence=10, associativity="left"),
    "!=": ast.Operator(symbol="!=", name="__builtin__ne", precedence=10, associativity="left"),
    "&&": ast.Operator(symbol="&&", name="__builtin__and", precedence=14, associativity="left"),
    "||": ast.Operator(symbol="||", name="__builtin__or", precedence=15, associativity="left"),
}
