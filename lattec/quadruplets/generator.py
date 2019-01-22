import typing
from .. import ast
from .scopes import var_decls
from .. import quads as Q


def gen_quads_post(node: ast.Node) -> None:
    # expressions
    if isinstance(node, ast.IConstant):
        def impl_e() -> Q.Val:
            assert isinstance(node, ast.IConstant)
            return Q.Constant(Q.I32(), node.val)
        node.attrs.quad_gen = impl_e

    if isinstance(node, ast.BConstant):
        def impl_e() -> Q.Val:
            assert isinstance(node, ast.BConstant)
            return Q.Constant(Q.I1(), node.val)
        node.attrs.quad_gen = impl_e

    if isinstance(node, ast.SConstant):
        def impl_e() -> Q.Val:
            assert isinstance(node, ast.SConstant)
            return Q.SConstant(Q.String(), node.val)
        node.attrs.quad_gen = impl_e

    if isinstance(node, ast.Variable):
        var = var_decls[node.var][-1]

        def impl_e() -> Q.Val:
            return var
        node.attrs.quad_gen = impl_e

    if isinstance(node, ast.Application):
        def impl_e() -> Q.Val:
            assert isinstance(node, ast.Application)
            f = node.function.attrs.quad_gen()
            if isinstance(f, Q.GlobalVar) and f.name in ["__builtin__and", "__builtin__or"]:
                fst = node.args[0].attrs.quad_gen
                snd = node.args[1].attrs.quad_gen
                half = Q.new_label()
                pos = Q.new_label()
                neg = Q.new_label()
                end = Q.new_label()
                fv = fst()

                if f.name == "__builtin__and":
                    Q.add_quad(Q.CondBranch(fv, half, neg))
                else:  # f.name == "__builtin__or"
                    Q.add_quad(Q.CondBranch(fv, pos, half))
                Q.add_quad(half)
                sv = snd()
                Q.add_quad(Q.CondBranch(sv, pos, neg))

                ft = node.function.attrs.type
                assert isinstance(ft, ast.Function)
                v = Q.new_var(Q.from_ast_type(ft.ret))

                Q.add_quad(pos)
                Q.add_quad(Q.Assign(v, Q.Constant(Q.I1(), 1)))
                Q.add_quad(Q.Branch(end))

                Q.add_quad(neg)
                Q.add_quad(Q.Assign(v, Q.Constant(Q.I1(), 0)))
                Q.add_quad(Q.Branch(end))

                Q.add_quad(end)

                return v
            else:
                args = [e.attrs.quad_gen() for e in node.args]
                ft = node.function.attrs.type
                assert isinstance(ft, ast.Function)
                v = Q.new_var(Q.from_ast_type(ft.ret))
                Q.add_quad(Q.Call(v, f, args))
                # defer string deletion
                if isinstance(v.type, Q.String):
                    Q.add_defer(Q.Call(
                        Q.new_var(Q.Void()),
                        Q.GlobalVar(
                            Q.FunctionPtr(Q.Void(), [Q.String()]),
                            "__builtin__delref_string"
                        ),
                        [v]
                    ))
                return v
        node.attrs.quad_gen = impl_e

    # statements
    if isinstance(node, ast.Block):
        def impl_s() -> None:
            assert isinstance(node, ast.Block)
            Q.open_defer_scope()
            for e in node.statements:
                e.attrs.quad_gen()
            for q in Q.close_defer_scope():
                Q.add_quad(q)
        node.attrs.quad_gen = impl_s

    if isinstance(node, ast.FreeExpression):
        node.attrs.quad_gen = node.expr.attrs.quad_gen

    if isinstance(node, ast.Declaration):
        var = var_decls[node.var.var][-1]

        def impl_s() -> None:
            pass
        node.attrs.quad_gen = impl_s

    if isinstance(node, ast.Assignment):
        var = var_decls[node.var.var][-1]

        def impl_s() -> None:
            assert isinstance(node, ast.Assignment)
            val = node.expr.attrs.quad_gen()
            assert isinstance(var, Q.Var)
            if isinstance(var.type, Q.String):
                # reusing an attr set for every first assignment
                if node.expr.attrs.ignore_names is None:
                    Q.add_quad(Q.Call(
                        Q.new_var(Q.Void()),
                        Q.GlobalVar(
                            Q.FunctionPtr(Q.Void(), [Q.String()]),
                            "__builtin__delref_string"
                        ),
                        [var]
                    ))
                else:
                    Q.add_defer(Q.Call(
                        Q.new_var(Q.Void()),
                        Q.GlobalVar(
                            Q.FunctionPtr(Q.Void(), [Q.String()]),
                            "__builtin__delref_string"
                        ),
                        [var]
                    ))

                Q.add_quad(Q.Call(
                    Q.new_var(Q.Void()),
                    Q.GlobalVar(
                        Q.FunctionPtr(Q.Void(), [Q.String()]),
                        "__builtin__addref_string"
                    ),
                    [val]
                ))
            Q.add_quad(Q.Assign(var, val))
        node.attrs.quad_gen = impl_s

    if isinstance(node, ast.Return):
        def impl_s() -> None:
            # defered calls when return happens
            assert isinstance(node, ast.Return)
            ret = None
            if node.val is not None:
                ret = node.val.attrs.quad_gen()
                # bump ref count on an object if returning a string
                if isinstance(ret.type, Q.String):
                    Q.add_quad(Q.Call(
                        Q.new_var(Q.Void()),
                        Q.GlobalVar(
                            Q.FunctionPtr(Q.Void(), [Q.String()]),
                            "__builtin__addref_string"
                        ),
                        [ret]
                    ))

            for q in sum(Q.defer_stack, []):
                Q.add_quad(q)
            Q.add_quad(Q.Return(ret))
        node.attrs.quad_gen = impl_s

    if isinstance(node, ast.If):
        def impl_s() -> None:
            assert isinstance(node, ast.If)
            cond = node.cond.attrs.quad_gen
            then_branch = node.then_branch.attrs.quad_gen
            if node.else_branch is not None:
                else_branch = node.else_branch.attrs.quad_gen
            else:
                else_branch = None

            then_lbl = Q.new_label()
            if else_branch:
                else_lbl = Q.new_label()
            end_lbl = Q.new_label()
            if not else_branch:
                else_lbl = end_lbl

            cv = cond()
            Q.add_quad(Q.CondBranch(cv, then_lbl, else_lbl))
            Q.add_quad(then_lbl)
            then_branch()
            Q.add_quad(Q.Branch(end_lbl))
            if else_branch:
                Q.add_quad(else_lbl)
                else_branch()
                Q.add_quad(Q.Branch(end_lbl))
            Q.add_quad(end_lbl)

        node.attrs.quad_gen = impl_s

    if isinstance(node, ast.While):
        def impl_s() -> None:
            assert isinstance(node, ast.While)
            cond = node.cond.attrs.quad_gen
            body = node.body.attrs.quad_gen
            body_lbl = Q.new_label()
            cond_lbl = Q.new_label()
            end_lbl = Q.new_label()
            Q.add_quad(Q.Branch(cond_lbl))
            Q.add_quad(body_lbl)
            body()
            Q.add_quad(Q.Branch(cond_lbl))
            Q.add_quad(cond_lbl)
            cv = cond()
            Q.add_quad(Q.CondBranch(cv, body_lbl, end_lbl))
            Q.add_quad(end_lbl)

        node.attrs.quad_gen = impl_s

    # TLDs
    if isinstance(node, ast.FunctionDeclaration):
        params: typing.List[Q.Var] = [
            var_decls[e.var.var][-1] for e in node.params]  # type: ignore

        def impl_t() -> Q.Function:
            assert isinstance(node, ast.FunctionDeclaration)
            assert isinstance(node.type, ast.Function)

            Q.open_defer_scope()

            head_params = [Q.new_var(p.type) for p in params]
            for p, hp in zip(params, head_params):
                Q.add_quad(Q.Assign(p, hp))
                if isinstance(p.type, Q.String):
                    Q.add_quad(Q.Call(
                        Q.new_var(Q.Void()),
                        Q.GlobalVar(
                            Q.FunctionPtr(Q.Void(), [Q.String()]),
                            "__builtin__addref_string"
                        ),
                        [p]
                    ))
                    Q.add_defer(Q.Call(
                        Q.new_var(Q.Void()),
                        Q.GlobalVar(
                            Q.FunctionPtr(Q.Void(), [Q.String()]),
                            "__builtin__delref_string"
                        ),
                        [p]
                    ))

            node.body.attrs.quad_gen()
            for q in Q.close_defer_scope():
                Q.add_quad(q)
            if isinstance(node.type.ret, ast.Void):
                Q.add_quad(Q.Return(None))
            body = Q.gather()
            assert isinstance(node.type, ast.Function)
            return Q.Function(  # type: ignore
                Q.from_ast_type(node.type.ret),
                node.name,
                head_params,
                body
            )

        node.attrs.quad_gen = impl_t

    if isinstance(node, ast.Program):
        def impl_p():
            assert isinstance(node, ast.Program)
            return [e.attrs.quad_gen() for e in node.decls]
        node.attrs.quad_gen = impl_p
