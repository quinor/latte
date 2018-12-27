from . import scopes, typecheck, traverse, returns, constexprs
from .. import ast


def type_analysis(tree: ast.Program) -> ast.Program:
    scopes.clear()
    ret = traverse.traverse(
        tree,
        pre_order=[
            scopes.infer_scopes_pre,
            typecheck.infer_types_pre,
        ],
        post_order=[
            typecheck.infer_types_post,
            scopes.infer_scopes_post,
        ]
    )
    assert isinstance(ret, ast.Program)
    return ret


def static_analysis(tree: ast.Program) -> ast.Program:
    scopes.clear()
    ret = traverse.traverse(
        tree,
        pre_order=[
        ],
        post_order=[
            constexprs.fold_constexprs_post,
            returns.check_returns_post,
        ]
    )
    assert isinstance(ret, ast.Program)
    return ret
