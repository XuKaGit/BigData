## spark-submit 脚本


- **作用**: 将写好的代码提交到spark, 由spark进行调度执行.

<p>


### 1. spark-submit 语法

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

### 2. Options



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


### 3. 优先级

代码中的配置(**set**) > spark-submit 命令中的配置 > spark-defaults.conf 中的配置


### 4.

- **deploy mode options**: ``--deploy-mode``用于指定**driver**在哪里启动, 默认是**client**模式, 也可以是**cluster**模式. 如果是**client**模式, 则driver在你提交任务的机器上启动. 如果是**cluster**模式, 则driver会在集群中随机一台机器启动.
   - **pyspark**只支持**client**模式
   - **cluster**模式相对更好, 因为此模式下, client端提交完代码后 可以关闭, driver会一直运行, 直到任务执行完毕.

- 在**YARN**模式下
  - **client**模式: driver和AppMaster是不在一起的, 各玩各的.
  - **cluster**模式: driver和AppMaster合二为一.