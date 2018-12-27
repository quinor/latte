import typing
from collections import defaultdict
from .. import ast


var_decls: typing.Dict[str, typing.List[ast.Declaration]] = defaultdict(list)
scope_stack: typing.List[typing.List[str]] = []


def infer_scopes_pre(node: ast.Node) -> None:
    if isinstance(node, ast.Block):
        scope_stack.append([])

    if isinstance(node, ast.FunctionDeclaration):
        scope_stack.append([])
        assert isinstance(node.type, ast.Function)
        fn_t = node.type
        scope_stack[-1].append("return")
        var_decls["return"].append(ast.decl_from_var_type(ast.Variable(var="return"), fn_t.ret))


def infer_scopes_post(node: ast.Node) -> None:
    if isinstance(node, (ast.Block, ast.FunctionDeclaration)):
        for v in scope_stack.pop():
            var_decls[v].pop()

    if isinstance(node, ast.Declaration):
        var_decls[node.var.var].append(node)
        scope_stack[-1].append(node.var.var)


def clear() -> None:
    var_decls.clear()
    scope_stack.clear()
