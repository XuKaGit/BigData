# Spark 操作与函数详解详解

## 1. Concepts

- **shuffle** : 数据混洗, Shuffle 可以说是 Spark 中最核心但也最昂贵的操作. 简单来说, Shuffle 是在集群节点之间对数据进行重新分区,分发的过​​程. 当需要执行的操作, 其结果不能仅仅通过操作当前分区的数据来完成, 而需要汇总来自不同分区(甚至不同节点)的数据时,就需要 Shuffle


## 2. Transformations

### 2.1. Mappers


#### 2.1.1. `flatMap()`
`flatMap()` = 一对多映射 + 扁平化 : 对 RDD 中的每一个元素应用一个函数, 这个函数返回的是一个**序列(例如列表,数组)**; 再将所有这些返回的序列"压平"或"展开", 合并成一个单一的 RDD.

<p>

示例: 将一个包含多个句子的 RDD, 拆分成包含所有单词的 RDD:

- 输入 RDD: `["hello world", "spark fun"]`

- 如果使用 map, 并应用 `sentence.split(" ")` 函数: 
    - 第一个元素 `"hello world"` -> `["hello", "world"]`; 第二个元素 `"spark fun"` -> `["spark", "fun"]`
    - map 后的输出 RDD：`[["hello", "world"], ["spark", "fun"]]`
    - 最终会得到一个嵌套的列表, 这通常不是我们想要的.

<p>

- 如果使用 flatMap, 并应用 `sentence.split(" ")`函数：

    - 它会执行与 map 相同的函数, 得到 `[["hello", "world"], ["spark", "fun"]]`

    - 然后执行 flat 操作, 将这个嵌套的列表"压平"

    - flatMap 后的最终输出 RDD: `["hello", "world", "spark", "fun"]`. 这就是我们想要的,由单个单词组成的 RDD.

### 2.2. Reducers




#### 2.2.1. `reduceByKey()`

`reduceByKey(func)` 是一个应用于 (键, 值) 对 RDD（Pair RDD）上的转换(Transformation)操作. 它的核心功能是: 使用一个指定的函数 func, 将具有相同键的值进行聚合. 它之所以如此重要, 是因为它在内部进行了大量的优化, 尤其是在处理大规模数据时, 性能远超其他看似功能相似的操作(如 groupByKey()). 

<p>

`reduceByKey` 的执行过程可以分为三个阶段:

- 阶段一: Map 端本地聚合 (Map-Side Combine): 在每个 RDD 分区内部(即在每个 Worker 节点上), `reduceByKey` 会对该分区内具有相同键的值应用用户提供的 `func` 函数进行第一次聚合.这个阶段发生在数据 Shuffle 之前.

- 阶段二: 数据 Shuffle (洗牌): 只有在第一阶段中每个分区本地聚合后的**中间结果**才会被发送到网络上传输.所有具有相同键的中间结果会被发送到同一个节点, 以便进行最终的聚合.

- 阶段三: Reduce 端最终聚合 (Final Reduce): 在接收到所有相关键的中间结果后, 节点会再次应用用户提供的 `func` 函数, 将这些中间结果合并成最终结果.


<p>


func 函数的要求: 传递给 `reduceByKey` 的函数 `func` 必须满足两个数学性质: 

- 结合律 (Associative): (a + b) + c 的结果必须等于 a + (b + c).
    - 原因: 这保证了 Spark 可以先在部分数据上进行计算(如分区本地聚合), 然后再将这些部分结果合并起来, 最终结果依然是正确的. 加法 + 和乘法 * 都满足结合律.

- 交换律 (Commutative): a + b 的结果必须等于 b + a.

    - 原因: Spark 不保证在一个分区内处理元素的顺序, 交换律确保了无论处理顺序如何,结果都一样.

```python

from pyspark import SparkConf, SparkContext

# 初始化 Spark 环境
conf = SparkConf().setAppName("ReduceByKeyExample").setMaster("local")
sc = SparkContext(conf=conf)

# 创建一个 (商品, 销售额) 的 RDD
sales_data = [("苹果", 10), ("香蕉", 5), ("苹果", 5), 
              ("橘子", 8), ("香蕉", 15), ("苹果", 20)]
sales_rdd = sc.parallelize(sales_data)

# 定义一个求和函数
# func 接收两个参数，这两个参数都是相同键的值
# 例如，对于'苹果'，第一次可能是 func(10, 5) -> 15
# 第二次可能是 func(15, 20) -> 35
add_func = lambda x, y: x + y

# 使用 reduceByKey 进行聚合
total_sales_rdd = sales_rdd.reduceByKey(add_func)

# 收集结果并打印
result = total_sales_rdd.collect()
print("各商品销售总额:")
for product, total in result:
    print(f"{product}: {total}")

# 输出：
# 各商品销售总额:
# 苹果: 35
# 香蕉: 20
# 橘子: 8

sc.stop()
```

