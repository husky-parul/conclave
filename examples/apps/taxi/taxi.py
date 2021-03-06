import sys

import conclave.lang as sal
from conclave import CodeGenConfig
from conclave import generate_and_dispatch
from conclave.codegen.sharemind import SharemindCodeGenConfig
from conclave.codegen.spark import SparkConfig
from conclave.utils import *


def protocol():
    cols_in_1 = [
        defCol("companyID", "INTEGER", [1]),
        defCol("price", "INTEGER", [1])
    ]
    in1 = sal.create("in1", cols_in_1, {1})
    cols_in_2 = [
        defCol("companyID", "INTEGER", [2]),
        defCol("price", "INTEGER", [2])
    ]
    in2 = sal.create("in2", cols_in_2, {2})
    cols_in_3 = [
        defCol("companyID", "INTEGER", [3]),
        defCol("price", "INTEGER", [3])
    ]
    in3 = sal.create("in3", cols_in_3, {3})

    cab_data = sal.concat([in1, in2, in3], "cab_data")

    selected_input = sal.project(
        cab_data, "selected_input", ["companyID", "price"])
    local_rev = sal.aggregate(selected_input, "local_rev", [
        "companyID"], "price", "+", "local_rev")
    scaled_down = sal.divide(
        local_rev, "scaled_down", "local_rev", ["local_rev", 1000])
    first_val_blank = sal.multiply(
        scaled_down, "first_val_blank", "companyID", ["companyID", 0])
    local_rev_scaled = sal.multiply(
        first_val_blank, "local_rev_scaled", "local_rev", ["local_rev", 100])
    total_rev = sal.aggregate(first_val_blank, "total_rev", [
        "companyID"], "local_rev", "+", "global_rev")
    local_total_rev = sal.join(local_rev_scaled, total_rev, "local_total_rev", [
        "companyID"], ["companyID"])
    market_share = sal.divide(local_total_rev, "market_share", "local_rev", [
        "local_rev", "global_rev"])
    market_share_squared = sal.multiply(market_share, "market_share_squared", "local_rev",
                                        ["local_rev", "local_rev", 1])
    hhi = sal.aggregate(market_share_squared, "hhi", [
        "companyID"], "local_rev", "+", "hhi")

    sal.collect(hhi, 1)

    # return root nodes
    return {in1, in2, in3}


if __name__ == "__main__":


    # python3 ${DIR}/taxi.py $1 $2-spark-node-0:8020 /home/ubuntu spark://$2-spark-node-0:7077

    # taxi.py <party ID> <HDFS master node:port> <HDFS root dir> <Spark master url>"

    if len(sys.argv) < 5:
        print("usage: taxi.py <party ID> <HDFS master node:port> <HDFS root dir> <Spark master url>")
        sys.exit(1)

    pid = int(sys.argv[1])
    hdfs_namenode = sys.argv[2]
    hdfs_root = sys.argv[3]
    spark_master_url = sys.argv[4]

    workflow_name = "job-" + str(pid)
    sm_config = SharemindCodeGenConfig("/mnt/shared")

    spark_config = SparkConfig(spark_master_url)

    conclave_config = CodeGenConfig(workflow_name) \
        .with_sharemind_config(sm_config) \
        .with_spark_config(spark_config)

    conclave_config.code_path = "/mnt/shared/" + workflow_name
    conclave_config.input_path = "hdfs://{}/{}/taxi".format(
        hdfs_namenode, hdfs_root)
    conclave_config.output_path = "hdfs://{}/{}/taxi".format(
        hdfs_namenode, hdfs_root)
    conclave_config.pid = pid
    conclave_config.name = workflow_name
    network_config = {
        "pid": pid,
        "parties": {
            1: {"host": "ca-spark-node-0", "port": 9001},
            2: {"host": "cb-spark-node-0", "port": 9002},
            3: {"host": "cc-spark-node-0", "port": 9003}
        }
    }
    conclave_config.with_network_config(network_config)

    generate_and_dispatch(protocol, conclave_config, ["sharemind"], ["spark"])
