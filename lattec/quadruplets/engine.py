from .. import ast, traverse
from . import generator, scopes, quads


def quadruplet_generation(tree: ast.Program) -> None:
    quads.clear()
    traverse.traverse(
        tree,
        pre_order=[
            scopes.infer_scopes_pre,
        ],
        post_order=[
            generator.gen_quads_post,
            scopes.infer_scopes_post,
        ]
    )
    ret = None
    # assert isinstance(ret, ast.Program)
    return ret
