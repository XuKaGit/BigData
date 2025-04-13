"""

使用Windows本地模式运行Spark程序
- 本地的数据
- 本地的Spark
- 本地的Hadoop
- 本地的cpu

"""


import os
import re

from pyspark import SparkConf, SparkContext


if __name__== '__main__':


    os.environ['JAVA_HOME'] = "C:/Program Files/Java/jdk-1.8"
    # 配置hadoop路径
    os.environ['HADOOP_HOME'] = "D:/hadoop-3.3.4"
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

    # strip() 方法用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
    # split() 方法用于把一个字符串分割成一个列表
    rsRdd = fileRdd.filter(lambda x: len(x) > 0) \
                   .flatMap(lambda line: line.strip().split()) \
                   .map(lambda word: (word, 1)) \
                   .reduceByKey(lambda x, y: x + y)
    """
    
    # 使用正则表达式去切除多个字符
    rsRdd = fileRdd.filter(lambda x: len(x) > 0) \
                   .flatMap(lambda line: re.split('\s+', line.strip())) \
                   .map(lambda word: (word, 1)) \
                   .reduceByKey(lambda x, y: x + y)
    """

    print(rsRdd.collect())



    # 创建output文件夹
    # saveAsTextFile方法在输出目录已存在时会抛出异常
    rsRdd.saveAsTextFile("../data/wordcount/output")


    sc.stop()

