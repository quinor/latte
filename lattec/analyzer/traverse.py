import typing
import attr
from .. import ast


def traverse(
    root: ast.Node,
    pre_order: typing.Callable[[ast.Node], None] = None,
    post_order: typing.Callable[[ast.Node], None] = None,
) -> None:
    def traverse_impl(tree: ast.Node) -> None:
        if pre_order:
            pre_order(tree)

        d = attr.asdict(tree, recurse=False)
        for k, v in d.items():
            if isinstance(v, list):
                for e in v:
                    if isinstance(e, ast.Node):
                        traverse_impl(e)
            elif isinstance(v, ast.Node):
                traverse_impl(v)

        if post_order:
            post_order(tree)

    traverse_impl(root)
