import typing
import attr
from .. import ast, prelude, errors
from ..ast import undef_t
from .scopes import var_decls
from . import scopes
from .. import config


def expr_post(expr: ast.Expression) -> typing.Optional[ast.Expression]:
    if isinstance(expr, ast.IConstant):
        expr.attrs.type = ast.Int()

    if isinstance(expr, ast.BConstant):
        expr.attrs.type = ast.Bool()

    if isinstance(expr, ast.SConstant):
        expr.attrs.type = ast.String()

    if isinstance(expr, ast.Variable):
        if len(var_decls[expr.var]) == 0:
            errors.add_error(errors.Error(
                expr.start,
                expr.end,
                errors.TypeAnalysisKind.VariableDoesNotExist,
                f"variable {expr.var} does not exist in this scope.",
            ))
            expr.attrs.type = undef_t
        else:
            expr.attrs.type = var_decls[expr.var][-1].type

    if isinstance(expr, ast.Application):
        fn_t = expr.function.attrs.type

        # silence poison chain if function is of undefined type
        if fn_t == undef_t:
            expr.attrs.type = undef_t

        elif isinstance(fn_t, ast.Function):
            expr.attrs.type = fn_t.ret

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
                    expected != actual.attrs.type
                    and not isinstance(actual.attrs.type, ast.UndefinedType)
                ):
                    errors.add_error(errors.Error(
                        actual.start,
                        actual.end,
                        errors.TypeAnalysisKind.ArgumentTypeMismatch,
                        f"The actual type of a function argument {actual.attrs.type} does not "
                        f"agree with expected type {expected}.",
                    ))

        # special workaround for polymorphic operators
        elif isinstance(fn_t, ast.TypeAlternative):
            expr.attrs.type = ast.undef_t
            for subtype in fn_t.alt:
                assert isinstance(subtype, ast.Function)
                if len(subtype.params) != len(expr.args):
                    continue
                if any(
                    expected != actual.attrs.type
                    for expected, actual in zip(subtype.params, expr.args)
                ):
                    continue
                expr.attrs.type = subtype.ret
                expr.function.attrs.type = subtype
                poly_t = subtype.params[0]
                if isinstance(poly_t, ast.Int):
                    t_name = "int"
                if isinstance(poly_t, ast.String):
                    t_name = "string"
                if isinstance(poly_t, ast.Bool):
                    t_name = "bool"
                return attr.evolve(
                    expr,
                    function=attr.evolve(
                        expr.function,
                        var=expr.function.var+"_"+t_name
                    )
                )
            if expr.attrs.type == ast.undef_t:
                    errors.add_error(errors.Error(
                        expr.start,
                        expr.end,
                        errors.TypeAnalysisKind.FunctionCallMismatch,
                        f"Could not match overloaded function call with encountered expression. "
                        f"Possible function types are: {'; '.join(str(e) for e in fn_t.alt)}. "
                        f"Encountered argument types are: "
                        f"({', '.join(str(e.attrs.type) for e in expr.args)})",
                    ))

        # if the function isn't well-formed at all
        else:
            errors.add_error(errors.Error(
                expr.function.start,
                expr.function.end,
                errors.TypeAnalysisKind.FunctionNotCallable,
                f"This object of type {fn_t} is not callable.",
            ))
            expr.attrs.type = undef_t
    return None


