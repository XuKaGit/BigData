# Introduction to Hadoop


**什么是Hadoop:** 狭义上Hadoop指的是Apache软件基金会的一款开源软件. 用java语言实现, 开源. 允许用户使用简单的编程模型实现跨机器集群, 对海量数据进行分布式计算处理. 广义上Hadoop指的是围绕Hadoop打造的**大数据生态圈**

- **Hadoop核心组件:**
  - 基于**HDFS**的分布式数据储存
  - 基于**MapReduce**的分布式数据计算 ( 提供编程接口供用户开发分布式计算程序)
  - 基于**YARN**的分布式资源调度

- **Hadoop发行版本:** 开源社区版( Apache)与 商业发行版( CDH, 星环)


## 1. 分布式与Hadoop集群

### 1.1 分布式的基础架构

大数据体系中, 分布式的调度主要有2类架构模式:
- **去中心化模式**: 没有明确的中心, 众多服务器之间基于特定规则进行同步协调
- **中心化模式** (Master and Slaves ): 有一个节点作为中心, 统一调度其它节点, Hadoop就是中心化模式架构


### 1.2 Apache Hadoop集群整体概述
Hadoop集群包括两个集群: `HDFS集群`, `YARN集群`. 这两个集群**逻辑上分离**(两个集群互相之间没有依赖,互不影响), 但是通常**物理上在一起**(某些角色进程往往部署在同一台物理服务器上). 两个集群都是标准的主从架构集群. 而`MapReduce`是计算框架,代码层面的组件, 没有集群之说.



#### 1.2.1 HDFS的基础架构
HDFS是Hadoop三大组件之一, 全称Haddop Distracted File System.
- HDFS采用中心化模式(主从模式): 在一个HDFS集群中有: **NameNode**(主角色), **DataNode**(从角色), **SecondaryNameNode**(主角色的辅助角色).

<div style="text-align: center;">
    <img src="Figures\HDFS架构.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>

- **NameNode**: HDFS系统中的主角色, 是一个独立的进程. 负责管理整个系统和DataNode

- **DataNode**: HDFS的从角色, 是一个独立的进程. 主要负责数据的存储和取出

- **SecondaryNameNode**: NameNode的辅助, 也是一个独立的进程, 抓哟帮助NameNode完成元数据的整理工作

#### 1.2.2 YARN的基础架构

YARN集群主要负责资源管理和任务调度，它当中的主角色叫做`ResourceManager`, 简称`RM`; 从角色叫做`NodeManager`, 简称`NM`


## 2. HDFS分布式文件系统基础


HDFS通过许多设计试图解决分布式/集群化存储的问题, 这些问题包括: 1. 文件分布在不同机器上不利于寻找; 2. 文件过大导致单机存不下, 上传下载效率低; 3. 硬件故障难以避免, 数据易丢失 ; 4. 在多台计算机存储文件的前提下, 如何能够提供统一的访问接口,像是访问一个普通文件系统一样使用分布式文件系统...




### 2.1 元数据管理

针对`文件分布在不同机器上不利于寻找`这个问题, HDFS通过在NameNode上存储元数据来解决. 

- **数据**: 指存储的内容本身, 比如文件,视频,图片等; 这些数据底层最终是存储在磁盘等存储介质上的, 一般用户无需关心, 只需要基于目录树进行增删改查即可, 实际针对数据的操作由文件系统完成.

- **元数据(metadata)**: 又称之为解释性数据, 记录数据的数据; 文件系统元数据一般指文件大小,最后修改时间,底层存储位置,属性,所属用户,权限等信息.

- Namenode管理的元数据具有两种类型:
  - 文件自身属性信息: 文件名称, 权限, 修改时间, 文件大小, 复制因子, 数据块大小.
  - 文件块位置映射信息: 记录文件块(block)和DataNode之间的映射信息, 即哪个块位于哪个节点上. 

<p>

- **Hadoop**基于一批**edits**和一个**fsimage**文件的配合完成对所有存储的文件的管理

- **edits文件**是一个**流水账文件**, 记录hdfs中的每一次操作, 以及本次操作影响的文件及其对应的block. 



- **fsimage文件**是所有**edits**文件合并后得到的最终的, 统一的吧结果. 

- **元数据合并的参数设定**: 可以设置edits文件合并的频率, 默认的一个小时(3600s)合并一次/达到一百万次事务 合并一次. 对元数据进行合并的是SecondaryNameNode. 


### 2.2. Blocks

- HDFS中的文件在物理上是分块存储(`block`)的, 默认大小是`128M(134217728)`, 不足`128M`则本身是一块. 块的大小可以通过配置参数来规定, 参数位于`hdfs-default.xml`中`dfs.blocksize`

- 文件的各个block的具体存储管理由DataNode节点承担. 每一个block都可以在多个DataNode上存储.

