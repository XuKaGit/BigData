## Introduction to  Spark


### 1. Spark框架的概述

- **Spark定义**: Apache Spark是用于大规模数据(large-scala data)处理的统一(unified)分析引擎.
- **Spark起源**: Spark最早源于一篇论文 *Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing*, 论文中提出了一种弹性分布式数据集(RDD)的概念.
<p>

- **RDD**: RDD是一种分布式内存抽象,其使得程序员能够在大规模集群中做**内存运算**,并且有一定的**容错**方式.而这也是整个Spark的核心数据结构,Spark整个平台都围绕着RDD进行.

- **Spark**是由**Scala**语言编写的


- 在Spark中, **数据**都叫**RDD**; **方法**都叫**算子**; **程序**都叫**DAG(有向无环图)**.


#### 1.1 Spark的组成

- **Spark Core**: Spark Core是Spark的核心,它实现了Spark的基本功能,包括任务调度,内存管理,错误恢复,与存储系统交互等. 可以基于多种语言进行编程,如Scala,Java,Python等.

<p>

- **Spark SQL**: 类似于Hive, 基于SQL进行开发, SQL会转化为SparkCore离线程序.

<p>

- **Spark Streaming**: Spark Streaming是Spark的一个模块,它提供了实时流处理能力.它将数据流分割成小的批次,然后使用Spark Core来处理这些批次.


- **Struct Streaming**: Spark Structured Streaming是Spark的一个模块,它提供了结构化流处理能力.它将数据流分割成小的批次,然后使用Spark SQL来处理这些批次.

<p>

- **Spark ML lib**: MLlib是Spark的一个模块,它提供了机器学习算法和工具,包括分类,回归,聚类,协同过滤等.
- **GraphX**: GraphX是Spark的一个模块,它提供了图计算能力,包括图算法,图存储和图计算优化等.




#### 1.2 Spark运行的3种模式

- **Local模式**: 本地模式,用于开发和测试,可以在本地机器上运行,不需要集群环境.
- **Standalone模式**: 独立模式,Spark自带的集群管理器,可以在集群上运行,需要配置集群环境.
- **YARN模式**: YARN模式,使用Hadoop YARN作为集群管理器,可以在Hadoop集群上运行,需要配置Hadoop YARN环境.




#### 1.3 Spark为什么比mapreduce快

- **内存计算**: Spark将数据保存在内存中,而MapReduce将数据保存在磁盘上,因此Spark的计算速度比MapReduce快.
   
   - 由于 MapReduce 的框架限制, 一个 MapReduce 任务只能包含一次 Map 和一次 Reduce. 计算完成之后, MapReduce 会将运算结果写回到磁盘中(更准确地说是分布式存储系统)供下次计算使用. 如果所做的运算涉及大量循环, 那么整个计算过程会不断重复地往磁盘里读写中间结果. 这样的读写数据会引起大量的网络传输以及磁盘读写, 极其耗时. 而且它们都是没什么实际价值的废操作. 因为上一次循环的结果会立马被下一次使用, 完全没必要将其写入磁盘.

   - **DAG执行引擎**: Spark使用DAG(Directed Acyclic Graph)执行引擎,可以将多个操作合并成一个任务,减少了shuffle和数据落地磁盘的次数. 所以一个Spark 任务并不止包含一个Map 和一个Reduce, 而是由一系列的Map、Reduce构成. 这样, 计算的中间结果可以高效地转给下一个计算步骤, 提高算法性能.


<p>

- MR计算是**进程**级别的, 而Spark是**线程**级别的, 所以Spark的启动速度更快, 执行效率更高.

### 2. 三种工作模式与Web页面介绍

#### 2.1 单机模式

- 见 `EnvBuild.md`
- 本地模式启动:  
   ```shell
   conda activate
   /export/server/spark/bin/pyspark --master local[2]

   ```


- 测试：



   ```python

   # map算子实现列表元素平方

   list1 = [1,2,3,4,5,6,7,8,9,10]

   #将列表通过sc.parallelize方法转化为一个分布式集合RDD
   listRdd = sc.parallelize(list1) # sc是SparkContext对象
   #将RDD中的每个分区的数据进行处理
   resultRdd = listRdd.map(lambda x: x ** 2)
   # 将结果RDD的每个元素进行输出
   resultRdd.foreach(lambda x : print(x))


   ```



#### 2.2 Spark Standalone模式

- Standalone模式是Spark自带的集群管理器,可以在集群上运行,需要配置集群环境.


<div style="text-align: center;">
    <img src="Figures\spark_alone.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>

- 具体安装见 `EnvBuild.md`

- 集群提交任务:
   ```shell

   # 提交任务 pi.py
   /export/server/spark/bin/spark-submit --master spark://node1:7077 /export/server/spark/examples/src/main/python/pi.py 10

   ```

- 进入集群模式python编程:
   ```shell
   /export/server/spark/bin/pyspark --master spark://node1:7077
   ```

#### 2.3. Spark程序运行的层次结构

在Spark程序中, 一个程序( 对应一个**Driver**进程)由多个Job组成, 一个Job由多个Stage组成, 一个Stage由多个Task组成.

- 在分布式集群模式下, 任何一个Spark程序( **任务**)都是由1个**Driver**和多个**Executor**组成的. 
  - **Driver** 和 **Executor** 都是进程, 都是在有任务时才会启动.
  - **Driver**负责将任务拆分成多个**Task**, 并将Task发送给**Executor**, Executor负责执行Task并返回结果给Driver. Driver和Executor都运行在集群的各个节点上.
  - **独立进程**: Driver 运行在独立的 JVM 中, 这意味着它与Master分开.所以Driver关闭不影响Master进程.