### 2.3. Aggregations

#### 2.3.1. `groupByKey()`

`groupByKey()` 是一个应用于由 `(键, 值)` 对组成的 RDD(即 Pair RDD)上的转换操作(**宽依赖**). 它的作用是将所有具有相同键的值组合(汇集)到一个可迭代的序列中:

- 输入: 一个 `RDD[(K, V)]`, 其中 K 是键, V 是值.

- 输出: 一个 `RDD[(K, Iterable<V>)]`, 其中 K 是原始的键, `Iterable<V>` 是一个包含所有属于该键的原始值的可迭代对象.

- 简单来说: 按键分组, 把值放入一个列表

```python 

假设 RDD 分布在两个分区上: 

Partition 1: ('A', 1), ('B', 2)
Partition 2: ('A', 3), ('C', 4)

执行 groupByKey() 之后, Spark 会进行 Shuffle, 将相同的键发送到同一个分区, 结果 RDD 如下: 

Partition X: ('A', <iterator [1, 3]>)
Partition Y: ('B', <iterator [2]>), ('C', <iterator [4]>)

====================================================================
from pyspark import SparkConf, SparkContext

# 初始化 Spark 环境
conf = SparkConf().setAppName("GroupByKeyExample").setMaster("local")
sc = SparkContext(conf=conf)

# 创建一个 (键, 值) 对的 RDD
data = [("水果", "苹果"), ("水果", "香蕉"), ("蔬菜", "白菜"), 
        ("水果", "橙子"), ("蔬菜", "萝卜")]
rdd = sc.parallelize(data)

# 使用 groupByKey()
grouped_rdd = rdd.groupByKey()

# groupByKey() 返回的结果中，值是一个可迭代对象 (ResultIterable)


# 将 groupByKey() 操作后得到的分组 RDD，将其中的值从特殊的可迭代对象转换为标准的 Python 列表
# 然后将整个 RDD 的所有数据从集群收集回驱动程序（Driver）的主内存中，并赋值给变量 result
result = grouped_rdd.mapValues(list).collect()

# 打印结果
print("groupByKey() 的结果:")
for key, values in result:
    print(f"{key}: {values}")

# 输出:
# groupByKey() 的结果:
# 水果: ['苹果', '香蕉', '橙子']
# 蔬菜: ['白菜', '萝卜']

sc.stop()
====================================================================
```


### 2.6. Filters

### 2.5. Joins

Spark join 基本原理: Spark join的基本实现流程如下图所示, Spark将参与Join的两张表抽象为流式表(`StreamTable`)和查找表(`BuildTable`), 通常系统会默认设置`StreamTable`为大表, `BuildTable`为小表. 流式表的迭代器为`streamItr`, 查找表迭代器为`BuidIter`. Join操作就是遍历`streamIter`中每条记录, 然后从`buildIter`中查找相匹配的记录.





## 3. Actions


`select, filter, withColumn	count, show, collect, save, toPandas`

## 4. Spark DataFrames & SQL

### 4.1. Window Operations

与 groupBy 操作不同, groupBy 会将多行数据聚合为一行, 而窗口操作在计算后不会将行合并, 它会为每一行都返回一个结果.

<p>

在 PySpark 中, 定义一个窗口主要通过 `pyspark.sql.Window` 对象来完成, 它主要包含三个部分:

- `partitionBy(*cols)` - 分区, 作用: 定义窗口的边界, 类似于 SQL 中的 `GROUP BY`. 所有的计算都将在这些分区内独立进行, 如果不指定 `partitionBy`, 则所有数据都在同一个窗口内.

- `orderBy(*cols)` - 排序, 作用: 在每个分区内部, 根据指定的列对数据进行排序. 对于排名,lag(前一行),lead(后一行)等依赖顺序的函数, `orderBy` 是必需的.

- `rowsBetween(start, end) / rangeBetween(start, end)` - 定义窗口范围 (Frame), 作用: 更精确地定义在排序后的分区内,哪些行被包含进来用于计算.这对于计算移动平均, 累计总和等非常有用. `start` 和 `end` 可以是 `Window.unboundedPreceding (窗口第一行)`, `Window.currentRow (当前行)`, `Window.unboundedFollowing (窗口最后一行)`, 或者是相对于当前行的偏移量.


<p>

常用窗口函数类型
- 排名函数 (Ranking Functions)

    - `rank()`: 排名, 有并列时会跳过后续名次 (例如: 1, 2, 2, 4)

    - `dense_rank()`: 密集排名, 有并列时不会跳过后续名次 (例如: 1, 2, 2, 3)

    - `row_number()`: 行号,不考虑并列,  排名唯一 (例如: 1, 2, 3, 4)

    - `percent_rank()`: 百分比排名

