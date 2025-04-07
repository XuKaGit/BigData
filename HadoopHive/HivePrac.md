# Hive实操



## 1.启动Hive
- 首先, 确保启动了Metastore服务, hdfs和yarn集群

```shell
start-dfs.sh
start-yarn.sh
mapred --daemon start historyserver
nohup /export/server/hive/bin/hive --service metastore >> /export/server/hive/logs/metastore.log 2>&1 &
```

- 运行jps, 看有没有**RunJar**, 如果有那么表示已经启动了Metastore服务
- 在目录`export/server/hive`下执行`bin/hive`进入到`Hive Shell`环境中

### 1.1 Hive客户端

#### 1.1.1 HiveServer2 & Beeline

- 在启动Hive的时候, 除了必备的Metastore服务, 有2种方式使用Hive. 除了上述的方法, 还有`bin/hive --service hiveserver2`, 它的后台执行脚本是`nohup bin/hive --service hiveserver2 >> logs/hiveserver2.log 2>&1 &`. 
<p>


- `bin/hive --service hiveserver2`启动的是HiveServer2服务.

<p>

- HiveServer2是Hive内置的一个`ThriftServer`服务, 提供`Thrift`端口供其它客户端链接. 可以连接ThriftServer的客户端有: 
  - Hive内置的 beeline客户端工具(命令行工具)
  - 第三方的图形化SQL工具,如DataGrip/ DBeaver/ Navicat等

<div style="text-align: center;">
    <img src="Figures\HiveServer2.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>


- hiveserver2监听了10000端口，对外提供的thrift端口，默认10000  . `netstat -anp|grep 10000`

- **Beeline**: 在node1上使用beeline客户端进行连接访问. 需要注意hiveserver2服务启动之后需要稍等一会才可以对外提供服务. **Beeline**是**JDBC**的客户端，通过JDBC协议和Hiveserver2服务进行通信, 协议的地址是:**jdbc:hive2://node1:10000**

```shell
/export/server/hive/bin/beeline
connect jdbc:hive2://node1:10000
```

- Notice: 执行`nohup bin/hive --service hiveserver2 >> logs/hiveserver2.log 2>&1 &`后, 执行`tail -f logs/hiveserver2.log`没有异常则表示启动成功.


#### 1.1.2 DataGrip


## 2. HQL-(HiveSQL)

- 执行的HQL命令可以在 node1:8088 网页上YARN控制台查看 (写SQL, 执行MapReduce)

- **创建表:** `CREAT TABLE test(id INT, name String, gender string);`
   - 如果不指定表的database, 默认创建的表是存储在数据库`default`中

- 创建的`test`表在哪: 执行`hadoop fs -ls /user/hive/warehouse` 就可以看到`/user/hive/warehouse/test`
   - Hive中创建的表和库数据, 存储在HDFS中, 默认存放在hdfs://node1:8020/user/hive/warehouse中


### 2.1. Hive数据库操作

#### 2.1.1 数据库创建 / 删除

```sql

--如果数据库已存在就删除
drop database if exists db_msg cascade ;

--如果数据库
drop database db_msg cascade;

--创建数据库
create database db_msg ;
--切换数据库
use db_msg ;
-- 描述数据库
desc database db_msg

--列举数据库
show databases ;
```

```sql
# 查询数据库
SHOW DATABASES [LIKE 'identifier_with_wildcards'];
# example 
hive> show databases like 'db_study*';
OK
db_study_1
db_study_2

```


#### 2.1.2 数据库与HDFS的关系

- Hive的库在HDFS上就是一个以 **.db**结尾的目录
- 默认存储在 `/user/hive/warehouse`中
- 可以使用**location**关键字在创建的时候指定存储目录
```sql
create database db_hive2 location '/db_study';
ALTER DATABASE database_name SET LOCATION hdfs_path;
```
### 2.2. Hive数据表操作

#### 2.2.1 Hive表的基本语法以及基本数据类型