def stmt_post(stmt: ast.Statement) -> typing.Optional[ast.Statement]:

    if isinstance(stmt, ast.Declaration):
        if len(var_decls[stmt.var.var]) > 0:
            # redeclaration
            if stmt.var.var in scopes.scope_stack[-1]:
                errors.add_error(errors.Error(
                    stmt.start,
                    stmt.end,
                    errors.TypeAnalysisKind.VariableRedeclaration,
                    f"This variable has been declared before in this scope. Previous "
                    f"declaration at {var_decls[stmt.var.var][-1].start}.",
                ))
            # shadow
            elif config.cfg["wshadow"]:
                errors.add_error(errors.Error(
                    stmt.start,
                    stmt.end,
                    errors.TypeAnalysisKind.VariableShadow,
                    f"This variable declaration shadows previously declared variable. Previous "
                    f"declaration at {var_decls[stmt.var.var][-1].start}.",
                ))

    if isinstance(stmt, ast.Assignment):
        tv = stmt.var.attrs.type
        te = stmt.expr.attrs.type
        if tv != undef_t and te != undef_t and tv != te:
            errors.add_error(errors.Error(
                stmt.start,
                stmt.end,
                errors.TypeAnalysisKind.AssignmentTypeMismatch,
                f"The type of the variable {stmt.var.var} ({tv}) does not "
                f"agree with the type of the expression ({te}).",
            ))

    if isinstance(stmt, ast.Return):
        te = stmt.val
        ret_t = var_decls["return"][-1].type
        if te is not None:
            if te.attrs.type != undef_t and isinstance(te.attrs.type, ast.Void):
                errors.add_error(errors.Error(
                    stmt.start,
                    stmt.end,
                    errors.TypeAnalysisKind.ReturnTypeMismatch,
                    f"Return of type {te.attrs.type} with value is not permitted",
                ))
            if te.attrs.type != undef_t and ret_t != te.attrs.type:
                errors.add_error(errors.Error(
                    stmt.start,
                    stmt.end,
                    errors.TypeAnalysisKind.ReturnTypeMismatch,
                    f"The type of the function return {ret_t} does not match with the type of the "
                    f"expression: {te.attrs.type}.",
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
        cond_t = stmt.cond.attrs.type
        if cond_t != undef_t and cond_t != ast.Bool():
                errors.add_error(errors.Error(
                    stmt.cond.start,
                    stmt.cond.end,
                    errors.TypeAnalysisKind.ConditionTypeMismatch,
                    f"This conditional value should be of type {ast.Bool()}, not {cond_t}.",
                ))
    return None


def tld_pre(tld: ast.Node) -> None:
    if isinstance(tld, ast.FunctionDeclaration):
        d: dict = {}
        for param in tld.params:
            if isinstance(param.type, ast.Void):
                errors.add_error(errors.Error(
                    param.start,
                    param.end,
                    errors.TypeAnalysisKind.FunctionVoidParameter,
                    f"This function parameter is of forbidden type {ast.Void}.",
                ))

            if param.var.var in d:
                errors.add_error(errors.Error(
                    param.start,
                    param.end,
                    errors.TypeAnalysisKind.FunctionSameParameter,
                    f"This function already has got another parameter with name {param.var.var}.",
                ))
            else:
                d[param.var.var] = param

    if isinstance(tld, ast.Program):
        for v, t in prelude.prelude_types:
            var_decls[v].append(ast.decl_from_var_type(ast.Variable(var=v), t))
        for fn in tld.decls:
            if len(var_decls[fn.name]) > 0:
                errors.add_error(errors.Error(
                    fn.start,
                    fn.end,
                    errors.TypeAnalysisKind.MultipleFunctionDefinitions,
                    f"Function with this name has been already declared. Previous definition at "
                    f"{var_decls[fn.name][-1].start}.",
                ))
            var_decls[fn.name].append(ast.decl_from_var_type(
                ast.Variable(start=fn.start, end=fn.end, var=fn.name), fn.type))


def tld_post(tld: ast.Node) -> typing.Optional[ast.Node]:
    if isinstance(tld, ast.Program):
        if "main" not in var_decls:
            errors.add_error(errors.Error(
                None,
                None,
                errors.TypeAnalysisKind.NoMain,
                f"Main function does not exist.",
            ))
        elif var_decls["main"][-1].type != ast.Function(params=[], ret=ast.Int()):
            main = var_decls["main"][-1]
            main_expected_t = ast.Function(params=[], ret=ast.Int())
            errors.add_error(errors.Error(
                main.start,
                main.end,
                errors.TypeAnalysisKind.NoMain,
                f"Main function type mismatch. Should be {main_expected_t}, is {main.type}.",
            ))
    return None


def infer_types_pre(node: ast.Node) -> None:
    tld_pre(node)


def infer_types_post(node: ast.Node) -> typing.Optional[ast.Node]:
    if isinstance(node, ast.Expression):
        return expr_post(node)
    if isinstance(node, ast.Statement):
        return stmt_post(node)
    return tld_post(node)
