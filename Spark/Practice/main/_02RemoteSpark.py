"""

在Windows本地连接云上HDFS
- HDFS上的数据
- 本地的资源

"""
import os
import time

from pyspark import SparkConf, SparkContext

if __name__== '__main__':


    os.environ['JAVA_HOME'] = "C:/Program Files/Java/jdk-1.8"

    # 配置hadoop路径
    os.environ['HADOOP_HOME'] = "D:/hadoop-3.3.4"
    # 配置python解释器
    os.environ['PYSPARK_PYTHON'] = "D:/Anaconda/envs/DDL/python.exe"
    os.environ['PYSPARK_DRIVER_PYTHON'] = "D:/Anaconda/envs/DDL/python.exe"

    # hadoop用户
    os.environ['HADOOP_USER_NAME'] = 'hadoop'

    #  想要一个 spark context 对象, 简称 sc

    # 获取conf对象
    # setMaster 按照什么方式运行, local / node1:7077
    # * 代表使用所有cpu, 2代表使用2核cpu,  setAppName 设置任务的名字
    conf = SparkConf().setMaster("local[4]").setAppName("wordcount")
    # 获取 sc对象
    sc = SparkContext(conf=conf)

    print(sc)

    fileRdd = sc.textFile("hdfs://124.71.7.7:9820/test.txt")

    # strip() 方法用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
    # split() 方法用于把一个字符串分割成一个列表
    rsRdd = fileRdd.filter(lambda x: len(x) > 0) \
        .flatMap(lambda line: line.strip().split()) \
        .map(lambda word: (word, 1)) \
        .reduceByKey(lambda x, y: x + y)

    time.sleep(100)
    print(rsRdd.collect())
    time.sleep(100)

    # 创建output文件夹
    # saveAsTextFile方法在输出目录已存在时会抛出异常
    rsRdd.saveAsTextFile("hdfs://node1:9820/result")

    sc.stop()
