import typing
from collections import defaultdict
from .. import ast, prelude
from .. import quads as Q


var_decls: typing.Dict[str, typing.List[Q.Val]] = defaultdict(list)
scope_stack: typing.List[typing.List[str]] = []


def infer_scopes_pre(node: ast.Node) -> None:
    if isinstance(node, (ast.Block, ast.FunctionDeclaration)):
        scope_stack.append([])

    if isinstance(node, ast.Declaration):
        var_decls[node.var.var].append(Q.new_var(Q.from_ast_type(node.type)))
        scope_stack[-1].append(node.var.var)

    if isinstance(node, ast.Program):
        for v, t in prelude.prelude_types + [(e.name, e.type) for e in node.decls]:
            if isinstance(t, ast.TypeAlternative):
                pass  # we ignore the polymorphic ones - should be eliminated
            else:
                var_decls[v].append(Q.GlobalVar(Q.from_ast_type(t), v))


def infer_scopes_post(node: ast.Node) -> None:
    if isinstance(node, (ast.Block, ast.FunctionDeclaration)):
        for v in scope_stack.pop():
            var_decls[v].pop()


def clear() -> None:
    var_decls.clear()
    scope_stack.clear()