- 基本语法
```sql

# 完整的创建表的语法

CREATE [TEMPORARY] [EXTERNAL] TABLE [IF NOT EXISTS] [db_name.]table_name

[(col_name data_type [COMMENT col_comment], ...)]

[COMMENT table_comment]

[PARTITIONED BY (col_name data_type [COMMENT col_comment], ...)]

[CLUSTERED BY (col_name, col_name, ...)

[SORTED BY (col_name [ASC|DESC], ...)] INTO num_buckets BUCKETS]

[ROW FORMAT row_format]

[STORED AS file_format]

[LOCATION hdfs_path]

[TBLPROPERTIES (property_name=property_value, ...)]

```

- 数据类型
```
int
boolean
double
string
varchar  # 可变字符串
timestamp
date
array
```
- Hive的基本数据类型可以做类型转换, 转换的方式包括隐式转换以及显示转换
   - 方式一:隐式转换. 具体规则:
    ```
    a. 任何整数类型都可以隐式地转换为一个范围更广的类型, 如tinyint可以转换成int, int可以转换成bigint.

    b. 所有整数类型、float和string类型都可以隐式地转换成double.

    c. tinyint、smallint、int都可以转换为float.

    d. boolean类型不可以转换为任何其它的类型。
    ```


  - 方式二: 显示转换, 可以借助**cast函数**完成显示的类型转换


#### 2.2.2 Hive的字段分割符

- Hive数据表的 默认分隔符是: '\001'
- 可以通过`row format delimited fieldsterminated by '\t'`在创建表的时候修改


#### 2.2.3 内部表和外部表

- 内部表(管理表), 管理表意味着Hive会完全接管该表, 包括元数据和HDFS中的数据. 而外部表则意味着Hive只接管元数据, 而不完全接管HDFS中的数据. 所以删除时, hive只会删除外部表的**元数据**.
<p>

- 外部表的地址可以是任何地址, 需要**location**指定. 内部表的数据存储位置默认在**warehouse**下的数据库内.

- MySQL 数据库中的database `hive`中的数据表 `TBLS`记载着hive所有数据表的信息
<p>




- 内部表建表: 内部表建表不加修饰词即可.

```sql

create table database_name.table_name (column1 string，column2 string)
```

- 外部表建表: 外建表 和 数据 是**相互独立**的, 这是通过 **location**关键字关联.



```sql

# 先创建外部表, 再移动数据到LOCATION目录
# 先检查不存在 /tmp/test_ext目录
hadoop fs -ls /tmp

create external table test_ext(id int, name string) row format delimited fields terminated by '\t' location 'tmp/test_ext';
#可以看到/tmp/test_ext被创建
# 上传数据
hadoop fs -put test_ext.txt /tmp/test_ext


```



```sql
# 内部表转外部表
alter table t1 set tblproperties('EXTERNAL' = 'TRUE');
# 外部表转内部表
alter table t2 set tblproperties('EXTERNAL' = 'FALSE');
```


#### 2.2.4. 分区表

- Hive分区是把数据按照某个属性分成不同的数据子集。

<p>

- 在Hive中，数据被存储在HDFS中，每个分区实际上对应HDFS下的一个文件夹，这个文件夹中保存了这个分区的数据。

<p>

- 因此，在Hive中使用分区，实际上是将数据按照某个属性值进行划分，然后将相同属性值的数据存储在同一个文件夹中。Hive分区的效率提升主要是因为，当进行查询操作时，只需读取与查询相关的数据分区，避免了全表扫描，节约了查询时间。

<p>

- Hive分区的主要作用是:

  - 提高查询效率: 使用分区对数据进行访问时，系统只需要读取和此次查询相关的分区，避免了全表扫描，从而显著提高查询效率。
<p>

  - 降低存储成本: 分区可以更加方便的删除过期数据，减少不必要的存储。






```sql

CREATE TABLE IF NOT EXISTS t_student (
sno int,
sname string
) partitioned by(grade int)
row format delimited fields terminated by '\t';
--  分区的字段不要和表的字段相同。相同会报错error10035

-- 载入数据
-- 将相应年级一次导入
load data local inpath '/usr/local/soft/bigdata29/grade2.txt' into table t_student partition(grade=2);


-- 查看分区
show partitions t_student;
```


- **动态分区（DP）**: 静态分区与动态分区的主要区别在于静态分区是手动指定，而动态分区是通过数据来进行判断。详细来说，静态分区的列是在编译时期通过用户传递来决定的；动态分区只有在SQL执行时才能决定。开启动态分区首先要在hive会话中设置如下的参数


