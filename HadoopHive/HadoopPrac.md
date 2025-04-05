
## 1. Haddop-HDFS


### 1.1 HDFS集群环境部署
- 见文件`EnvBuild.md`


### 1.2. HDFS的shell操作

#### 1.2.1 进程的启停管理

**一键启停脚本** - Hadoop HDFS组件内置了HDFS集群的一键启动脚本
- `$HADOOP_HONE/sbin/start-dfs.sh`的执行原理如下
  - 在**执行此脚本的机器上**启动**SecondaryNameNode**
  - 读取`core-site.xml`的内容(fs.defaultFS项), 确认**NameNode所在的机器**并启动**NameNode**
  - 读取`workers`内容, 确认**DataNode所在机器**并启动全部**DataNode**

- `$HADOOP_HONE/sbin/stop-dfs.sh`的执行原理如下
  - 在**执行此脚本的机器上**关闭**SecondaryNameNode**
  - 读取`core-site.xml`的内容(fs.defaultFS项), 确认**NameNode所在的机器**并关闭**NameNode**
  - 读取`workers`内容, 确认**DataNode所在机器**并关闭全部**DataNode**

**单进程启停**
- `$HADOOP_HONE/sbin/hadoop-daemon.sh`此脚本可以单独控制**所在机器**的进程的启停. 用法`hadoop-daemon.sh (start|status|stop) (namenode|secondarynamenode|datanode)`
-  `$HADOOP_HONE/bin/hdfs`脚本也可以单独控制**所在机器**的进程的启停. 用法`hdfs --daemo (start|status|stop) (namenode|secondarynamenode|datanode)`

#### 1.2.2 文件系统操作命令

- 如何区分Linux文件路径与HDFS文件路径
  - Linux : `file:///`, 比如环境变量配置文件(`/etc/profile`)的路径可以写为 `file:///etc/profile`
  - HDFS : `hdfs://namenode:port/`, 比如我们创建的一个`demo.txt`路径可以写作`hdfs://node1:8020/demo.txt`
  - **但是**通常情况下协议头`file://`, `hdfs://namenode:port/`可以**省略**

- **shell命令行一般格式**: `hadoop fs [generic options]` (老版本)  或 `hdfs dfs [generic options]` (新版本)

<p>

- **创建文件夹(创建HDFS分布式文件系统中文件夹):** `hadoop fs -mkdir [-p] <path> ...`  / `hdfs dfs -mkdir [-p] <path> ...`

<p>

- **查看HDFS文件系统内容**: `hdfs dfs -ls [-h] [-R] <path> ...`

<p>

- **上传文件到HDFS指定目录下** : ```hdfs dfs -put [f] [-p] <localsrc >  ... <dst>```. 作用:将单个的源文件src或者多个源文件srcs从本地文件系统(linux)拷贝到目标文件系统中（`<dst>`对应的路径, 在HDFS文件系统中）. 也可以从标准输入中读取输入, 写入目标文件系统中.
  - 例子1: `hdfs dfs -put test.txt /data` : 将本地hadoop用户home目录下的`test.txt`文件上传到HDFS文件系统的 `/data`目录下
  - 例子2: `hdfs dfs -put file:///etc/profile hdfs://node1:8020/data`
  - 如果报错`IOException: Got error, status=ERROR, status message , ack with firstBadLink as 39.108.123.147:9866`, 则需要在三台云服务器上打开9866接口
<p>

- **hdfs dfs -cat <path>**: 例子: `hdfs dfs -cat /test/data1.txt`
<p>

- **可以结合管道符读取大文件**: `hdfs dfs -cat <file-path> | more`
<p>

- **下载HDFS文件**: `hdfs dfs -get [-f] [-p] <src> ... <locate>`, 其中<src>是HDFS文件地址, <locate>是我们想要下载文件去的本地Linux系统的地址

<p>

- **拷贝HDFS文件**: `hdfs dfs -cp [-f] <sc> ... <dst>`将HDFS的文件复制到HDFS系统地址. 
<p>

- **追加数据到HDFS文件中**: `hdfs dfs -appendToFile <localsrc> ... <dst>`: 将所给定的本地文件的内容追加到给定的dst文件, dst文件如果不存在, 将创建该文件
<p>

- **HDFS文件移动**: `hdfs dfs -mv <src> ... <dst>`
<p>

- **HDFS文件删除**: `hdfs dfs -rm -r [-skipTrash] URI`

- **设置回收站(Trash)**: 回收站默认关闭, 如果要打开要在`core-site.xml`设置. 

#### 1.2.3. HDFS权限操作 

#### 1.2.4. HDFS客户端 - Jetbrians产品插件

