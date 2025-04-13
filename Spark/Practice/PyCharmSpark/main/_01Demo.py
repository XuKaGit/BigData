import os

from pyspark import SparkConf, SparkContext


if __name__== '__main__':


    os.environ['JAVA_HOME'] = "C:\Program Files\Java\jdk-1.8"
    # 配置hadoop路径
    os.environ['HADOOP_HOME'] = "D:\hadoop-3.3.4"
    # 配置python解释器
    os.environ['PYSPARK_PYTHON'] = "D:/Anaconda/envs/DDL/python.exe"
    os.environ['PYSPARK_DRIVER_PYTHON'] = "D:/Anaconda/envs/DDL/python.exe"


    #  想要一个 spark context 对象, 简称 sc

    # 获取conf对象
    # setMaster 按照什么方式运行, local / node1:7077
    # * 代表使用所有cpu, 2代表使用2核cpu,  setAppName 设置任务的名字
    conf = SparkConf().setMaster("local[4]").setAppName("wordcount")
    # 获取 sc对象
    sc = SparkContext(conf=conf)

    print(sc)

    fileRdd = sc.textFile("../data/wordcount/data.txt")

    rsRdd = fileRdd.filter(lambda x: len(x) > 0).flatMap(lambda line : line.strip().split(" ")).map(lambda word: (word, 1)).reduceByKey(lambda x, y: x + y)

    rsRdd.saveAsTextFile("../data/wordcount/output1")


    sc.stop()