```sql
# 表示开启动态分区
set hive.exec.dynamic.partition=true;
set hive.exec.dynamic.partition.mode=nonstrict;
# 动态分区建表语句与静态分区相同

```


#### 2.2.5. 分桶表

- 分区提供了一个隔离数据和优化查询的便利方式，不过并非所有的数据都可形成合理的分区，尤其是需要确定合适大小的分区划分方式. 不合理的数据分区划分方式可能导致有的分区数据过多，而某些分区没有什么数据的尴尬情况分桶是将数据集分解为更容易管理的若干部分的另一种技术。

<p>

- Hive采用对列值哈希

- Hive分桶是将数据划分为若干个存储文件，并规定存储文件的数量。

  - Hive分桶的实现原理是将数据按照某个字段值分成若干桶，并将相同字段值的数据放到同一个桶中。在存储数据时，桶内的数据会被写入到对应数量的文件中，最终形成多个文件。

<p>

- 分桶的主要作用是:

  - 提高join查询( 数据聚合)效率: 获得更高的查询处理效率。桶为表加上了额外的结构，Hive 在处理有些查询时能利用这个结构。具体而言，连接两个在（包含连接列的）相同列上划分了桶的表，可以使用 Map 端连接 （Map-side join）高效的实现。比如JOIN操作。对于JOIN操作两个表有一个相同的列，如果对这两个表都进行了桶操作。那么将保存相同列值的桶进行JOIN操作就可以，可以大大较少JOIN的数据量。

  - 同理 过滤/分组 的性能也会提升

  <p>

  - 均衡负载: 数据经过分桶后更容易实现均衡负载，数据可以分发到多个节点中，提高了查询效率。

  - 方便抽样: 使取样（sampling）更高效。在处理大规模数据集时，在开发和修改查询的阶段，如果能在数据集的一小部分数据上试运行查询，会带来很多方便

<p>

- **分桶Vs分区：** 综上所述，分区和分桶的区别在于其提供的性能优化方向不同。分区适用于对于数据常常进行的聚合查询数据分析，而分桶适用于对于数据的均衡负载、高效聚合等方面的性能优化。当数据量较大、查询效率比较低时，使用分区和分桶可以有效优化性能。分区主要关注数据的分区和存储，而分桶则重点考虑数据的分布以及查询效率。



```sql

set hive.enforce.bucketing=true;
create table myhive.psn_bucket
(
id int,
name string,
age int
)
clustered by(age) into 4 buckets
row format delimited fields terminated by '\t';

# 分桶表只能用 insert select插入数据, load data不行
# 向分桶表加载数据 (data load), 必须先建一个中转表
insert overwrite table myhive.psn_bucket select * from myhive.temp cluster by(age)
```


#### 2.2.6 修改表操作

- **重命名数据表**: `ALTER TABLE table_name RENAME TO new_table_name;`
<p>

- **添加列**: `ALTER TABLE table_name ADD COLUMNS (col_name data_type [COMMENT col_comment], ...);`
<p>


- **删除列**: `ALTER TABLE table_name REPLACE COLUMNS (col_name data_type [COMMENT col_comment], ...);`
<p>

- **修改列名**: `ALTER TABLE table_name CHANGE old_col_name new_col_name data_type [COMMENT col_comment];`
   - 注意: 只能修改列名, 不能修改列的类型, 如果需要修改列的类型, 需要使用`REPLACE COLUMNS`语句.


<p>

- **添加分区**: `ALTER TABLE table_name ADD PARTITION (part_col_name=part_col_value);`
- **删除分区**: `ALTER TABLE table_name DROP PARTITION (part_col_name=part_col_value);`

<p>

- **修改分区值**: `ALTER TABLE table_name PARTITION (part_col_name=part_col_value) RENAME TO PARTITION (new_part_col_name=new_part_col_value);`


<p>

- **修改表属性**: `ALTER TABLE table_name SET TBLPROPERTIES (property_name=property_value, ...);`
  - 注意hdfs上的实体文件夹名字不会改变, 只是表的元数据发生了变化


- **清空表数据**: `TRUNCATE TABLE table_name;`
   - 不能清空外部表的数据, 只能清空内部表的数据.


#### 2.2.7 复杂数据类型
- Hive支持复杂数据类型, 包括: `array`, `map`, `struct`


