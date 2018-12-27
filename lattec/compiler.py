import os
from . import parser, analyzer, errors, config


def compile() -> None:
    filename = config.cfg["input"]
    # outname = config.cfg["output"]
    assert filename[-4:] == ".lat"
    filename = os.path.expanduser(filename)
    # basename = filename[:-4]

    code = open(filename, "r").read().replace("\t", "    ")
    steps = [
        parser.program_parser,
        analyzer.type_analysis,
        analyzer.static_analysis,
    ]
    prog = code
    for no, step in enumerate(steps):
        prog = step(prog)  # type: ignore
        if errors.errors():
            print("ERROR")
            if not config.cfg["silent"]:
                errors.print_errors(code)
            exit(-1-no)
    print("OK")
    exit(0)
