import sys
import argparse

class Config(object):
    input_file1 = None
    input_file2 = None
    inputlist = None
    outputlist = None

    def __init__(self):
        self.input_file1 = None
        self.input_file2 = None
        self.inputlist = None
        self.outputlist = None

usage = "Usage: %s smt2file-1 smt2file-2 \"in1, in2, ..., inn\" \"out1, out2, ..., outm\""%sys.argv[0]


def generate_equivalence_check(config):

    model_1 = ""
    with open(config.input_file1) as f:
        model_1 = f.read()

    model_2 = ""
    with open(config.input_file2) as f:
        model_2 = f.read()

        inps = config.inputlist.replace(" ", "").split(",")
        outs = config.outputlist.replace(" ", "").split(",")

    set_vals = []

    init_vars_1 = []
    curr_vars_1 = []
    next_vars_1 = []
    init_1 = []
    trans_1 = []
    variables_1 = []

    init_vars_2 = []
    curr_vars_2 = []
    next_vars_2 = []
    init_2 = []
    trans_2 = []
    variables_2 = []

    (set_vals, variables_1, init_vars_1, curr_vars_1, next_vars_1, init_1, trans_1) = parse_model(model_1)
    (set_vals, variables_2, init_vars_2, curr_vars_2, next_vars_2, init_2, trans_2) = parse_model(model_2)

    print("\n".join(set_vals))

    print("\n".join([x.replace(CURR, m_1("")+CURR) for x in curr_vars_1]))
    print("\n".join([x.replace(NEXT, m_1("")+NEXT) for x in next_vars_1]))
    print("\n".join([x.replace(CURR, m_1("")+CURR).replace(NEXT, m_1("")+NEXT) for x in trans_1]))

    print("\n".join([x.replace(CURR, m_2("")+CURR) for x in curr_vars_2]))
    print("\n".join([x.replace(NEXT, m_2("")+NEXT) for x in next_vars_2]))
    print("\n".join([x.replace(CURR, m_2("")+CURR).replace(NEXT, m_2("")+NEXT) for x in trans_2]))

    pre = []

    for inp in inps:
        pre.append("(= %s %s)"%(curr(m_1(inp)), curr(m_2(inp))))

    for ous in outs:
        pre.append("(= %s %s)"%(curr(m_1(ous)), curr(m_2(ous))))

    pos = []    
    for ous in outs:
        pos.append("(= %s %s)"%(next(m_1(ous)), next(m_2(ous))))


    precond = to_and(pre)
    poscond = to_and(pos)
    cond = "(and %s (not %s))"%(precond, poscond)

    print("(assert %s)"%cond)

    print("(check-sat)")

    return 0


DFUN = "declare-fun"
CURR = "__CURR__"
NEXT = "__NEXT__"
INIT = "__AT0"
COMM = ";;"

def parse_model(model):
    setvals = []
    init_vars = []
    curr_vars = []
    next_vars = []
    init = []
    trans = []
    variables = []

    for line in model.split("\n"):
        if COMM in line:
            continue
        if line == "":
            continue
        if ("declare-fun" in line):
            if (CURR in line):
                curr_vars.append(line)
                var = line[line.find(DFUN)+len(DFUN)+1:line.find(")")-2]
                variables.append(var)
            if (NEXT in line):
                next_vars.append(line)
            if (INIT in line):
                init_vars.append(line)
        elif ("set" in line):
            setvals.append(line)
        else:
            if INIT in line:
                init.append(line)
            else:
                trans.append(line)

    return (setvals, variables, init_vars, curr_vars, next_vars, init, trans)

def to_and(lst):
    if len(lst) == 1:
        return lst[0]
    
    ret = "(and %s %s)"%(lst[0], lst[1])
    if len(lst) == 2:
        return ret

    for i in range(2,len(lst),1):
        ret = "(and %s %s)"%(ret, lst[i])

    return ret

def at(time):
    return "__AT%s"%time

def curr(var):
    return "%s%s"%(var, CURR)

def next(var):
    return "%s%s"%(var, NEXT)

def m_1(prefix):
    return "%s<1>"%prefix

def m_2(prefix):
    return "%s<2>"%prefix


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Equivalence check of two smtlib2 formulas generated by CoreIR.')

    parser.set_defaults(input_file1=None)
    parser.add_argument('-i1', '--input-file1', metavar='input_file1', type=str, required=True,
                       help='input file 1')

    parser.set_defaults(input_file2=None)
    parser.add_argument('-i2', '--input-file2', metavar='input_file2', type=str, required=True,
                       help='input file 2')
    
    parser.set_defaults(inputlist=None)
    parser.add_argument('-i', '--inputs', metavar='inputlist', type=str, required=True,
                        help='list of input variables')

    parser.set_defaults(outputlist=None)
    parser.add_argument('-o', '--outputs', metavar='outputlist', type=str, required=True,
                        help='list of output variables')
    
    args = parser.parse_args()

    config = Config()
    
    config.input_file1 = args.input_file1
    config.input_file2 = args.input_file2
    config.inputlist = args.inputs
    config.outputlist = args.outputs
    
    sys.exit(generate_equivalence_check(config))
