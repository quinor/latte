import typing
import attr
import collections
from .. import quads as Q


@attr.s(auto_attribs=True)
class Block:
    body: typing.List[Q.Quad]
    occ_cnt: int


def divide(l: typing.List[Q.Quad]) -> typing.Tuple[bool, typing.List[Q.Quad]]:
    dirty = False

    blocks: typing.Dict[str, Block] = collections.OrderedDict()
    cur_name = ""
    cold = False
    for q in l:
        if isinstance(q, Q.Label):
            cur_name = q.name
            blocks[cur_name] = Block([], 0)
            cold = False

        if cold:
            dirty = True
            continue

        if isinstance(q, (Q.Return, Q.Branch, Q.CondBranch)):
            cold = True

        blocks[cur_name].body.append(q)

    blocks["entry"].occ_cnt += 1  # function always starts

    for q in l:
        if isinstance(q, Q.Branch):
            blocks[q.target.name].occ_cnt += 1
        if isinstance(q, Q.CondBranch):
            blocks[q.target_true.name].occ_cnt += 1
            blocks[q.target_false.name].occ_cnt += 1

    ret: typing.List[Q.Quad] = []
    for _, bl in blocks.items():
        if bl.occ_cnt > 0:
            ret.extend(bl.body)
        else:
            dirty = True

    return dirty, ret


def prune(f: Q.Function) -> Q.Function:
    body = f.body
    dirty = True
    while dirty:
        dirty, body = divide(body)
    return attr.evolve(f, body=body)


def pruning(p: Q.Program) -> Q.Program:
    return list(map(prune, p))
