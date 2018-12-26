from .traverse import traverse
from .. import ast
from ..ast import undef_t
from .. import errors
import typing
from collections import defaultdict


unary_bool = ast.Function(params=[ast.Bool()], ret=ast.Bool())
unary_int = ast.Function(params=[ast.Int()], ret=ast.Int())
binary_bool = ast.Function(params=[ast.Bool(), ast.Bool()], ret=ast.Bool())
binary_int = ast.Function(params=[ast.Int(), ast.Int()], ret=ast.Int())
binary_int_bool = ast.Function(params=[ast.Int(), ast.Int()], ret=ast.Bool())
binary_string_bool = ast.Function(params=[ast.String(), ast.String()], ret=ast.Bool())
binray_string = ast.Function(params=[ast.String(), ast.String()], ret=ast.String())

prelude_types = [
    ("printInt", ast.Function(params=[ast.Int()], ret=ast.Void())),
    ("printString", ast.Function(params=[ast.String()], ret=ast.Void())),
    ("error", ast.Function(params=[], ret=ast.Void())),
    ("readInt", ast.Function(params=[], ret=ast.Int())),
    ("readString", ast.Function(params=[], ret=ast.String())),
    ("__builtin__unary_minus", unary_int),
    ("__builtin__unary_not", unary_bool),
    ("__builtin__mod", binary_int),
    ("__builtin__mul", binary_int),
    ("__builtin__div", binary_int),
    ("__builtin__add", ast.TypeAlternative(alt=[binary_int, binray_string])),
    ("__builtin__sub", binary_int),
    ("__builtin__le", binary_int_bool),
    ("__builtin__lt", binary_int_bool),
    ("__builtin__ge", binary_int_bool),
    ("__builtin__gt", binary_int_bool),
    ("__builtin__eq", ast.TypeAlternative(alt=[binary_int_bool, binary_string_bool, binary_bool])),
    ("__builtin__ne", ast.TypeAlternative(alt=[binary_int_bool, binary_string_bool, binary_bool])),
    ("__builtin__and", binary_bool),
    ("__builtin__or", binary_bool),
]


var_types: typing.Dict[str, typing.List[ast.Declaration]] = defaultdict(list)
scope_stack: typing.List[typing.List[str]] = []


def infer_expr(expr: ast.Expression) -> None:
    if isinstance(expr, ast.IConstant):
        expr.attrs["type"] = ast.Int()

    if isinstance(expr, ast.BConstant):
        expr.attrs["type"] = ast.Bool()

    if isinstance(expr, ast.SConstant):
        expr.attrs["type"] = ast.String()

    if isinstance(expr, ast.Variable):
        if len(var_types[expr.var]) == 0:
            errors.add_error(errors.Error(
                expr.start,
                expr.end,
                errors.TypeAnalysisKind.VariableDoesNotExist,
                f"variable {expr.var} does not exist in this scope.",
            ))
            expr.attrs["type"] = undef_t
        else:
            expr.attrs["type"] = var_types[expr.var][-1].type
            expr.attrs["source"] = var_types[expr.var][-1]

    if isinstance(expr, ast.Application):
        fn_t = expr.function.attrs["type"]

        # silence poison chain if function is of undefined type
        if fn_t == undef_t:
            expr.attrs["type"] = undef_t

        elif isinstance(fn_t, ast.Function):
            expr.attrs["type"] = fn_t.ret

            # number of arguments check
            if len(fn_t.params) != len(expr.args):
                errors.add_error(errors.Error(
                    expr.start,
                    expr.end,
                    errors.TypeAnalysisKind.IncorrectArgumentCount,
                    f"There are {len(expr.args)} arguments in the function call, "
                    f"should be {len(fn_t.params)}.",
                ))

            # consecutive arguments check, ignore undefineds, they were already reported
            for expected, actual in zip(fn_t.params, expr.args):
                if (
                    expected != actual.attrs["type"]
                    and not isinstance(actual.attrs["type"], ast.UndefinedType)
                ):
                    errors.add_error(errors.Error(
                        actual.start,
                        actual.end,
                        errors.TypeAnalysisKind.ArgumentTypeMismatch,
                        f"The actual type of a function argument {actual.attrs['type']} does not "
                        f"agree with expected type {expected}.",
                    ))

        # special workaround for polymorphic operators, TODO proper implementation?
        elif isinstance(fn_t, ast.TypeAlternative):
            expr.attrs["type"] = ast.undef_t
            for subtype in fn_t.alt:
                assert isinstance(subtype, ast.Function)
                if len(subtype.params) != len(expr.args):
                    continue
                if any(
                    expected != actual.attrs["type"]
                    for expected, actual in zip(subtype.params, expr.args)
                ):
                    continue
                expr.attrs["type"] = subtype.ret
                expr.function.attrs["type"] = subtype
                break
            if expr.attrs["type"] == ast.undef_t:
                    errors.add_error(errors.Error(
                        expr.start,
                        expr.end,
                        errors.TypeAnalysisKind.FunctionCallMismatch,
                        f"Could not match overloaded function call with encountered expression. "
                        f"Possible function types are: {'; '.join(str(e) for e in fn_t.alt)}. "
                        f"Encountered argument types are: "
                        f"({', '.join(str(e.attrs['type']) for e in expr.args)})",
                    ))

        # if the function isn't well-formed at all
        else:
            errors.add_error(errors.Error(
                expr.function.start,
                expr.function.end,
                errors.TypeAnalysisKind.FunctionNotCallable,
                f"This object of type {fn_t} is not callable.",
            ))
            expr.attrs["type"] = undef_t


def infer_stmt_pre(stmt: ast.Statement) -> None:
    if isinstance(stmt, ast.Block):
        scope_stack.append([])


