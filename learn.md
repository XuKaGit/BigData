#### hdfs路径

`hdfs://namenode:8020/data/raw/clicks_parquet`  -> `[协议]://[NameNode:端口] / [文件系统路径]`

#### `df.withColumn`

df.withColumn() 是 PySpark DataFrame 的一个转换(Transformation)方法, 它的主要功能是添加一个新列或者替换一个同名的现有列.
最重要的一点是，DataFrame 是 **不可变（Immutable）** 的. 这意味着 withColumn() 不会修改原始的 DataFrame (df), 而是会返回一个包含了新列的,全新的 DataFrame.所以你通常需要将结果赋给一个新的变量.
`new_df = df.withColumn("column_name", column_expression)`


#### spark.sql 处理 hive 表

Configuration of Hive is done by placing your hive-site.xml, core-site.xml (for security configuration), and hdfs-site.xml (for HDFS configuration) file in conf/.


步骤一: Hive开启MetaStore服务
1.1:修改 hive/conf/hive-site.xml 新增如下配置
```xml
<configuration>
    <property>
      <name>hive.metastore.warehouse.dir</name>
      <value>/user/hive/warehouse</value>
    </property>
    <property>
      <name>hive.metastore.local</name>
      <value>false</value>
    </property>
    <property>
      <name>hive.metastore.uris</name>
      <value>thrift://node01:9083</value>
    </property>
 </configuration>

```
1.2. 启动 Hive Metastore 服务
```bash
nohup /export/servers/hive/bin/hive --service metastore 2>&1 >> /var/log.log &
```

步骤二: SparkSQL整合Hive MetaStore
SparkSQL 整合 Hive 的 MetaStore 主要思路就是要通过配置能够访问它, 并且能够使用 HDFS 保存 WareHouse, 所以可以直接拷贝 Hadoop 和 Hive 的配置文件到 Spark 的配置目录.
```bash
cp /export/servers/hive-1.1.0-cdh5.14.0/conf/hive-site.xml /export/servers/spark/conf
cp /export/servers/hadoop-2.6.0-cdh5.14.0/etc/hadoop/core-site.xml /export/servers/spark/conf
cp /export/servers/hadoop-2.6.0-cdh5.14.0/etc/hadoop/hdfs-site.xml /export/servers/spark/conf

```



```python
from pyspark.sql import SparkSession

# 创建 SparkSession 并启用 Hive 支持
spark = SparkSession.builder \
    .appName("HiveQueryExample") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://node01:9083") \
    .enableHiveSupport() # 开启hive语法的支持 \
    .getOrCreate()

# 查询 Hive 表
query = "SELECT * FROM your_database.your_table"
df = spark.sql(query)

# 显示查询结果
df.show()

# 停止 SparkSession
spark.stop()


```

当你执行一条 `spark.sql("SELECT * FROM my_table` 查询时, Spark 内部会执行以下步骤:

- 查询元数据: Spark Driver 首先会去连接 Hive Metastore, 询问: "嘿, 你知道一张叫 my_table 的表吗?"

- 获取"地址"和"结构": Metastore 回答:"当然, 我知道. 这张表的列是 (id INT, name STRING), 它的数据文件存储在 HDFS 的这个路径下: hdfs://namenode:8020/user/hive/warehouse/my_table/".

- 制定执行计划: Spark Driver 拿到表的结构(Schema)和数据位置后, 会制定一个优化的查询执行计划.

- 分布式读取数据: Spark Driver 将任务分发给集群中的各个 Executor 节点. Executor 们直接访问 HDFS, 从指定的路径 hdfs://.../my_table/ 下并行读取数据文件.

- 执行计算: Executor 在内存中执行计算(比如过滤/聚合等), 并最终返回结果


#### spark.sql 处理 hdfs上 没有被注册为hive表的文件


使用 `spark.read API` 读取数据, 然后可以将其注册为一个临时视图(Temporary View), 之后就可以对这个临时视图使用 spark.sql 了

```python

# 1. 直接从 HDFS 路径读取 Parquet 文件，Spark 会自动推断其结构
clicks_df = spark.read.parquet("hdfs://namenode:8020/data/raw/clicks_parquet")

# 2. 为这个 DataFrame 创建一个临时的、只在当前 SparkSession 中有效的“表名”
clicks_df.createOrReplaceTempView("temp_clicks_table")

# 3. 现在就可以使用 spark.sql 来查询这个临时视图了
frequent_users_df = spark.sql("""
    SELECT userId, COUNT(*) as click_count
    FROM temp_clicks_table
    WHERE event_date = '2025-08-21'
    GROUP BY userId
    HAVING COUNT(*) > 100
""")
frequent_users_df.show()
```


