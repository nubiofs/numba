# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import

from .. import flowy
from ..flowy import Opcode

simple_ops = [
    # Need a data dependence graph to optimize these
    Opcode("load", read=True),
    Opcode("store", read=False),

    # Some opcodes we try to optimize
    Opcode("tuple_new", canfold=True),
    Opcode("int_eq", read=False, sideeffects=False, canfold=True),
    Opcode("int_mul", read=False, sideeffects=False, canfold=True),

    # Branches
    Opcode("cbranch"),
]

opdict = dict((opcode.op, opcode) for opcode in simple_ops)

class OpContext(flowy.OperationContext):

    def is_terminator(self, operation):
        return operation.opcode.op == "cbranch"

    def get_condition(self, conditional_branch):
        return conditional_branch.args[0]

def make_testprogram():
    g = flowy.FunctionGraph()
    builder = flowy.OperationBuilder(g)

    # if x: ...
    entry = builder.add_block([], "entry")
    cond_block = builder.add_block([entry], "cond")
    loop_block = builder.add_block([cond_block], "loop")
    exit_block = builder.add_block([cond_block, loop_block])

    cond_block.add_parent(loop_block)

    c1 = builder.const(1)
    c2 = builder.const(2)

    eq = builder.op(opdict["int_eq"], [c1, c2])
    cbr = builder.op(opdict["cbranch"], [eq])
    op1 = builder.op(opdict["int_mul"], [c1, c2])
    op2 = builder.op(opdict["tuple_new"], [c1, c2, op1])

    cond_block.append(cbr)
    loop_block.extend([op1, op2])

    return g

def test_LICM():
    g = make_testprogram()
    print(g)

test_LICM()