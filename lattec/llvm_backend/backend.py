import typing
import collections
from .. import quads as Q


def generate_function(f: Q.Function) -> typing.List[str]:
    # TODO: occurence count for multi-assignment
    # TODO: types
    var_occ: typing.Dict[str, int] = collections.defaultdict(int)
    lvar_c = 0
    mem_vars: typing.Dict[str, Q.Var] = {}

    for q in f.body:
        if isinstance(q, Q.Call) and q.target is not None:
            var_occ[q.target.name] += 1

    ret: typing.List[str] = []
    ret.append(f"def <type> @{f.name}({', '.join(p.name for p in f.params)}) ""{")
    for q in f.body:
        if isinstance(q, Q.Declaration):
            ret.append(f"    #{q.var}: {q.var.type}")

        if isinstance(q, Q.Label):
            ret.append(f"{q.name}:")

        if isinstance(q, Q.Call):
            # TODO: proper builtins
            if q.target is None:
                ret.append(f"    {q.function}({', '.join(str(e) for e in q.params)})")
            else:
                tgt: Q.Var
                tgt_name = q.target.name
                cnt = var_occ[tgt_name]
                if cnt == 1:
                    tgt = q.target
                else:
                    if cnt > 1:
                        new_lvar = Q.new_var(Q.Ptr(Q.I32()))  # TODO: type
                        lvar_c += 1
                        ret.append(f"    {new_lvar} = alloca")
                        mem_vars[tgt_name] = new_lvar
                        var_occ[q.target.name] = 0
                    # get mem
                    tgt = q.target

                ret.append(f"    {tgt} = {q.function}({', '.join(str(e) for e in q.params)})")

        if isinstance(q, Q.CondBranch):
            ret.append(f"    br {q.cond}, {q.target_true}, {q.target_false}")

        if isinstance(q, Q.Branch):
            ret.append(f"    br {q.target}")

        if isinstance(q, Q.Return):
            ret.append(f"    ret {str(q.val) if q.val else ''}")

    ret.append("}")
    ret.append("")
    return ret


def generate_llvm(funcs: typing.List[Q.Function]) -> None:
    for f in funcs:
        for l in generate_function(f):
            pass
            print(l)
