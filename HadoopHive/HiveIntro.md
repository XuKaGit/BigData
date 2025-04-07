## Introduction to Hive

**Hive 是什么:**
- MapReduce支持程序开发( `Java/Python`), 但是不支持`SQL`
- Apache Hive是一款分布式SQL计算工具, 其主要功能是将SQL语句翻译成MapReduce程序运行.

<p>

**Hive的应用场景:**
- Hive构建在Hadoop文件系统之上, Hive不提供实时的查询和基于行级的数据更新操作, 不适合**需要低延迟的应用**, 如**联机事务处理(On-line Transaction Processing, OLTP)相关应用. 
- Hive适用于**联机分析处理( On-Line Analytical Processing, OLAP)**, 应用场景如: 数据挖掘/非实时分析等.

<p>

**Hive需要的基本功能:**
 - 用户只写SQL,
 - Hive自动将SQL转化为MapReduce程序并提交运行
 - 处理位于HDFS上的结构化数据

 <p>

**Hive的架构**
- **元数据(Metastore)**: 元数据包括表名, 表所属的数据库(默认是default), 表的拥有者, 列/分区字段, 表的类型(是否是外部表), 表的数据所在目录等. 元数据默认存储在自带的derby数据库中, 推荐使用MySQL存储Metastore
- **Driver**: SQL解析器, 执行SQL分析/ SQL到MapReduce程序的转换/ 以及提交MapReduce程序运行并收集执行结果. 

<div style="text-align: center;">
    <img src="Figures\Hive_Structure.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>


**Hive执行流程**
- Hive通过给用户提供的一系列交互接口, 接受到的用户指令( HiveSQL, HQL), 使用自己Driver, 结合元数据(metaStore), 将这些指令翻译成MapReduce, 提交到Hadoop中执行, 最后，将执行返回的结果输出到用户交互接口中. 



**Hive和MySQL比较:**


| 特性         | Hive                       | MySQL                     |
|--------------|----------------------------|---------------------------|
| 语言         | 类 SQL                    | SQL                       |
| 语言规模     | 大数据(PD及以上)        | 数据量小，一般在百万左右到达单表极限 |
| 数据插入     | 能增加 `INSERT`，不能 `UPDATE`，`DELETE` | 能 `INSERT`，`UPDATE`，`DELETE` |
| 数据存储     | HDFS                       | 拥有自己的存储空间       |
| 计算引擎     | MapReduce/Spark/Tez       | 自己的引擎 InnoDB        |






