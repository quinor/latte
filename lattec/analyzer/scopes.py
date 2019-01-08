import typing
from collections import defaultdict
from .. import ast


var_decls: typing.Dict[str, typing.List[ast.Declaration]] = defaultdict(list)
scope_stack: typing.List[typing.List[str]] = []
ignore_stack: typing.List[typing.List[typing.Tuple[str, ast.Declaration]]] = []


def infer_scopes_pre(node: ast.Node) -> None:
    if isinstance(node, ast.Block):
        scope_stack.append([])

    if isinstance(node, ast.Expression):
        ignore = node.attrs.ignore_names
        if ignore is not None:
            ignore_stack.append([])
            for name in ignore:
                ignore_stack[-1].append((name, var_decls[name].pop()),)

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

    if isinstance(node, ast.Expression):
        if node.attrs.ignore_names is not None:
            for nm, vr in ignore_stack.pop():
                var_decls[nm].append(vr)

    if isinstance(node, ast.Declaration):
        var_decls[node.var.var].append(node)
        scope_stack[-1].append(node.var.var)


def clear() -> None:
    var_decls.clear()
    scope_stack.clear()
