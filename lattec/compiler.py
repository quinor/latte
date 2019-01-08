import os
from . import parser, analyzer, quadruplets, errors, config, llvm_backend, colors


def compile() -> None:
    filename = config.cfg["input"]
    outname = config.cfg["output"]
    assert filename[-4:] == ".lat"
    filename = os.path.expanduser(filename)
    basename = filename[:-4]
    llfile = f"{basename}.ll"
    outfile = outname or f"{basename}.bc"

    code = open(filename, "r").read().replace("\t", "    ")
    steps = [
        parser.program_parser,
        analyzer.type_analysis,
        analyzer.static_analysis,
        quadruplets.quadruplet_generation,
        quadruplets.assignment_elimination_mem,
        quadruplets.pruning,
        llvm_backend.generate_llvm,
    ]
    prog = code
    for no, step in enumerate(steps):
        prog = step(prog)  # type: ignore
        if errors.errors():
            print(colors.red("ERROR"))
            if not config.cfg["silent"]:
                errors.print_errors(code)
            exit(-1-no)

    print(colors.green("OK"))
    open(llfile, "w").write(prog)
    os.system(f"llvm-as {llfile} -o {outfile}")
    if config.cfg["mrjp_testing"]:
        os.system(f"lli {outfile} >tmp.out")
        os.system(f"diff -q tmp.out {basename}.output")
        os.system(f"rm tmp.out")
