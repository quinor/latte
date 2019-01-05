from .. import ast
from .. import prelude


def expr_post(node: ast.Expression) -> ast.Expression:
    node.attrs.value = None

    if isinstance(node, (ast.IConstant, ast.BConstant, ast.SConstant)):
        node.attrs.value = node.val

    if isinstance(node, ast.Application):
        vals = [ch.attrs.value for ch in node.args]
        if all(e is not None for e in vals) and node.function.var in prelude.const_fn_impls:
            node.attrs.value = prelude.const_fn_impls[node.function.var](*vals)  # type: ignore

    if node.attrs.value is not None:
        if isinstance(node.attrs.type, ast.Int):
            return ast.IConstant(
                start=node.start,
                end=node.end,
                attrs=node.attrs,
                val=node.attrs.value,
            )
        if isinstance(node.attrs.type, ast.Bool):
            return ast.BConstant(
                start=node.start,
                end=node.end,
                attrs=node.attrs,
                val=node.attrs.value,
            )
        if isinstance(node.attrs.type, ast.String):
            return ast.SConstant(
                start=node.start,
                end=node.end,
                attrs=node.attrs,
                val=node.attrs.value,
            )
    return node


def stmt_post(node: ast.Statement) -> ast.Statement:
    if isinstance(node, ast.While):
        if node.cond.attrs.value is False:
            return ast.InlinedBlock(statements=[])

    if isinstance(node, ast.If):
        val = node.cond.attrs.value
        if val is not None:
            if val:
                return node.then_branch
            else:
                if node.else_branch:
                    return node.else_branch
                return ast.InlinedBlock(statements=[])

    return node


def fold_constexprs_post(node: ast.Node) -> ast.Node:
    if isinstance(node, ast.Expression):
        return expr_post(node)
    if isinstance(node, ast.Statement):
        return stmt_post(node)
    return node