- **array**: 数组类型, 例如: `array<int>`表示一个整型数组, `array<string>`表示一个字符串数组.
   - 建表语句 :
   
   ```sql
   creat table myhive.test_array(name string, work_locations array<string>)
   row format delimited fields terminated by '\t'
   COLLECTION ITEMS TERMINATED BY ',';   #这里指定数组内元素的分隔符
   ```

  ```sql

  # 找到每个人工作的第一个城市
  select name, work_locations[0] from myhive.test_array; 
  # 统计每个工作过城市的个数
  select name, size(work_locations) from myhive.test_array;
  # 找找谁在天津工作过
  select * from myhive.test_array where ARRAY_CONTAINS(work_location, '天津') 
  ```

- **map**: Kay-Value格式的数据
   - 字段与字段之间分隔符为',' ; 需要map字段之间的分隔符: '#' ; kay 与 value之间 ':'

  ```sql
  
  create table myhive.test_map(
  name string,
  member map<string, string>
  )
  row format delimited 
  fields terminated by ',' 
  collection items terminated by '#' 
  map keys terminated by ':'; #map 中的key与value的分隔符


  #查看map values
  select name, members['father'], members['mother'] from myhive.test_map;
  
  #取出map的全部keys, 返回类型是array
  select map_keys(members)  from myhive.test_map;

  # 看谁有sister这个key
  select * from myhive.test_map where ARRAY_CONTAINS(map_keys(members),'sister') ;
  # 看谁有王琳这个value
  select * from myhive.test_map where ARRAY_CONTAINS(map_values(members),'王琳') ;
  ```


- **struct**:
  - 结构体类型, 例如: `struct<field1:data_type, field2:data_type>`表示一个包含多个字段的结构体.
  - 字段之间#分割, struct之间冒号分割
  - 建表语句 :
  
  ```sql
  create table myhive.test_struct(name string, address struct<city:string, state:string>)
  row format delimited fields terminated by '#';
  collection items terminated by ':'

  ```
  
  ```sql
  # 查询结构体中的字段
  select name, address.city, address.state from myhive.test_struct;

  ```


### 2.3. 数据加载与导出

- **从hdfs加载**: 原文件会消失, 因为操作的本质是移动文件位置
```sql
#myhive是database
#test_load是数据表

load data inpath '/tmp/search_log.txt' overwrite into table myhive.test_load
```

- **从linux本地加载**: 原文件不会消失
```sql
load data local inpath '/home/hadoop/search_log.txt' overwrite into table myhive.test_load
```

- 使用**select**语法加载数据

```sql 

# example
insert into table table1 select * from table2;
insert overwrite table table1 select * from table2;

```

- **insert overwrite**方式导出: 将hive表中的数据导出到其他任意目录, 例如Linux本地硬盘, 或者hdfs, 或者mysql
```sql

# 语法
insert overwrite [local] directory 'path' select_statement1 FROM from_statement;

# example
insert overwrite local directory '/home/hadoop/export1' select * from myhive.test_load;
insert overwrite local directory '/home/hadoop/export2' row format delimited fields terminated by '\t' select * from myhive.test_load;

insert overwrite directory '/tmp/export1' select * from myhive.test_load;
```


- **hive shell下导出数据:**

```
bin/hive -e "select * from myhive.test_load;" > /home/hadoop/export/export4.txt
bin/hive -f export.sql > /home/hadoop/export/export4.txt
```

### 2.4. 数据查询


- **group**

  - 用于将数据分组, 例如: `group by field_name`
  - `group by`后面可以跟多个字段, 例如: `group by field1, field2`
  - `group by`后面可以跟`order by`, 例如: `group by field1, field2 order by field3` 

- **having**

  - 用于对分组后的数据进行过滤, 例如: `having count(*) > 10`
  - `having`后面可以跟多个条件, 例如: `having count(*) > 10 and sum(field1) < 100`
  - `having`后面可以跟`order by`, 例如: `having count(*) > 10 order by field1`
  - `having`后面可以跟`limit`, 例如: `having count(*) > 10 limit 10`
  - `having`后面可以跟`order by`, 例如: `having count(*) > 10 order by field1 limit 10`

