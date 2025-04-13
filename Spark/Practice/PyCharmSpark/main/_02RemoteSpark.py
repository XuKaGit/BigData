"""

在Windows本地连接云上HDFS
- HDFS上的数据
- 本地的Spark
- 本地的cpu

"""
import os
from pyspark import SparkConf, SparkContext

if __name__== '__main__':


    os.environ['JAVA_HOME'] = "C:\Program Files\Java\jdk-1.8"
    # 配置hadoop路径
    os.environ['HADOOP_HOME'] = "D:\hadoop-3.3.4"
    # 配置python解释器
    os.environ['PYSPARK_PYTHON'] = "D:/Anaconda/envs/DDL/python.exe"
    os.environ['PYSPARK_DRIVER_PYTHON'] = "D:/Anaconda/envs/DDL/python.exe"