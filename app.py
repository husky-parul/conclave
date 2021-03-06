import sys
sys.path.append('/opt/app-root/src/conclave')

print ("This Hi is from app.py!!")

"""
Simple example workflow for MOC deployment of Conclave
"""
from conclave import lang as sal
from conclave.utils import *
from conclave import workflow

print ("*********** this is conclave path: ")
def protocol():
    """
    Define inputs and operations to be performed between them.
    """

    # define input columns
    cols_in_a = [
        defCol('a', 'INTEGER', [2]),
        defCol('b', 'INTEGER', [2]),
    ]
    cols_in_b = [
        defCol('a', 'INTEGER', [2]),
        defCol('c', 'INTEGER', [2]),
    ]
    cols_in_c = [
        defCol('a', 'INTEGER', [2]),
        defCol('d', 'INTEGER', [2])
    ]

    # instantiate input columns
    # NOTE: input file names will correspond to the 0th arg of each create call ("in1", "in2", etc.)
    in1 = sal.create("in1", cols_in_a, {2})
    in2 = sal.create("in2", cols_in_b, {2})
    in3 = sal.create("in3", cols_in_c, {2})

    # operate on columns
    # join in1 & in2 over the column 'a', name output relation 'join1'
    join1 = sal.join(in1, in2, 'join1', ['a'], ['a'])
    join2 = sal.join(join1, in3, 'join2', ['a'], ['a'])

    # collect leaf node
    out = sal.collect(join2, 2)

    # return root nodes
    return {in1, in2, in3}


if __name__ == "__main__":

    workflow.run(protocol)
