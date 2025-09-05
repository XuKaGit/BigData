# Spark 调优

## 1. 解决数据倾斜问题

### 1.1. 加盐再去盐

### 1.2. 优化 Spark join

Spark join的基本实现流程如下图所示, Spark将参与Join的两张表抽象为**流式表(StreamTable)**和**查找表(BuildTable)**, 通常系统会默认设置**StreamTable**为大表, **BuildTable**为小表. 流式表的迭代器为`streamItr`, 查找表迭代器为`BuidIter`. Join操作就是遍历streamIter中每条记录, 然后从buildIter中查找相匹配的记录. 

#### 1.2.1. SortMergeJoin

SortMergeJoin是spark默认的join方式, 步骤: 

- 对两张表**分别**进行shuffle重分区, 之后将相同key的记录分到对应分区, 每个分区内的数据在join之前都要进行排序, 这一步对应Exchange节点和sort节点. 也就是spark 的sort merge shuffle过程.

- 遍历流式表, 对每条记录都采用顺序查找的方式从查找表中搜索, 每遇到一条相同的key就进行join关联. 每次处理完一条记录, 只需从上一次结束的位置开始继续查找. 

#### 1.2.2. BroadcastHashJoin

BroadcastHashJoin适用于一张表非常小, 可以被广播到每个executor的场景. 这种join方式避免了shuffle过程, 直接将小表广播到每个executor, 然后在每个executor上对大表进行join操作.

#### 1.2.3. ShuffleHashJoin


## 2. 解决输出卡死问题

`.coalesce(partition:int)` : `.coalesce(100)` ->  将DataFrame 或 RDD 的分区(Partition)数量, 以一种高效的方式减少到 100 个