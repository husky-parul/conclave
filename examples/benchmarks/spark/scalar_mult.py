import conclave.lang as sal
import conclave.dispatch as dis
from conclave.comp import dag_only
from conclave.utils import *
from conclave.codegen import spark
from conclave import CodeGenConfig
import sys


def scalar_mult(namenode, root, f_size, master_url):

    @dag_only
    def protocol():

        colsInA = [
            defCol('a', 'INTEGER', [1]),
            defCol('b', 'INTEGER', [1]),
        ]

        in1 = sal.create("in1", colsInA, set([1]))
        mult1 = sal.multiply(in1, 'mult1', 'a', ['a', 5])

        return set([in1])

    dag = protocol()
    config = CodeGenConfig('scalar_mult_spark_{}'.format(f_size))

    config.code_path = "/mnt/shared/" + config.name
    config.input_path = "hdfs://{}/{}/{}" \
        .format(namenode, root, f_size)
    config.output_path = "hdfs://{}/{}/scalar_mult_sp{}" \
        .format(namenode, root, f_size)

    cg = spark.SparkCodeGen(config, dag)
    job = cg.generate(config.name, config.output_path)
    job_queue = [job]

    dis.dispatch_all(master_url, None, job_queue)

if __name__ == "__main__":

    hdfs_namenode = sys.argv[1]
    hdfs_root = sys.argv[2]
    # configurable benchmark size
    filesize = sys.argv[3]
    spark_master_url = sys.argv[4]

    scalar_mult(hdfs_namenode, hdfs_root, filesize, spark_master_url)

