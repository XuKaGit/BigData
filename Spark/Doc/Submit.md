# Spark提交与运行模式



## 1. spark-submit 脚本


- **作用**: 将写好的代码提交到spark, 由spark进行调度执行.

<p>


### 1.1 spark-submit 语法


#### 1.1.1. local 模式下 spark-submit 语法

```shell

saprk-submit --master local[4] /export/server/spark/examples/src/main/python/pi.py 10
```

#### 1.1.2. Standalone模式下 spark-submit 语法
```shell
# 提交任务的命令

cd /export/server/spark

./bin/spark-submit [options] <app jar | python file | R file> [app arguments]

# 比如
./bin/spark-submit \
      --name {Application Name} \
      --master spark://localhost:7077 \  # 指定standalone模式
      --deploy-mode client \
      --executor-memory 4G \
      --total-executor-cores 8 \
      myapp.py
```

```shell

## 杀死一个任务
### 也可以在网页 node1:8080 上进行操作
./bin/spark-submit --kill [submission ID] --master [spark://node1:7077]

## 查看一个任务的状态
./bin/spark-submit --status [submission ID] --master [spark://node1:7077]

```





#### 1.1.3. Yarn 模式下 spark-submit 语法


```shell

spark-submit
  --name {application name}
  --master yarn
  --deploy-mode cluster
  --keytab ihp-dataops/ihp/config/hdfs_hive_config/hrcsdz.common-ro-1-picp.keytab
  --principal hrcsdz.common-ro-1-picp@INDATA.COM
  --queue default
  --py-files ihp-dataops/ihp.zip,tool_config_input.yaml,keytabfile
  --conf spark.yarn.dist.archives=hdfs://indata-100-126-0-14.indata.com:8020/tmp/llmtempdata/llc_test/llc.tar.gz#environment
  --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=./environment/bin/python3
  --conf spark.yarn.appMasterEnv.PYSPARK_DRIVER_PYTHON=./environment/bin/python3
  --conf spark.security.credentials.hbase.enabled=false
  --conf spark.executorEnv.FTLANG_CACHE=./environment/fasttext-langdetect
  ihp-dataops/ihp/tag/language/language_tag_tool.py

```

- options解读:
  - `--py-files ...:` 它告诉Spark需要将我们打包的代码 (ihp.zip),配置文件 (tool_config_input.yaml) 和密钥文件 (keytabfile) 都分发到集群的所有工作节点上.
  - `--conf spark.yarn.dist.archives=...` : 这个配置负责分发一个`压缩好的Python虚拟环境 (llc.tar.gz)`. `#`后面的 `environment` 会创建一个名为 `environment` 的快捷方式(符号链接), 这样作业代码就可以通过这个固定的路径名来访问虚拟环境了
  - `--queue default`: 告诉Yarn: 请将我这个 Spark 作业, 提交到 YARN 集群中名为 default 的资源队列里去排队和运行.

<br>
```
# 如何创建 llc.tar.gz
conda activate llc
conda install torch
conda-pack -n llc -o llc.tar.gz

```

### 1.2. Other Options


- **driver-memory**:  设置driver的内存大小, 等于代码中的 `SparkConf.set("spark.driver.memory", "2g")`

- **driver-cores**: 设置driver的cpu核数, 默认**1g**. 等于代码中的 `SparkConf.set("spark.driver.cores", "2")`

- **superviser**:  如果设置为true, 则当driver失败时, 重新启动driver.

<p>

- **executor-memory**:  设置executor的内存大小, 等于代码中的 `SparkConf.set("spark.executor.memory", "2g")`

- **executor-cores**:  指定每个executor使用的cpu核数, 等于代码中的 `SparkConf.set("spark.executor.cores", "2")`

<p>

- **total-executor-cores**:  standalone 模式下指定**所有**executor使用的cpu核数, 用于间接指定executor的数量.

- **num-executors**:  YARN模式下指定executor的数量




### 1. 3. 命令优先级

代码中的配置(**set**) > spark-submit 命令中的配置 > spark-defaults.conf 中的配置