#### hive表和hdfs文件之间的关系

HDFS (Hadoop Distributed File System) 是一个分布式文件存储系统, 用来实际保存数据.

Hive 是一个数据仓库工具, 本身并不存储数据, 而是存储 表的元数据(表结构、字段信息、分区信息、数据位置等), 这些元数据保存在 Metastore(通常是关系型数据库)中.


Hive 表与 HDFS 文件的映射关系: Hive 表中的数据, 底层就是存放在 HDFS 上的文件.

表中的 每一行数据 不会单独存成文件, 而是以 文件(Text、ORC、Parquet 等) 的形式批量存储.

一个表对应一个目录:

- 例如: hdfs://namenode:8020/user/hive/warehouse/mydb.db/mytable/

一个分区对应子目录:

- 例如: .../mytable/dt=2025-08-22/

文件存放在分区或表目录下, 可能是多个文件(因为数据是分布式存储)


- 内部表: 注册为hive表的hdfs文件默认存储在Hive 的默认仓库目录: hdfs://namenode:8020/user/hive/warehouse/
- 外部表: 注册为hive表的hdfs文件存储在用户指定的路径, 例如: hdfs://namenode:8020/data/external/mytable/, 删除表时, 只删除元数据,不删除 HDFS 上的数据文件


#### 将hadoop文件注册为hive表

```python

LOAD DATA INPATH '/user/hadoop/data/file1.txt' INTO TABLE my_table;
```

#### spark.sql opertor -> .agg()

`df.groupBy().agg()` 是 PySpark DataFrame 的一个转换(Transformation)方法, 它的主要功能是对数据进行分组聚合操作. 这个方法允许你对 DataFrame 中的数据进行分组, 然后对每个组应用一个或多个聚合函数, 如计数、求和、平均值等.

#### Actions vs Transformations

特性	Transformation (转换)	Action (行动)		
求值时机	惰性求值 (Lazy)	立即求值 (Eager)		
返回类型	Spark DataFrame / RDD	非DataFrame值（Python对象, 数字, None等）		
作用	构建执行计划 (DAG)	触发执行计划		
数据流	在Executor节点间分布式处理	将数据从Executor汇集到Driver或写入外部系统		
典型示例	select, filter, withColumn	count, show, collect, save, toPandas		



#### 怎么设置spark-submit的`num-executors`,`executor-cores`以及`executor-memory`等资源参数

- `num-executors`: 启动的 Executor 进程的总数, 每个 Executor 是一个独立的 JVM 进程, 负责执行任务(Task)

- `executor-cores`: 分配给每个 Executor 的 CPU核心数. 这些核心可以并行执行任务.

- `executor-memory`: 分配给每个 Executor 的堆内存(Heap Memory)大小, 这部分内存主要用于RDD的缓存/shuffle过程中的数据缓冲等.

- `Container`: YARN 中的资源分配单位, Spark 的一个 Executor 会运行在一个 Container 中.

- 小型到中型 Executor

  `executor-cores`: 建议设置为 4 或 5 个.

  - HDFS I/O 吞吐量: HDFS 客户端在处理大量并发读写时可能会遇到瓶颈. 通常, 每个 Executor 分配 5 个或更少的核心可以获得较好的 HDFS 吞吐量.超过这个数量, I/O 性能提升可能就不明显了.

  - GC (垃圾回收) 效率: 虽然较大的 Executor 内存可以缓存更多数据, 但过大的 JVM 堆内存(例如, 超过 64GB)可能会导致长时间的 Full GC, 造成任务长时间停顿(Stop-the-World). 将核心数和内存限制在一定范围内, 有助于保持 GC 的高效.

  - 并行度: `executor-cores` 乘以 `num-executors` 决定了整个 Spark 应用的最大并行任务数

  - `executor-memory`:  根据每个节点的总内存和 executor-cores 来计算


观察 Spark UI：Spark UI 是你最好的朋友。通过观察任务的执行时间、GC 时间、Shuffle 数据量等指标，来判断你的配置是否合理。

如果 GC 时间过长，可以尝试减少 executor-memory。

