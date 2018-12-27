import typing
import attr
from .. import ast


def traverse(
    root: ast.Node,
    pre_order: typing.List[typing.Callable[[ast.Node], None]] = [],
    post_order: typing.List[typing.Callable[[ast.Node], None]] = [],
) -> None:
    def traverse_impl(tree: ast.Node) -> None:
        for f in pre_order:
            f(tree)

        d = attr.asdict(tree, recurse=False)
        for k, v in d.items():
            if isinstance(v, list):
                for e in v:
                    if isinstance(e, ast.Node):
                        traverse_impl(e)
            elif isinstance(v, ast.Node):
                traverse_impl(v)

        for f in post_order:
            f(tree)

    traverse_impl(root)