## 2. spark运行模式

- **deploy mode options**: ``--deploy-mode``用于指定**driver**在哪里启动, 默认是**client**模式, 也可以是**cluster**模式. 如果是**client**模式, 则driver在你提交任务的机器上启动. 如果是**cluster**模式, 则driver会在集群中随机一台机器启动.
   - **cluster**模式相对更好, 因为此模式下, client端提交完代码后 可以关闭, driver会一直运行, 直到任务执行完毕.


### 2.1. standalone mode



#### 2.1.1. client mode

工作流程:

- 你在客户端机器上运行 spark-submit
- Driver 在这台客户端机器上启动
- Driver 向 Spark Master 请求资源(CPU核心/内存) 来运行 Executor.
- Master 在集群的 Worker 节点上启动 Executor 进程.
- 这些 Executor 进程会反向连接到你客户端机器上的 Driver 进程, 接收任务并汇报结果

#### 2.1.2. cluster mode

工作流程: 

- 你在客户端机器上运行 spark-submit
- spark-submit 会将你的应用程序(比如你的 Python 文件或 Jar 包) 上传到集群.
- 它请求 Master 在集群中启动一个 Driver 进程.
- Master 选择一个 Worker 节点, 并在该节点上启动 Driver.
- 一旦 Driver 在集群内部成功启动, 客户端的 spark-submit 进程就可以安全退出了, 它后续的运行与客户端机器无关.
- 集群内的 Driver 再向 Master 申请资源来启动 Executor.



### 2.2. yarn mode

**YARN ApplicationMaster (AM)**: 可以想象成 Spark 作业派驻到 YARN 军营里的后勤官. 它的主要职责是与 YARN 的最高指挥部(ResourceManager) 沟通, 为总司令申请作战部队(申请资源来运行 Executor). 

- **client**模式: driver和AppMaster是不在一起的, 各玩各的. Driver运行在你执行 spark-submit 命令的客户端机器; ApplicationMaster运行在 YARN 集群内部的一个容器里. 其运行逻辑如下:
  - 你运行 `spark-submit --deploy-mode client` ...
  - Spark Driver 程序立即在你本地的客户端机器上启动
  - 本地的 Driver(总司令)联系 YARN 的 ResourceManager, 说:"请帮我在集群里启动我的后勤官(ApplicationMaster)".
  - ResourceManager 在集群的某个节点上启动一个容器, 运行 ApplicationMaster. 这个 AM 是一个相对轻量的进程.
  - 这个远在前线的 AM(后勤官)的主要工作, 就是充当一个代理: 它接收来自后方大本营 Driver 的指令("我需要10个兵力,每个兵力需要2G内存");它将这些指令转发给 ResourceManager,进行资源申请.当申请到容器后,它在这些容器里启动 Executor 进程
  - Executor 启动后, 会反向直接连接到你客户端机器上的 Driver, 接收具体的作战命令.
  - 如果你的客户端机器关机或网络中断,后方的总司令就没了,整个应用就会失败.

<br>

- **cluster**模式: Driver 和 ApplicationMaster 运行在同一个进程中, 位于 YARN 集群的第一个容器(Container)里. 它们本质上是同一个东西. 其运行逻辑如下:
  - 你运行 `spark-submit --deploy-mode cluster ...`
  - 你的代码和依赖被打包, 发送给 YARN 的 ResourceManager
  - ResourceManager 命令集群中的一个节点(NodeManager) 启动第一个容器. 这个容器就是 `ApplicationMaster`
  - 在这个 AM 容器内部, Spark Driver 程序开始运行.
  - 这个 Driver/AM 进程 作为后勤官, 向 ResourceManager 申请更多的容器资源.
  - 当申请到新容器后, 它会在这些新容器里启动 Executor 进程
  - 从此, Driver(总司令)就在这个前线指挥部(AM 容器)里, 直接向它的部队(Executors)下达命令
  - 即使你关闭了提交任务的电脑, 这个位于集群内部的"总司令兼后勤官"也会继续指挥作战, 直到任务完成



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