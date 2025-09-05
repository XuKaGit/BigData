## Spark 如何与 Hadoop与 Hive交互



### 1. spark.sql 处理 hive 表

Configuration of Hive is done by placing your hive-site.xml, core-site.xml (for security configuration), and hdfs-site.xml (for HDFS configuration) file in `conf/.`


#### 步骤1. Hive开启MetaStore服务

- 1.1: 修改 `hive/conf/hive-site.xml` 新增如下配置
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
- 1.2: 启动 Hive Metastore 服务

```bash
nohup /export/servers/hive/bin/hive --service metastore 2>&1 >> /var/log.log &
```

#### 步骤2: SparkSQL整合Hive MetaStore

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

- 获取"地址"和"结构": Metastore 回答:"当然, 我知道. 这张表的列是 `(id INT, name STRING)`, 它的数据文件存储在 HDFS 的这个路径下: `hdfs://namenode:8020/user/hive/warehouse/my_table/`".

- 制定执行计划: Spark Driver 拿到表的结构(Schema)和数据位置后, 会制定一个优化的查询执行计划.

- 分布式读取数据: Spark Driver 将任务分发给集群中的各个 Executor 节点. Executor 们直接访问 HDFS, 从指定的路径 `hdfs://.../my_table/`下并行读取数据文件.

- 执行计算: Executor 在内存中执行计算(比如过滤/聚合等), 并最终返回结果


### 2. spark.sql 处理 hdfs 上没有被注册为hive表的文件


使用 `spark.read API` 读取数据, 然后可以将其注册为一个临时视图(Temporary View), 之后就可以对这个临时视图使用 spark.sql 了

```python

# 1. 直接从 HDFS 路径读取 Parquet 文件，Spark 会自动推断其结构
clicks_df = spark.read.parquet("hdfs://namenode:8020/data/raw/clicks_parquet")

# 2. 为这个 DataFrame 创建一个临时的, 只在当前 SparkSession 中有效的“表名”
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

### 3. 将spark dataframe写入hive

```python

# 写成 Hive 内部表（如果表不存在会自动建表）
df.write.mode("overwrite").saveAsTable("mydb.my_managed_table")
```