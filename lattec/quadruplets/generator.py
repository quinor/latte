from .. import ast
from .scopes import var_decls
from . import quads


def nothing():
    pass


def gen_quads_post(node: ast.Node) -> None:
    # expressions
    if isinstance(node, ast.IConstant):
        def impl():
            return str(node.val)
        node.attrs["quad_gen"] = impl

    if isinstance(node, ast.BConstant):
        def impl():
            return str(int(node.val))
        node.attrs["quad_gen"] = impl

    if isinstance(node, ast.SConstant):
        def impl():
            return f"\"{node.val}\""
        node.attrs["quad_gen"] = impl

    if isinstance(node, ast.Variable):
        var = var_decls[node.var][-1]

        def impl():
            return str(var)
        node.attrs["quad_gen"] = impl

    if isinstance(node, ast.Application):
        # fn = node.function.var
        def impl():
            f_val = node.function.attrs["quad_gen"]()
            args_val = [e.attrs["quad_gen"]() for e in node.args]
            v = quads.new_var()
            quads.add_quad(f"    {v} = {f_val}({', '.join(args_val)})")
            return v
        node.attrs["quad_gen"] = impl

    # statements
    if isinstance(node, ast.Block):
        def impl():
            for e in node.statements:
                e.attrs["quad_gen"]()
        node.attrs["quad_gen"] = impl

    if isinstance(node, ast.FreeExpression):
        node.attrs["quad_gen"] = node.expr.attrs["quad_gen"]

    if isinstance(node, ast.Declaration):
        var = var_decls[node.var.var][-1]
        node.attrs["quad_gen"] = nothing

    if isinstance(node, ast.Assignment):
        var = var_decls[node.var.var][-1]

        def impl():
            val = node.expr.attrs["quad_gen"]()
            quads.add_quad(f"    {var} = {val}")
        node.attrs["quad_gen"] = impl

    if isinstance(node, ast.Return):
        def impl():
            if node.val is not None:
                quads.add_quad(f"    return {node.val.attrs['quad_gen']()}")
            else:
                quads.add_quad(f"    return")
        node.attrs["quad_gen"] = impl

    if isinstance(node, ast.If):
        def impl():
            cond = node.cond.attrs["quad_gen"]
            then_branch = node.then_branch.attrs["quad_gen"]
            if node.else_branch is not None:
                else_branch = node.else_branch.attrs["quad_gen"]
            else:
                else_branch = None

            then_lbl = quads.new_label()
            end_lbl = quads.new_label()
            else_lbl = quads.new_label() if else_branch else end_lbl

            cv = cond()
            quads.add_quad(f"    br {cv} {then_lbl} {else_lbl}")
            quads.add_quad(f"{then_lbl}:")
            then_branch()
            quads.add_quad(f"    br {end_lbl}")
            if else_branch:
                quads.add_quad(f"{else_lbl}:")
                else_branch()
                quads.add_quad(f"    br {end_lbl}")
            quads.add_quad(f"{end_lbl}:")

        node.attrs["quad_gen"] = impl

    if isinstance(node, ast.While):
        def impl():
            cond = node.cond.attrs["quad_gen"]
            body = node.body.attrs["quad_gen"]
            body_lbl = quads.new_label()
            cond_lbl = quads.new_label()
            end_lbl = quads.new_label()
            quads.add_quad(f"    br {cond_lbl}")
            quads.add_quad(f"{body_lbl}:")
            body()
            quads.add_quad(f"    br {cond_lbl}")
            quads.add_quad(f"{cond_lbl}:")
            cv = cond()
            quads.add_quad(f"    br {cv} {body_lbl} {end_lbl}")
            quads.add_quad(f"{end_lbl}:")

        node.attrs["quad_gen"] = impl

    # TLDs
    if isinstance(node, ast.FunctionDeclaration):
        params = [var_decls[e.var.var][-1] for e in node.params]

        def impl():
            quads.add_quad(f"def {node.name} ({', '.join(params)})" " {")
            node.body.attrs["quad_gen"]()
            quads.add_quad("}\n")

        node.attrs["quad_gen"] = impl
        # TEMP
        node.attrs["quad_gen"]()
        for l in quads.quads:
            print(l)
        quads.quads.clear()