- 分析函数 (Analytic Functions)

    - `lag(col, offset)`: 获取当前行之前第 offset 行的 col 列的值.

    - `lead(col, offset)`: 获取当前行之后第 offset 行的 col 列的值.

- 聚合函数 (Aggregate Functions): sum(col), avg(col), max(col), min(col), count(col) 等.这些聚合函数在窗口上使用时, 不会减少行数, 而是将聚合结果作为新的一列添加到每一行.

```python
from pyspark.sql import SparkSession, Window
from pyspark.sql import functions as F

# 初始化 SparkSession
spark = SparkSession.builder.appName("WindowOperationsExample").getOrCreate()

# 创建示例 DataFrame
data = [("IT", "张三", 8000),
        ("IT", "李四", 8500),
        ("IT", "王五", 7000),
        ("HR", "赵六", 6000),
        ("HR", "钱七", 6500),
        ("IT", "孙八", 9000),
        ("HR", "周九", 5500)]
columns = ["department", "name", "salary"]
df = spark.createDataFrame(data, columns)
df.show()

# +----------+----+------+
# |department|name|salary|
# +----------+----+------+
# |        IT|张三|  8000|
# |        IT|李四|  8500|
# |        IT|王五|  7000|
# |        HR|赵六|  6000|
# |        HR|钱七|  6500|
# |        IT|孙八|  9000|
# |        HR|周九|  5500|
# +----------+----+------+

# 示例一 - 计算每个部门的薪资排名 (使用排名函数)
# 定义窗口：按部门分区，按薪资降序排列
window_spec_rank = Window.partitionBy("department").orderBy(F.col("salary").desc())

# 应用 rank() 和 dense_rank() 函数
df_ranked = df.withColumn("rank", F.rank().over(window_spec_rank)) \
              .withColumn("dense_rank", F.dense_rank().over(window_spec_rank))

print("计算薪资排名:")
df_ranked.show()

# +----------+----+------+----+----------+
# |department|name|salary|rank|dense_rank|
# +----------+----+------+----+----------+
# |        HR|钱七|  6500|   1|         1|
# |        HR|赵六|  6000|   2|         2|
# |        HR|周九|  5500|   3|         3|
# |        IT|孙八|  9000|   1|         1|
# |        IT|李四|  8500|   2|         2|
# |        IT|张三|  8000|   3|         3|
# |        IT|王五|  7000|   4|         4|
# +----------+----+------+----+----------+

# 示例二 - 与薪资更高一位的同事比较 (使用分析函数)

# 使用 lag() 函数获取薪资排名高一位（即薪资更高）的同事的薪资
# 注意：因为是降序排列，所以 lag(1) 是薪资更高的那个人
df_lag = df_ranked.withColumn("higher_salary", F.lag("salary", 1).over(window_spec_rank))

print("与薪资更高一位的同事比较:")
df_lag.show()

# +----------+----+------+----+----------+-------------+
# |department|name|salary|rank|dense_rank|higher_salary|
# +----------+----+------+----+----------+-------------+
# |        HR|钱七|  6500|   1|         1|         null|
# |        HR|赵六|  6000|   2|         2|         6500|
# |        HR|周九|  5500|   3|         3|         6000|
# |        IT|孙八|  9000|   1|         1|         null|
# |        IT|李四|  8500|   2|         2|         9000|
# |        IT|张三|  8000|   3|         3|         8500|
# |        IT|王五|  7000|   4|         4|         8000|
# +----------+----+------+----+----------+-------------+


# 示例三 - 计算部门内的累计薪资 (使用聚合函数和 Frame)
# 定义窗口：按部门分区，按薪资升序排列，范围是从第一行到当前行
window_spec_agg = Window.partitionBy("department") \
                          .orderBy("salary") \
                          .rowsBetween(Window.unboundedPreceding, Window.currentRow)

# 应用 sum() 函数计算累计总和
df_agg = df.withColumn("running_total_salary", F.sum("salary").over(window_spec_agg))

print("计算部门内的累计薪资:")
df_agg.show()

# +----------+----+------+--------------------+
# |department|name|salary|running_total_salary|
# +----------+----+------+--------------------+
# |        HR|周九|  5500|                5500|
# |        HR|赵六|  6000|               11500|
# |        HR|钱七|  6500|               18000|
# |        IT|王五|  7000|                7000|
# |        IT|张三|  8000|               15000|
# |        IT|李四|  8500|               23500|
# |        IT|孙八|  9000|               32500|
# +----------+----+------+--------------------+
```