- **having和where的区别**

  - `where`用于对原始数据进行过滤, 而`having`用于对分组后的数据进行过滤
  - `where`在`group by`之前执行, 而`having`在`group by`之后执行
  - `where`不能使用聚合函数, 而`having`可以使用聚合函数


- **order**

  - 用于对数据进行排序, 例如: `order by field_name`
  - `order by`后面可以跟多个字段, 例如: `order by field1, field2`
  - `order by`后面可以跟`limit`, 例如: `order by field1, field2 limit 10`

- **limit**

  - 用于限制查询结果的条数, 例如: `limit 10`
  - `limit`后面可以跟`offset`, 例如: `limit 10 offset 5`
  - `limit`后面可以跟`order by`, 例如: `limit 10 order by field1, field2` 

- **cluster**

  - 用于对数据进行分桶, 例如: `cluster by field_name`
  - `cluster by`后面可以跟多个字段, 例如: `cluster by field1, field2`
  - `cluster by`后面可以跟`order by`, 例如: `cluster by field1, field2 order by field3` 
  - `cluster by`后面可以跟`limit`, 例如: `cluster by field1, field2 limit 10`
  - `cluster by`后面可以跟`order by`, 例如: `cluster by field1, field2 order by field3 limit 10`

- **distribute**

  - 用于对数据进行分布式处理, 例如: `distribute by field_name`
  - `distribute by`后面可以跟多个字段, 例如: `distribute by field1, field2`
  - `distribute by`后面可以跟`order by`, 例如: `distribute by field1, field2 order by field3` 
  - `distribute by`后面可以跟`limit`, 例如: `distribute by field1, field2 limit 10`
  - `distribute by`后面可以跟`order by`, 例如: `distribute by field1, field2 order by field3 limit 10`
  - `distribute by`后面可以跟`cluster by`, 例如: `distribute by field1, field2 cluster by field3`
  - `distribute by`后面可以跟`having`, 例如: `distribute by field1, field2 having count(*) > 10`
  - `distribute by`后面可以跟`group by`, 例如: `distribute by field1, field2 group by field3`
  - `distribute by`后面可以跟`order by`, 例如: `distribute by field1, field2 order by field3` 


### 2.5. 函数




- **聚合函数**: 用于对一组值进行计算并返回单个值, 例如: `count()`, `sum()`, `avg()`, `max()`, `min()`
- **窗口函数**: 用于在查询结果中进行复杂的分析, 例如: `row_number()`, `rank()`, `dense_rank()`
- **字符串函数**: 用于对字符串进行操作, 例如: `concat()`, `length()`, `lower()`, `upper()`, `substring()`

```sql
# 语法 



select [distinct] select_expr, ... from table_reference [where ...] [group by ...] [having ...] [order by ...] [limit ...];
# example     
select count(*) from myhive.test_load where name='zhangsan' group by name order by count(*) desc limit 10;
select name, count(*) from myhive.test_load where name='zhangsan' group by name order by count(*) desc limit 10;
select name, count(*) from myhive.test_load where name='zhangsan' group by name order by count(*) desc limit 10;
select name, count(*) from myhive.test_load where name='zhangsan' group by name order by count(*) desc limit 10;
select name, count(*) from myhive.test_load where name='zhangsan' group by name order by count(*) desc limit 10;
select name, count(*) from myhive.test_load where name='zhangsan' group by name order by count(*) desc limit 10;
select name, count(*) from myhive.test_load where name='zhangsan' group by name order by count(*) desc limit 10;
select name, count(*) from myhive.test_load where name='zhangsan' group by name order by count(*) desc limit 10;
```

- **日期函数**: 用于对日期进行操作, 例如: `current_date()`, `current_timestamp()`, `date_add()`, `date_sub()`, `datediff()`
- **数学函数**: 用于对数字进行操作, 例如: `abs()`, `ceil()`, `floor()`, `round()`, `rand()`

```sql  
# 语法
select [distinct] select_expr, ... from table_reference [where ...] [group by ...] [having ...] [order by ...] [limit ...];     
```



## 参考

- [Hive3.1.2分区与排序（内置函数）](https://www.cnblogs.com/Act-Kang/p/18255898)
- [黑马大数据学习笔记4-Hive部署和基本操作](https://blog.csdn.net/weixin_45735391/article/details/132013444)