如果 CPU 利用率很低，可能是 I/O 密集型任务，或者任务并行度不够。可以检查分区数是否合理。

如果发现 Spill (溢写) 到磁盘的数据很多，说明 executor-memory 可能不足以容纳中间数据，需要适当增加。

考虑数据倾斜：如果发生数据倾斜，再完美的资源配置也无济于事。某个任务会因为处理远超平均水平的数据而成为瓶颈。需要从代码层面解决数据倾斜问题（如加盐、使用 map-side join 等）。


#### 序列化与反序列化

spark如何处理和分发大型、复杂且通常不可序列化的对象, 例如机器学习模型(TFBertForSequenceClassification)和分词器(BertTokenizer):



1. 问题的核心:Spark 的工作机制
要理解序列化问题, 首先要明白 Spark 的分布式执行模型:

- Driver (驱动程序)：是提交 Spark 作业的入口。它负责解析代码，创建执行计划，并将任务（Task）分发到各个 Executor。

- Executor (执行器)：是工作节点上的独立 JVM 进程。它们接收来自 Driver 的任务和代码，并实际处理数据。

当在代码中定义一个 UDF (用户自定义函数) 并应用它时，例如 `df.withColumn("tag_result", tag_self_cognition_udf(...))`，Spark 必须将这个 UDF 的逻辑以及它所依赖的所有变量（这被称为**闭包**）从 Driver 序列化（打包），然后通过网络发送给每个 Executor。Executor 接收到后会反序列化（解包）它们，以便执行任务。

<p>

关键的挑战在于：像 TensorFlow/Hugging Face 模型这样的对象非常复杂，内部可能包含无法被标准序列化工具（如 Python 的 pickle）处理的资源（如文件句柄、网络连接、底层 C++ 对象指针）。直接尝试在 Driver 端加载模型，然后让 Spark 将其序列化并发送给 Executor，几乎必然会导致 SerializationError 或 PicklingError。


2. 项目中的解决方案：在 Executor 端进行“懒加载” (Lazy Initialization)
项目代码 完美地展示了如何规避这个问题。

具体实现如下：

- 1: 全局变量初始化为 None：
在 UDF 文件的顶层，tokenizer 和 model 被声明为全局变量并初始化为 None。None 对象是完全可序列化的，因此 Spark 可以毫无问题地将包含这些变量的 UDF 闭包发送给所有 Executor。

```python
# 以下两个变量是必须的，避免在UDF外部加载模型时出现序列化问题
tokenizer = None
model = None
```

- 2： 在 UDF 内部检查并加载：
在 UDF 函数 tag_self_cognition 内部，代码首先检查 tokenizer 和 model 是否为 None。

```python

def tag_self_cognition(content, id, cfg):
    global model, tokenizer
    ...
    if tokenizer is None:
        tokenizer = BertTokenizer.from_pretrained(cfg["model_cfg"]["vocab_path"])
        logger.info("tokenizer is loaded")
    if model is None:
        model = TFBertForSequenceClassification.from_pretrained(cfg["model_cfg"]["model_path"])
        logger.info("model is loaded")
    ...
```

首次执行：当一个 Executor 进程第一次执行这个 UDF 时，它会发现 model 是 None。于是，它会在自己的进程内（在工作节点上）从指定的路径加载模型。

加载后重用：加载成功后，模型对象被赋值给全局变量 model。当这个 Executor 处理下一条数据再次调用此 UDF 时，if model is None: 的判断将为 False，因此会直接重用已经加载到内存中的模型，而不会重复加载。


这种解决方案的意义和优势
避免了序列化错误：通过不在 Driver 端创建模型对象，从根本上避免了序列化复杂对象的难题。

提高了效率：模型和分词器是资源密集型对象，加载过程非常耗时。这种“单例模式” (Singleton Pattern) 确保了每个 Executor 进程只加载一次模型，然后在其生命周期内处理成千上万条数据时都能复用，极大地提高了处理效率。如果为每一行数据都加载一次模型，性能将是灾难性的。

依赖共享存储：这个方案能成功运行的前提是，所有 Executor 节点都必须能够从完全相同的路径访问到模型文件。从配置文件 README.md 中可以看到，模型路径被设置为 /task-pvc/...，这表明项目部署在 Kubernetes 等容器化环境中，并通过 PVC (Persistent Volume Claim) 挂载了一个共享存储，确保了所有节点都能访问。