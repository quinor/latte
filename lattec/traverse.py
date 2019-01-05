import typing
import attr
from . import ast


def traverse(
    root: ast.Node,
    pre_order: typing.List[typing.Callable[[ast.Node], None]] = [],
    post_order: typing.List[typing.Callable[[ast.Node], typing.Optional[ast.Node]]] = [],
) -> ast.Node:
    def traverse_impl(tree: ast.Node) -> ast.Node:
        ret: typing.Optional[ast.Node] = None  # for the typecheck
        for pre_f in pre_order:
            ret = pre_f(tree)
            if ret is not None:
                tree = ret

        d = attr.asdict(tree, recurse=False)
        for k, v in d.items():
            if isinstance(v, list):
                for i, e in enumerate(v):
                    if isinstance(e, ast.Node):
                        ret = traverse_impl(e)
                        if ret is not None:
                            v[i] = ret
            elif isinstance(v, ast.Node):
                ret = traverse_impl(v)
                if ret is not None:
                    d[k] = ret

        tree = attr.evolve(tree, **d)

        for post_f in post_order:
            ret = post_f(tree)
            if ret is not None:
                tree = ret
        return tree

    return traverse_impl(root)
