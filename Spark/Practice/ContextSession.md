
## SparkSession 和 SparkContext 的区别与联系

### SparkContext

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

### SparkSession

- **Spark 2.x/3.x 时代的核心入口**
    - 是 Spark 应用程序的主要入口点(Spark 2.x 及后期版本), 整合了 `SparkContext`、`SQLContext`、`HiveContext` 等

    - 提供了 DataFrame 和 Dataset API 的统一入口

    - 简化了 Spark 应用的配置和初始化过程

    - 支持更高级的 SQL 和 DataFrame 操作

    - 提供了更丰富的配置选项和更好的性能优化
