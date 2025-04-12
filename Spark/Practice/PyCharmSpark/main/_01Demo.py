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
    # * 代表使用所有cpu, setAppName 设置任务的名字
    conf = SparkConf().setMaster("local[*]").setAppName("wordcount")
    # 获取 sc对象
    sc = SparkContext(conf=conf)

    print(sc)


    sc.stop()