- **HDFS的Block为什么这么大:** 是为了最小化查找( seek )时间, 控制定位文件与传输文件所用的时间比例. 假设定位到Block所需的时间为10ms, 磁盘传输速度为100M/s.如果要将定位到Block所用时间占传输时间的比例控制1%，则Block大小需要约100M.  



### 2.3. HDFS副本管理

文本的所有`block`都会有副本. 副本系数可以在文件创建的时间指定, 也可以在之后通过命令改变. 
副本数由文件`hdfs-site.xml`中参数`dfs.replication`控制, 默认值是**3**, 也就是会额外再复制**2**份, 连同**本身**总共**3**份副本. 


### 2.4 HDFS文件系统结构与Namespace

- HDFS支持传统的层次型文件组织结构 (即与**Linux**一样, 均是以 **/** 作为根目录的树形目录组织形式). 用户可以创建目录, 然后将文件保存在这些目录里. 文件系统**namespace**的层次结构和大多数现有的文件系统类似, 用户可以创建,删除,移动或重命名文件.
<p>

- Namenode负责维护文件系统的namespace, 任何对文件系统名称空间或属性的修改都将被Namenode记录下来. 换句话说Namenode记录了namespace中每一个路径(文件)所对应的数据块信息. 
<p>

- HDFS会给客户端提供一个统一的抽象目录树，客户端通过路径来访问文件，形如: `hdfs://node1:9820/dir-a/dir-b/dir-c/file.data`



### 2.5. HDFS文件读写流程

#### 2.5.1 写入

- 1. **客户端请求:**客户端向`NameNode`发送写入请求. 
- 2. **NameNode确认:** `NameNode`接收请求,审核权限和剩余课件后, 向客户端报告写入的`DataNode`的地址.
- 3. **数据包准备**: 客户端将数据分成数据包, 并将其放入数据包队列中.
 
- 4. **数据副本传递:** `DataNode`接收到数据后, 复制数据并向下一个`DataNode`传递数据, 直到所有副本都写入完成. 
- 5. **写入完成通知:** 所有`DataNode`确认接收到数据包后, 最终向`NameNode`报告写入完成, `NameNode`更新元数据记录.

**注意事项**:
  - 注意`NameNode`不负责数据写入, 只负责元数据记录与权限审批
  - 客户端直接向一台 `DataNode` 写数据, 这台 `DataNode` 通常是距离客户端最近(网络距离最短的).
  - 数据块副本的复制由 `DataNode` 之间自行完成, 通过`Pipeline` 方式按顺序复制



#### 2.5.2. 读取


- 1. **客户端请求:** 客户端向`NameNode`发送读取文件的请求.
- 2. **NameNode返回信息:** `NameNode`根据请求返回文件的块(block)列表及其所在的`DataNode位置`
- 3. **数据块定位:** 客户端根据返回的块列表, 直接向相应的`DataNode`请求数据.
- 4. **数据传输:** `DataNode`将请求的数据块发送给客户端, 完成数据读取.

### 2.6. HDFS强弱项

- HDFS上的应用主要是以流式读取数据(**Streaming Data Access**). 即HDFS基于这样的一个假设: 最有效的数据处理模式是一次写入, 多次读取(**write-one-read-many**).因此读取整个数据集所需时间比读取第一条记录的延时更重要 (或者说相较于数据访问的反应时间, 更注重数据访问的高吞吐量). 
<p>

- **适合场景:**  大文件, 数据流式访问, 一次写入多次读取, 低成本部署, 廉价PC, 高容错
<p>

- **不适合场景:**  
   - 小文件: 文件的元数据(如目录结构, 文件block的节点列表, block-node mapping)保存在NameNode的内存中, 整个文件系统的文件数量会受限于NameNode的内存大小.依照经验而言, 一个文件/目录/文件块一般占有`150字节`的元数据内存空间. 如果有100万个文件，每个文件占用1个文件块，则需要大约`300M`的内存。因此十亿级别的文件数量在现有商用机器上难以支持.
   - 数据交互式访问; 频繁任意修改; 低延迟处理



## 3. 分布式计算与MapReduce

分布式计算分为: **分散-汇总模式** Vs **中心调度-步骤执行模式**

- **分散-汇总模式**: `MapReduce`
- **中心调度-步骤执行模式**: `Spark`, `Flink`

- `MapReduce`是分散-汇总模式的分布式计算架构, 它提供两个两个编程接口: Map(分散) 和 Reduce(汇总).


### 3.1. MapReduce的计算过程

**mapreduce**的计算过程分为5个阶段: **split**, **map**, **shuffle**, **reduce**, **write**


<p>

- **split**: 指的是将源文件划分为大小相等的小数据块( 默认 128MB ). 并执行**格式化**操作, 即将划分好的分片( 小数据块)格式化为键值对 **<key,value>** 形式的数据, 其中, **key** 代表**偏移量**, **value** 代表每一行内容.

<p>


- **Map**: Hadoop 会为每一个分片构建一个 Map 任务, 并由该任务运行自定义的 `map()` 函数, 从而处理分片里的每一条记录. 
  - 每个 Map 任务都有一个**内存缓冲区**(缓冲区大小 **100MB** ), 输入的分片数据经过 Map 任务处理后的中间结果会写入内存缓冲区中. 如果写入的数据达到内存缓冲的阈值( **80MB** ), 会启动一个线程将**内存**中的溢出数据写入**磁盘**, 同时不影响 Map 中间结果继续写入缓冲区. 
  - 在溢写过程中,  MapReduce 框架会对 key 进行**排序**, 如果中间结果比较大, 会形成多个溢写文件.
  - **最后的缓冲区数据也会全部溢写入磁盘形成一个溢写文件**, 如果是多个溢写文件, 则最后**合并所有的溢写文件为一个文件**.


<p>

- **Shuffle**: `Shuffle` 是 Map 和 Reduce 之间的数据传输过程. 在 Map 阶段, 每个 Map 任务都会输出一组**中间键值对**. **Shuffle** 会将 MapTask 输出的处理结果数据分发给 ReduceTask , 并在分发的过程中, 对数据按 **key** 进行分区和排序. 分区数与 Reduce 任务数相同. 





- **Reduce阶段**: Reduce任务接收来自Map任务的中间键值对  `(<key, {value list}>)`, 并对每个键执行用户定义的Reduce函数, 最终以`<key, value>`的形式输出.


- **Write**: 将Reduce阶段输出的结果(`<key, value>`) 写入到HDFS中.



<div style="text-align: center;">
    <img src="Figures\MapRed1.png" style="width: 80%; max-width: 600px; height: auto;">
</div>



<div style="text-align: center;">
    <img src="Figures\MapRed2.png" style="width: 80%; max-width: 600px; height: auto;">
</div>




### 3.3. MapReduce的编程模型








## 4. YARN

### 4.1 YARN概述



- **Definition:** `YARN` (Yet Another Resource Negotiator, 另一种资源协调者) 是一种新的Hadoop资源管理器. YARN是一个通用资源管理系统和调度平台, 可为上层应用提供统一的资源管理和调度. 我们可以将YARN理解为一个分布式的操作系统平台, 而MapReduce等计算程序则相当于运行于操作系统之上的应用程序, YARN为这些程序提供运算所需的资源(内存、CPU等)


- **YARN功能说明**
  - **资源管理系统:** 集群的硬件资源, 和程序运行相关, 比如内存,CPU等.  (磁盘由`HDFS`管理)
  - **调度平台:** 多个程序同时申请计算资源如何分配, 调度的规则.
  - **通用:** 不仅仅支持MapReduce程序, 理论上支持各种计算程序. YARN不关心你干什么, 只关心你要资源, 在有的情况下给你, 用完之后还我



### 4.2 YARN架构

#### 4.2.1 YARN核心架构

- Master`ResourceManager`: YARN集群中的主角色, 决定系统中所有应用程序之间资源分配的最终权限,即最终仲裁者. 接收用户的作业提交, 并通过NM分配,管理各个机器上的计算资源.
<p>

- Slave`NodeManager`: YARN中的从角色, 一台机器上一个, 负责管理本机器上的计算资源. 根据RM命令, 启动Container容器,监视容器的资源使用情况. 并且向RM主角色汇报资源使用情况.

<p>

**Remark:** 何实现服务器上资源的精准分配: **容器**
- NM在服务器上构建一个容器( 提前占用资源, 类似集装箱的概念)
- 然后将容器的资源供给程序使用
- 程序运行在容器内, **无法突破容器的资源限制**

#### 4.2.2 YARN辅助架构

- 代理服务器 (ProxyServer, Web Application Proxy Web): 网络安全维护

- 历史服务器 (JobHistoryServer): 记录器.  (因为程序是运行在容器里的, 所以要统一)


#### 4.2.3 YARN工作流程

- YARN接受到任务时, 会启动 **AppMaster**( 进程 ), AppMaster会向RM申请资源, RM会根据集群资源情况, 返回资源给AppMaster, AppMaster根据返回的资源, 启动**Container**, Container启动后, AppMaster会向Container发送程序, Container接收到程序后, 启动程序运行.



## 5. Reference

- [图文详解 MapReduce 工作流程](https://blog.csdn.net/Shockang/article/details/117970151)
- [MapReduce基本原理及应用](https://www.cnblogs.com/lixiansheng/p/8942370.html)

- [Yarn的ApplicationMaster介绍](https://blog.csdn.net/weixin_38255444/article/details/103208155)
- [Yarn之 MRAppMaster 详解](https://www.jianshu.com/p/b81e4d9495d7)