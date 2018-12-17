import typing
import attr


@attr.s(frozen=True, auto_attribs=True)
class Type:
    pass


@attr.s(frozen=True, auto_attribs=True)
class Int(Type):
    pass


@attr.s(frozen=True, auto_attribs=True)
class Bool(Type):
    pass


@attr.s(frozen=True, auto_attribs=True)
class String(Type):
    pass


@attr.s(frozen=True, auto_attribs=True)
class Function(Type):
    params: typing.List[Type]
    ret: Type
