
## WordCount



**1. 创建数据**, 在 `/root/data.txt`-----`vim data.txt`


```
hadoop spark
hive spark hive hive spark

hadoop spark spark hive 
hive spark hive hive spark spark

hadoop spark hive hive
hive spark hive hive spark
```

**2. 实现思路**
```
读取文件, 将文件的数据变成分布式集合数据集RDD
先过滤, 将空行过滤掉
将每一行多个单词转化为一行一个单词, 形如:
'hive' 
'spark' 
'hive'
'hive'
'spark'

然后将每个单词转化为key-value的二元组(word,1), 形如:
('hive',1)
('spark',1)
('hive',1)
('hive',1)
('spark',1)

接着按照key进行分组, 形如:
('hive', [1,1,1])
('spark', [1,1,1,1])

最后对每个分组内的数据进行聚合, 形如:
('saprk', 4)
('hive', 3)
......
```


**3. 代码实现**

```python

# map: spark算子, 一对一处理
# flatMap: spark算子, 一对多处理; 即将一行多个元素转换成一行一个元素
     [[1,2], [3,4,5], [6,7,8,9]]   ---->   [1,2,3,4,5,6,7,8,9]
#filter
# foreach


fileRdd = sc.textFile('/root/data.txt')
fileRdd.count() # 统计文件行数
fileRdd.take(3) # 查看前3行数据

fileRdd = fileRdd.filter(lambda line: len(line.strip()) > 0) # 过滤掉空行
fileRdd.count() # 统计过滤后的行数

fileRdd = fileRdd.flatMap(lambda line: line.strip().split()) # 将每行数据拆分成多个单词
fileRdd.count() # 统计拆分后的单词数

tupleRdd = fileRdd.map(lambda word: (word,1)) # 将每个单词转化为key-value的二元组(word,1)

groupRdd = tupleRdd.groupByKey() # 按照key进行分组

resultRdd = groupRdd.map(lambda kv: (kv[0], sum(kv[1]))) # 对每个分组内的数据进行聚合
resultRdd.count() # 统计聚合后的个数

resultRdd.saveAsTextFile('/root/result.txt') # 将结果保存到文件中
```