#### 2.4. Spark Web页面

- **node1:4040**: 是一个运行的Application在运行的过程中临时绑定的端口, 用以查看当前任务的状态. 有新任务就会有一个4040, 4040被占用会顺延到4041, 4042等. 4040是一个临时端口, 当前程序运行完成后, 4040就会被注销. 4040和Driver相关联, 一个Driver启动起来, 一个4040端口就被绑定起来, 并可以查看该程序的运行状态.


- **node1:8080:** 默认情况是StandAlone下, Master角色(进程)的WEB端口, 用以查看当前Master( 集群)的状态。(Driver和Master是两个东西, Master进程用于管理集群, Driver用于管理某次运行的程序, 某个Driver程序运行完成, 其所绑定的4040端口释放, 但不会影响到Master进程)

- **node1:18080:** 默认是历史服务器的端口( 可以理解为是**历史Driver查看器**), 由于每个程序运行完成, 4040端口就要被注销, 在以后想回看某个程序的运行状态就可以通过历史服务器查看, 历史服务器长期稳定运行, 可供随时查看记录的程序的运行过程.




#### 2.5 Spark YARN模式
- YARN模式,使用Hadoop YARN作为集群管理器,可以在Hadoop集群上运行,需要配置Hadoop YARN环境.
- 具体安装见 `EnvBuild.md`


### 3. PySpark本地环境( Windows)搭建

- 1. 安装Anaconda



### 4. Spark RDD

### 5. Spark 算子

### 6. Spark SQL

### Other Spark Topics

#### **SparkContext**

SparkContext, 简称为 **SC**. SparkContext 是 PySpark 中最重要的类之一, 它是与 Spark 集群连接的主要入口点, 并提供了对 Spark 的核心功能的访问.
<p>

SparkContext 可以用来创建 RDD 和广播变量, 并且还可以执行与集群相关的一些操作. 可以通过使用 SparkContext 对象来调用各种方法, 以及配置和管理 Spark 应用程序.

<p>

可能的一个错误: 文件 `/tmp/spark-events` 不存在.
- 这个错误通常是由于 SparkContext 在启动时无法找到该文件而引起的.`/tmp/spark-events` 文件夹是 Spark 在运行过程中生成的事件日志文件的存储位置. SparkContext 在启动时会尝试去该文件夹存放日志文件, 以便后续的监控和调试. 如果该文件夹不存在, SparkContext 将无法写入日志文件, 从而导致该错误的出现.

- 解决方法: 要解决这个错误, `mkdir /tmp/spark-events`  (直接在云服务器本地创建就行)

#### **SparkSession**

- SparkSession是Spark 2.0引入的新概念,它是一个入口点,用于创建DataFrame、Dataset和SQLContext等对象.




### Reference

- [大数据面试题：Spark和MapReduce之间的区别？各自优缺点？](https://blog.csdn.net/qq_41544550/article/details/133658290)
- [知乎用户4omIIF对于”MapReduce和Spark的区别是什么“的回答](https://www.zhihu.com/question/53354580)
- [2024-02-21（Spark）](https://blog.csdn.net/weixin_44847812/article/details/136206678#:~:text=4040%EF%BC%9A%E6%98%AF%E4%B8%80%E4%B8%AA%E8%BF%90%E8%A1%8C%E7%9A%84Application%E5%9C%A8%E8%BF%90%E8%A1%8C%E7%9A%84%E8%BF%87%E7%A8%8B%E4%B8%AD%E4%B8%B4%E6%97%B6%E7%BB%91%E5%AE%9A%E7%9A%84%E7%AB%AF%E5%8F%A3%EF%BC%8C%E7%94%A8%E4%BB%A5%E6%9F%A5%E7%9C%8B%E5%BD%93%E5%89%8D%E4%BB%BB%E5%8A%A1%E7%9A%84%E7%8A%B6%E6%80%81%E3%80%82%204040%E8%A2%AB%E5%8D%A0%E7%94%A8%E4%BC%9A%E9%A1%BA%E5%BB%B6%E5%88%B04041%EF%BC%8C4042%E7%AD%89%E3%80%82,4040%E6%98%AF%E4%B8%80%E4%B8%AA%E4%B8%B4%E6%97%B6%E7%AB%AF%E5%8F%A3%EF%BC%8C%E5%BD%93%E5%89%8D%E7%A8%8B%E5%BA%8F%E8%BF%90%E8%A1%8C%E5%AE%8C%E6%88%90%E5%90%8E%EF%BC%8C4040%E5%B0%B1%E4%BC%9A%E8%A2%AB%E6%B3%A8%E9%94%80%E3%80%82%204040%E5%92%8CDriver%E7%9B%B8%E5%85%B3%E8%81%94%EF%BC%8C%E4%B8%80%E4%B8%AADriver%E5%90%AF%E5%8A%A8%E8%B5%B7%E6%9D%A5%EF%BC%8C%E4%B8%80%E4%B8%AA4040%E7%AB%AF%E5%8F%A3%E5%B0%B1%E8%A2%AB%E7%BB%91%E5%AE%9A%E8%B5%B7%E6%9D%A5%EF%BC%8C%E5%B9%B6%E5%8F%AF%E4%BB%A5%E6%9F%A5%E7%9C%8B%E8%AF%A5%E7%A8%8B%E5%BA%8F%E7%9A%84%E8%BF%90%E8%A1%8C%E7%8A%B6%E6%80%81%E3%80%82)