参考[Big Data Tools完整攻略，一键连接Hadoop](https://blog.csdn.net/weixin_44155966/article/details/108820920)

- 1 . 在 `PyCharm/DataGrip/IntelliJ`中安装`Big Data Tools`插件
- 2. 配置Windows
  - 2.1. 解压Hadoop安装包到Window系统, 如解压到 `D:\hadoop-3.3.4`
  - 2.2. 设置`$HADOOP_HOME`环境变量指向: `D:\hadoop-3.3.4`
  - 2.3. 设置环境变量Path
  - 2.4. 设置环境变量HAOOP_USER_NAME
  - 2.5. 下载 `hadoop.dll` , `winutils.exe` (github)
  - 2.6. 将 `hadoop.dll` , `winutils.exe` 放入 `$HADOOP_HOME/bin`中
  - 2.7. 将`hadoop.dll`放入c盘指定目录里 ([Big Data Tools完整攻略，一键连接Hadoop](https://blog.csdn.net/weixin_44155966/article/details/108820920))


## 2. YARN & MapReduce

### 2.1 YARN/MapReduce集群环境部署
- 见文件`EnvBuild.md`


### 2.2. YARN/MapReduce的shell操作


#### 2.2.1 进程的启停管理

**一键启停脚本** - Hadoop YARN内置了集群的一键启动脚本
- `$HADOOP_HONE/sbin/start-yarn.sh`的执行原理如下
  - 读取`yarn-site.xml`的内容, 确认**ResourceManager所在的机器**并启动**RM**
  - 读取`workers`内容, 确认**NM所在机器**并启动全部**NM**
  - 当前机器启动**proxyServer** (代理服务器)

- `$HADOOP_HONE/sbin/stop-yarn.sh` 可以停止 yarn的  `RM/NM/proxyServer`, 但是无法关闭历史服务器  **(historyServer)**



**单进程启停**

-  `$HADOOP_HONE/bin/yarn`脚本也可以单独控制**所在机器**的进程的启停. 用法`yarn --daemo (start|status|stop) (resourcemanager|nodemanager|proxyserver)`
<p>

- `mapred --daemon (start|stop) historyserver`可以停止**所在机器**的**历史服务器**


#### 2.2.2 提交MapReduce程序到YARN执行

- YARN作为资源调度管控框架, 其本身提供资源供许多程序运行, 常见的有: `MapReduce程序, Spark程序, Flink程序`

- `Hadoop`官方内置了一些预置的`MapReduce`程序代码, 我们无需编程, 只需要通过命令即可使用. 这些内置的示例MapReduce程序代码, 都在`$HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.1.jar` 这个文件内. 常用的有2个MapReduce内置程序:

  - wordcount: 单词计数程序.统计指定文件内各个单词出现的次数
  - pi: 求圆周率, 通过蒙特卡罗算法求圆周率

- 对于上述的内置实例程序, 我们可以通过 `hadoop jar` 命令来运行它, 提交MapReduce程序到YARN中. 语法`hadoop jar 程序文件 java类名 [程序参数] … [程序参数]`

  - **蒙特卡罗算法求圆周率**: `hadoop jar /export/server/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.4.jar pi 3 1000`

  - 报错处理参考: [Hadoop中解决INFO ipc.Client: Retrying connect to server的问题](https://blog.csdn.net/zhugongshan/article/details/103819830#:~:text=%E6%89%BE%E5%88%B0%2Fetc%2F%20hosts,%E6%96%87%E4%BB%B6%EF%BC%8C%E7%94%A8sudo%E5%91%BD%E4%BB%A4%E6%89%93%E5%BC%80%EF%BC%8C%E5%B0%86127.0.0.1%E5%92%8C127.0.1.1%E7%9A%84%E6%98%A0%E5%B0%84%E6%B3%A8%E9%87%8A%E6%8E%89%E5%8D%B3%E5%8F%AF%E3%80%82%20%E6%B3%A8%E6%84%8F%EF%BC%9A%E5%A6%82%E6%9E%9C%E5%8F%8A%E8%AE%BE%E8%AE%A1%E7%9A%84%E6%98%AF%E5%88%86%E5%B8%83%E5%BC%8F%E7%9A%84%EF%BC%8C%E5%B0%B1%E8%A6%81%E6%8A%8Amaster%E5%92%8Cslave%E4%B8%AD%E7%9A%84hosts%E6%96%87%E4%BB%B6%E9%83%BD%E8%A6%81%E4%BF%AE%E6%94%B9%EF%BC%8C%E4%BC%AA%E5%88%86%E5%B8%83%E5%BC%8F%E7%9A%84%E5%B0%B1%E6%97%A0%E6%89%80%E8%B0%93%E4%BA%86%EF%BC%8C%E5%9B%A0%E4%B8%BA%E5%AE%83%E5%8F%AA%E6%9C%89%E4%B8%80%E4%B8%AA%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E3%80%82%20%E6%9C%80%E5%90%8E%EF%BC%8C%E9%9C%80%E8%A6%81%E6%B3%A8%E6%84%8F%E7%9A%84%E6%98%AF%EF%BC%9A%E5%A6%82%E6%9E%9C%E4%BD%A0%E6%98%AF%E4%BC%AA%E5%88%86%E5%B8%83%E5%BC%8F%E7%9A%84%EF%BC%8C%E5%8F%AA%E7%94%A8%E9%85%8D%E7%BD%AE%E4%B8%80%E5%8F%B0%EF%BC%8C%E5%A6%82%E6%9E%9C%E4%BD%A0%E6%98%AF%E5%88%86%E5%B8%83%E5%BC%8F%E7%9A%84%EF%BC%8C%E5%B0%B1%E8%A6%81%E6%8A%8A%E6%89%80%E6%9C%89%E7%9A%84%E4%B8%BB%E6%9C%BA%E7%9A%84hosts%E6%96%87%E4%BB%B6%E7%9A%84%E5%89%8D%E4%B8%A4%E8%A1%8C%EF%BC%88%E5%9F%BA%E6%9C%AC%E4%B8%8A%E9%83%BD%E5%9C%A8%E5%89%8D%E4%B8%A4%E8%A1%8C%EF%BC%89%E5%85%A8%E9%83%A8%E6%B3%A8%E9%87%8A%E6%8E%89%E3%80%82), 以及[Error: INFO ipc.Client: Retrying connect to server: Already tried XXX time(s).](https://blog.csdn.net/sinat_38079265/article/details/122904393)
`