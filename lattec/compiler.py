import os
from . import parser, analyzer, errors


def compile(filename, outname=None, silent=False):
    assert filename[-4:] == ".lat"
    filename = os.path.expanduser(filename)
    # basename = filename[:-4]

    code = open(filename, "r").read().replace("\t", "    ")
    prog = parser.program_parser(code)
    if errors.errors():
        print("ERROR")
        if not silent:
            errors.print_errors(code)
        exit(-1)
    analyzer.analyze_types(prog)
    if errors.errors():
        print("ERROR")
        if not silent:
            errors.print_errors(code)
        exit(-2)
    print("OK")
    exit(0)
