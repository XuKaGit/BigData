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

### 2. 环境搭建

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






### Reference

- [大数据面试题：Spark和MapReduce之间的区别？各自优缺点？](https://blog.csdn.net/qq_41544550/article/details/133658290)
- [知乎用户4omIIF对于”MapReduce和Spark的区别是什么“的回答](https://www.zhihu.com/question/53354580)
