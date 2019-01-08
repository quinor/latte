from .. import ast, traverse
from .. import quads as Q
from . import generator, scopes


def quadruplet_generation(tree: ast.Program) -> Q.Program:
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
    return tree.attrs.quad_gen()  # type: ignore
