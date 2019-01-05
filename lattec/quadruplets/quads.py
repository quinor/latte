import typing


Var = str


var_cnt: int = 0
label_cnt: int = 0


quads: typing.List[str] = []


def clear() -> None:
    global var_cnt
    global label_cnt
    var_cnt = 0
    label_cnt = 0
    quads.clear()


def new_var() -> Var:
    global var_cnt
    ret = f"v{var_cnt}"
    var_cnt += 1
    return ret


def new_label() -> Var:
    global label_cnt
    ret = f"L{label_cnt}"
    label_cnt += 1
    return ret


def add_quad(q: str) -> None:
    quads.append(q)
