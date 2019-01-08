import collections
import typing
import attr
from .. import quads as Q


def mem_var(v: Q.Var) -> typing.Callable[[], Q.Var]:
    def impl_mv():
        assert isinstance(v.type, Q.Ptr)
        tgt = Q.new_var(v.type.type)
        Q.add_quad(Q.Load(tgt, v))
        return tgt
    return impl_mv


def just_val(v: Q.Val) -> typing.Callable[[], Q.Val]:
    def impl_jv():
        return v
    return impl_jv


def eliminate_fn(f: Q.Function) -> Q.Function:
    var_occ_count: typing.Dict[Q.Var, int] = collections.defaultdict(int)
    var_aliases: typing.Dict[Q.Var, typing.Callable[[], Q.Val]] = {}

    def A(v: Q.Val) -> Q.Val:
        if isinstance(v, Q.Var) and v in var_aliases:
            return var_aliases[v]()
        else:
            return v

    def sub_vars(q: Q.Quad) -> Q.Quad:
        if isinstance(q, Q.Call):
            return Q.Call(q.target, A(q.function), list(map(A, q.params)))
        if isinstance(q, Q.CondBranch):
            return Q.CondBranch(A(q.cond), q.target_true, q.target_false)
        if isinstance(q, Q.Return):
            return Q.Return(A(q.val) if q.val is not None else None)
        return q

    for q in f.body:
        if isinstance(q, Q.Assign):
            var_occ_count[q.target] += 1

    Q.add_quad(Q.Label("entry"))

    for q in f.body:
        if isinstance(q, Q.Assign):
            if var_occ_count[q.target] > 1:
                var_occ_count[q.target] = -1

                tgt = attr.evolve(q.target, type=Q.Ptr(q.target.type))
                Q.add_quad(Q.Alloc(tgt))
                var_aliases[q.target] = mem_var(tgt)

            if var_occ_count[q.target] == 1:
                var_occ_count.pop(q.target)

    for q in f.body:
        if isinstance(q, Q.Assign):
            if q.target in var_occ_count:
                tgt = attr.evolve(q.target, type=Q.Ptr(q.target.type))
                Q.add_quad(Q.Store(A(q.source), tgt))
            else:
                var_aliases[q.target] = just_val(A(q.source))
        else:
            Q.add_quad(sub_vars(q))
    return attr.evolve(f, body=Q.gather())


def assignment_elimination_mem(p: Q.Program) -> Q.Program:
    return list(map(eliminate_fn, p))