def infer_stmt_post(stmt: ast.Statement) -> None:
    if isinstance(stmt, ast.Block):
        stmt.attrs["returns"] = any(e.attrs["returns"] for e in stmt.statements)
        for i, e in enumerate(stmt.statements):
            if i != len(stmt.statements)-1 and e.attrs["returns"]:
                next_st = stmt.statements[i+1]
                errors.add_error(errors.Error(
                    next_st.start,
                    next_st.end,
                    errors.TypeAnalysisKind.DeadCode,
                    f"This statement (and all of the following statements in this block) are "
                    f"unreachable",
                ))
        for v in scope_stack.pop():
            var_types[v].pop()

    if isinstance(stmt, ast.FreeExpression):
        stmt.attrs["returns"] = False
        pass  # TODO: unused

    if isinstance(stmt, ast.Declaration):
        stmt.attrs["returns"] = False
        if len(var_types[stmt.var.var]) > 0:
            errors.add_error(errors.Error(
                stmt.start,
                stmt.end,
                errors.TypeAnalysisKind.VariableShadow,
                f"This variable declaration shadows previously declared variable. Previous "
                f"declaration at {var_types[stmt.var.var][-1].start}.",
            ))
        var_types[stmt.var.var].append(stmt)
        scope_stack[-1].append(stmt.var.var)

    if isinstance(stmt, ast.Assignment):
        stmt.attrs["returns"] = False
        tv = stmt.var.attrs["type"]
        te = stmt.expr.attrs["type"]
        if tv != undef_t and te != undef_t and tv != te:
            errors.add_error(errors.Error(
                stmt.start,
                stmt.end,
                errors.TypeAnalysisKind.AssignmentTypeMismatch,
                f"The type of the variable {stmt.var.var} ({tv}) does not "
                f"agree with the type of the expression ({te}).",
            ))

    if isinstance(stmt, ast.Return):
        stmt.attrs["returns"] = True
        te = stmt.val
        ret_t = var_types["return"][-1].type
        if te is not None:
            if te.attrs["type"] != undef_t and ret_t != te.attrs["type"]:
                errors.add_error(errors.Error(
                    stmt.start,
                    stmt.end,
                    errors.TypeAnalysisKind.ReturnTypeMismatch,
                    f"The type of the function return {ret_t} does not match with the type of the "
                    f"expressiom: {te.attrs['type']}.",
                ))
        else:
            if ret_t != ast.Void():
                errors.add_error(errors.Error(
                    stmt.start,
                    stmt.end,
                    errors.TypeAnalysisKind.ReturnTypeMismatch,
                    f"Return value should exist and be of type {ret_t}.",
                ))

    if isinstance(stmt, ast.If) or isinstance(stmt, ast.While):
        cond_t = stmt.cond.attrs["type"]
        if cond_t != undef_t and cond_t != ast.Bool():
                errors.add_error(errors.Error(
                    stmt.cond.start,
                    stmt.cond.end,
                    errors.TypeAnalysisKind.ConditionTypeMismatch,
                    f"This conditional value should be of type {ast.Bool()}, not {cond_t}.",
                ))

    if isinstance(stmt, ast.If):
        stmt.attrs["returns"] = (
            stmt.then_branch.attrs["returns"]
            and stmt.else_branch is not None
            and stmt.else_branch.attrs["returns"]
        )

    if isinstance(stmt, ast.While):
        stmt.attrs["returns"] = False


def infer_tld_pre(tld: ast.Node) -> None:
    if isinstance(tld, ast.FunctionDeclaration):
        d: dict = {}
        for param in tld.params:
            if param.var.var in d:
                errors.add_error(errors.Error(
                    param.start,
                    param.end,
                    errors.TypeAnalysisKind.FunctionSameParameter,
                    f"This function already has got another parameter with name {param.var}.",
                ))
            else:
                d[param.var.var] = param
        scope_stack.append([])
        assert isinstance(tld.type, ast.Function)
        fn_t = tld.type
        scope_stack[-1].append("return")
        var_types["return"].append(ast.decl_from_var_type(ast.Variable(var="return"), fn_t.ret))

    if isinstance(tld, ast.Program):
        for v, t in prelude_types:
            var_types[v].append(ast.decl_from_var_type(ast.Variable(var=v), t))
        for fn in tld.decls:
            var_types[fn.name].append(ast.decl_from_var_type(ast.Variable(var=fn.name), fn.type))


def infer_tld_post(tld: ast.Node) -> None:
    if isinstance(tld, ast.FunctionDeclaration):
        for v in scope_stack.pop():
            var_types[v].pop()
        assert isinstance(tld.type, ast.Function)
        if not tld.body.attrs["returns"] and tld.type.ret != ast.Void():
            errors.add_error(errors.Error(
                tld.start,
                tld.end,
                errors.TypeAnalysisKind.FunctionDoesNotReturn,
                f"There is a path in this function resulting in no return value.",
            ))


def infer_types_pre(node: ast.Node) -> None:
    if isinstance(node, ast.Expression):
        pass
    elif isinstance(node, ast.Statement):
        infer_stmt_pre(node)
    else:  # TLD
        infer_tld_pre(node)


def infer_types_post(node: ast.Node) -> None:
    if isinstance(node, ast.Expression):
        infer_expr(node)
    elif isinstance(node, ast.Statement):
        infer_stmt_post(node)
    else:  # TLD
        infer_tld_post(node)


def analyze_types(tree: ast.Program) -> None:
    var_types.clear()
    scope_stack.clear()
    traverse(tree, pre_order=infer_types_pre, post_order=infer_types_post)


# TODO: check compile-time consts (attr value in exprs, use in whiles and ifs for transformation)
# ^^^^^ move to separate file
# TODO: move return completeness check to a separate file
