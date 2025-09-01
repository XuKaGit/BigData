- hdfs库
    `- client = KerberosClient(url)`
- Kerberos
    - krbcontext
    - KerberosClient

- PyHive
    - cursor
    - cursor: cur.fetchall()
- hiveserver2

`cur = connection(self.zkServers, "/hiveserver2", "serverUri", "hive", None, self.dbname)
`

- hive 分区 

```
sql = """
load data inpath '{hdfs_path}' into table {table_name} 
partition(
    data_type='{data_type}', 
    version='{version}',
    tag_key='{tag_key}',
    dataset_name='{dataset_name}',
    data_version='{data_version}'
)
""".format(**args)
```

- pyarrow


- hive table vs hdfs file

- spark.yarn.dist.archives

- spark 入口 Python 脚本 vs 分发的依赖文件

- spark client vs 非client模式

- spark local vs yarn 模式


- 表的血缘追踪-- sparktool.py

- spark :  MapType(StringType(), StringType())

- YARN ApplicationMaster

- PyArrow

- datasketch

- ppl

- ftlangdetect

- hive分区与并行度 : 写入表的时候


- RDD3.flatMap(func2)

- RDD3.mapPartitions(func2)

- RDD5 = RDD2.join(RDD4)

- hashmap = RDD5.saveAsMap()

- 数据倾斜


- 序列化问题

- hive分区影响并发度