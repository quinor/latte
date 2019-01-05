import typing
from collections import defaultdict
from .. import ast, prelude
from . import quads


var_decls: typing.Dict[str, typing.List[quads.Var]] = defaultdict(list)
scope_stack: typing.List[typing.List[str]] = []


def infer_scopes_pre(node: ast.Node) -> None:
    if isinstance(node, (ast.Block, ast.FunctionDeclaration)):
        scope_stack.append([])

    if isinstance(node, ast.Declaration):
        var_decls[node.var.var].append(quads.new_var())
        scope_stack[-1].append(node.var.var)

    if isinstance(node, ast.Program):
        for v, _ in prelude.prelude_types:
            var_decls[v].append(v)
        for fn in node.decls:
            var_decls[fn.name].append(fn.name)


def infer_scopes_post(node: ast.Node) -> None:
    if isinstance(node, (ast.Block, ast.FunctionDeclaration)):
        for v in scope_stack.pop():
            var_decls[v].pop()


def clear() -> None:
    var_decls.clear()
    scope_stack.clear()
