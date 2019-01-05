from .. import ast, errors


def check_returns_pre(node: ast.Node) -> None:
    pass


def check_returns_post(node: ast.Node) -> None:
    if isinstance(node, ast.Statement):
        node.attrs.returns = False

    if isinstance(node, ast.Block):
        node.attrs.returns = any(e.attrs.returns for e in node.statements)
        for i, e in enumerate(node.statements):
            if i != len(node.statements)-1 and e.attrs.returns:
                next_st = node.statements[i+1]
                errors.add_error(errors.Error(
                    next_st.start,
                    next_st.end,
                    errors.TypeAnalysisKind.DeadCode,
                    f"This statement (and all of the following statements in this block) are "
                    f"unreachable",
                ))
                break

    if isinstance(node, ast.Return):
        node.attrs.returns = True

    if isinstance(node, ast.If):
        node.attrs.returns = (
            node.then_branch.attrs.returns
            and node.else_branch is not None
            and node.else_branch.attrs.returns
        )

    if isinstance(node, ast.FunctionDeclaration):
        assert isinstance(node.type, ast.Function)
        if not node.body.attrs.returns and node.type.ret != ast.Void():
            errors.add_error(errors.Error(
                node.start,
                node.end,
                errors.TypeAnalysisKind.FunctionDoesNotReturn,
                f"There is a path in this function resulting in no return value.",
            ))
