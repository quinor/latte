import typing
import collections
from .. import quads as Q
from . import resources


arithm_suf_map = {
    "add_int": "add",
    "sub": "sub",
    "mul": "mul",
    "div": "sdiv",
    "mod": "srem",
}

cmp_suf_map = {
    "le": "sle",
    "lt": "slt",
    "ge": "sge",
    "gt": "sgt",
    "eq_int": "eq",
    "ne_int": "ne",
    "eq_bool": "eq",
    "ne_bool": "ne",
}


def generate_function(f: Q.Function) -> typing.List[str]:
    var_occ: typing.Dict[str, int] = collections.defaultdict(int)

    for q in f.body:
        if isinstance(q, Q.Call) and q.target is not None:
            var_occ[q.target.name] += 1

    ret: typing.List[str] = []
    ret.append(f"define {f.ret} @{f.name}({', '.join(f'{p.type} {p}' for p in f.params)}) ""{")
    for q in f.body:
        if isinstance(q, Q.Label):
            ret.append(f"{q.name}:")

        if isinstance(q, Q.Call):
            assert isinstance(q.function, (Q.Var, Q.GlobalVar))
            assert isinstance(q.function.type, Q.FunctionPtr)
            fname = q.function.name
            bltn = fname.startswith("__builtin__")
            suffix = fname[len("__builtin__"):]
            rtype = q.function.type.ret
            tgt = (
                ""
                if q.target is None or isinstance(q.function.type.ret, Q.Void)else
                f"{q.target} = "
            )

            if bltn and suffix == "unary_minus":
                ret.append(f"    {tgt}sub {rtype} 0, {q.params[0]}")

            elif bltn and suffix == "unary_not":
                ret.append(f"    {tgt}sub {rtype} 1, {q.params[0]}")

            elif bltn and suffix in arithm_suf_map:
                op = arithm_suf_map[suffix]
                ret.append(f"    {tgt}{op} {rtype} {q.params[0]}, {q.params[1]}")

            elif bltn and suffix in cmp_suf_map:
                op = cmp_suf_map[suffix]
                ret.append(f"    {tgt}icmp {op} {q.params[0].type} {q.params[0]}, {q.params[1]}")

            else:
                assert isinstance(q.function.type, Q.FunctionPtr)
                ret.append(
                    f"    {tgt}call {q.function.type.ret} {q.function}"
                    f"({', '.join(f'{e.type} {e}' for e in q.params)})"
                )

        if isinstance(q, Q.CondBranch):
            ret.append(f"    br i1 {q.cond}, label {q.target_true}, label {q.target_false}")

        if isinstance(q, Q.Branch):
            ret.append(f"    br label {q.target}")

        if isinstance(q, Q.Return):
            if q.val:
                ret.append(f"    ret {q.val.type} {q.val}")
            else:
                ret.append(f"    ret void")

        if isinstance(q, Q.Assign):
            raise Exception("It should not be there!")

        if isinstance(q, Q.Alloc):
            assert isinstance(q.target.type, Q.Ptr)
            ret.append(f"    {q.target} = alloca {q.target.type.type}")

        if isinstance(q, Q.Load):
            ret.append(f"    {q.target} = load {q.target.type}, {q.source.type} {q.source}")

        if isinstance(q, Q.Store):
            ret.append(f"    store {q.source.type} {q.source}, {q.target.type} {q.target}")

    ret.append("}")
    ret.append("")
    return ret


def generate_llvm(funcs: Q.Program) -> str:
    code = resources.LLVM_RUNTIME
    code += "\n".join(l for f in funcs for l in generate_function(f))
    code += "\n"+"\n".join(Q.get_string_consts())
    return code
