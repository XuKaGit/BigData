# Spark提交与运行模式



## 1. spark-submit 脚本


- **作用**: 将写好的代码提交到spark, 由spark进行调度执行.

<p>


### 1.1 spark-submit 语法

```shell
# 提交任务的命令

cd /export/server/spark

./bin/spark-submit [options] <app jar | python file | R file> [app arguments]

## 杀死一个任务
### 也可以在网页 node1:8080 上进行操作
./bin/spark-submit --kill [submission ID] --master [spark://node1:7077]

## 查看一个任务的状态
./bin/spark-submit --status [submission ID] --master [spark://node1:7077]
```



- **Examples**:

```python
## standalone 模式
/export/server/spark/bin/spark-submit --master spark://node1:7077 /export/server/spark/examples/src/main/python/pi.py 10

### local 模式
saprk-submit --master local[4] /export/server/spark/examples/src/main/python/pi.py 10

### YARN 模式
spark-submit --master yarn programe.py outputpath

```

### 1.2. Options



<p>

- **name**: ``--name``, 设置应用名称, 等于代码中的 `SparkContext.setAppName()`

<p>


- **jars**: ``--jars``, 指定依赖的jar包, 等于代码中的 `SparkContext.setJars()`. 比如读写MySQL时, 需要指定`mysql-connector-java-5.1.47.jar`之类的MySQL驱动包.

<p>

- **conf**: ``--conf``, 设置spark的配置参数, 等于代码中的 `SparkConf.set()`

<p>

- **driver-memory**: ``--driver-memory``, 设置driver的内存大小, 等于代码中的 `SparkConf.set("spark.driver.memory", "2g")`

- **driver-cores**: ``--driver-cores``, 设置driver的cpu核数, 默认**1g**. 等于代码中的 `SparkConf.set("spark.driver.cores", "2")`


- **superviser**: ``--supervise``, 如果设置为true, 则当driver失败时, 重新启动driver.


<p>

- **executor-memory**: ``--executor-memory``, 设置executor的内存大小, 等于代码中的 `SparkConf.set("spark.executor.memory", "2g")`

<p>

- **executor-cores**: ``--executor-cores``, 指定每个executor使用的cpu核数, 等于代码中的 `SparkConf.set("spark.executor.cores", "2")`

<p>

- **total-executor-cores**: ``--total-executor-cores``, standalone 模式下指定**所有**executor使用的cpu核数, 用于间接指定executor的数量.

- **num-executors**: ``--num-executors``, YARN模式下指定executor的数量

<p>

- **queue**: ``--queue``, 指定提交任务到哪个队列


### 1. 3. 优先级

代码中的配置(**set**) > spark-submit 命令中的配置 > spark-defaults.conf 中的配置


### 1.4. 运行模式

- **deploy mode options**: ``--deploy-mode``用于指定**driver**在哪里启动, 默认是**client**模式, 也可以是**cluster**模式. 如果是**client**模式, 则driver在你提交任务的机器上启动. 如果是**cluster**模式, 则driver会在集群中随机一台机器启动.
   - **pyspark**只支持**client**模式
   - **cluster**模式相对更好, 因为此模式下, client端提交完代码后 可以关闭, driver会一直运行, 直到任务执行完毕.

- 在**YARN**模式下
  - **client**模式: driver和AppMaster是不在一起的, 各玩各的.
  - **cluster**模式: driver和AppMaster合二为一.



## 2. SparkSession 和 SparkContext 的区别与联系

- 都在driver中运行
### 2.1. SparkContext

- **Spark 1.x 时代的核心入口**
    - 是 Spark 功能的主要入口点(Spark 1.x 及早期版本)

    - 负责与集群通信, 管理任务调度、资源分配等底层操作. 

    - 直接创建 RDD

    - 控制 Spark 应用的生命周期 (`sc.start()`, `sc.stop()`)

    - 提供低级 API (如累加器、广播变量)

    ```python
    from pyspark import SparkContext
    sc = SparkContext("local", "MyApp")  # 本地模式
    rdd = sc.parallelize([1, 2, 3])     # 创建 RDD
    ```

### 2.2. SparkSession

- **Spark 2.x/3.x 时代的核心入口**
    - 是 Spark 应用程序的主要入口点(Spark 2.x 及后期版本), 整合了 `SparkContext`、`SQLContext`、`HiveContext` 等

    - 提供了 DataFrame 和 Dataset API 的统一入口

    - 简化了 Spark 应用的配置和初始化过程

    - 支持更高级的 SQL 和 DataFrame 操作

    - 提供了更丰富的配置选项和更好的性能优化

    ```
    from pyspark.sql import SparkSession

    # 初始化 SparkSession
    spark = SparkSession.builder.appName("RDDAndDataFrame").getOrCreate()

    # 方法 1：通过 SparkContext 创建 RDD
    sc = spark.sparkContext
    rdd = sc.parallelize([1, 2, 3])
    print("RDD 内容:", rdd.collect())

    # 方法 2：从 DataFrame 转换到 RDD
    df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
    rdd_from_df = df.rdd
    print("DataFrame 转 RDD:", rdd_from_df.collect())

    # 关闭 SparkSession
    spark.stop()
    ```