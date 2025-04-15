[TOC]

## 云计算平台配置Hadoop/Spark 集群

- 参考1: [基于阿里云服务器搭建完全分布式Hadoop集群+Hive仓库+Spark集群](https://blog.csdn.net/TYUT__pengkai/article/details/112464548)
- 参考2: [B站-黑马程序员大数据入门到实战教程](https://www.bilibili.com/video/BV1WY4y197g7?spm_id_from=333.788.videopod.episodes&vd_source=ea310d614abfa357560d43c5ecb9fcfd&p=4)

### 1. 云服务器的选择

推荐使用 腾讯云, 阿里云；系统选择 CentOS 或 Ubuntu. 一共三台服务器, 一个同时作为**NameNode, DataNode和SecondaryNameNode** (node1), 两个**DataNode**(node2, node3). 在此文中, 笔者将node1放在华为云服务器上, node2放在腾讯云上, node3放在阿里云上.

### 2. 云服务器配置

云服务器需要三步配置: 主机名映射, 设置SSH免密, 以及JDK环境搭建.

#### 2.0 更改主机名 (可选)
- 为了方便操作, 可以将三台服务器的主机名使用`hostname`命令修改为node1, node2 , node3. 

#### 2.1 主机名映射

- 第一步是建立ip映射,由于是云端服务器,我们直接使用真实的**公网ip**.**每台**服务器内均配置此文件(对应的服务器对自己操作时最好用自己的**内网ip**). 

- 以作为node1的服务器为例, 在命令行输入 `vim /etc/hosts`并在文件中**最前面**添加:
    ```
    node1私网ip    node1
    node2公网ip    node2
    node3公网ip    node3
    ```
    接着**ping**一下node2, node3看可否连接 (华为云用户需要可以参考[弹性公网IP Ping不通?](https://support.huaweicloud.com/ecs_faq/zh-cn_topic_0105130172.html#ZH-CN_TOPIC_0105130172__section1715910911214)). 

#### 2.2 SSH免密

##### 2.2.1 root用户SSH免密

- **生成公私钥**: 这一步需要在三台服务器上分别进行. 使用命令`ssh-keygen -t rsa -b 4096`生成公私钥, 随后, 会出现一系列交互式操作, 一路"回车键"即可, 生成的公私钥默认保存在`/root/.ssh/id_rsa`目录下. 
<p>

- **分发公钥, 保留私钥**: SSH协议使用非对称加密的方式进行通信, 公钥加密, 私钥解密. 因此, 对于每台服务器来说, 需要将自己的公钥分发给其他服务器. 使用命令`ssh-copy-id hostname` 完成密钥的分发工作, 这里的`hostname`为其他服务器的主机名. (是否要将hostname设置为本机并执行一次, 对于结果并没有影响)
<p>

- **测试通信**: `ssh hostname`即可登录到其他主机，这里的`hostname`为其他服务器的主机名. 要想推出, 直接命令行输入`exit`即可.

##### 2.2.2 hadoop用户SSH免密

在华为云node1和node3阿里云服务器分别创建用户`hadoop`, 密码设置为`12345678`, 在腾讯云node2创建用户`hadoop`, 密码设置为`FdQJawMY5E`. 并为3个hadoop用户设置SSH免密

```
# 在每台服务器上都运行
# 创建用户
adduser hadoop
passwd hadoop
# 进入用户
su - hadoop
# SSH免密
ssh-keygen -t rsa -b 4096
ssh-copy-id node1
ssh-copy-id node2
ssh-copy-id node3
```


#### 2.3 JDK搭建

- 为了尽可能的减少安装的问题和可能出现的错误, 强烈建议选用**相同的Java版本 (JDK 1.8)** 并在不同服务器上将它们安装在**同一目录**下.

- 1. **下载JDK软件压缩包**: 版本选择 `jdk-8u361-linux-x64.tar.gz`
- 2. **创建文件夹**: `mkdir -p /export/server`  (后续所有软件都会安装到此文件夹)
- 3. **解压缩JDK安装文件**: `tar -zxvf jdk-8u361-linux-x64.tar.gz -C /export/server/`

- 4. **重命名**: `mv jdk1.8.0_361/ jdk1.8.0/`
- 5. **配置JAVA_HOME环境变量**:  命令行运行`vim /etc/profile`进入, 并添加
```
# Java enviroment
export JAVA_HOME=/export/server/jdk1.8.0
export JRE_HOME=${JAVA_HOME}/jre
export CLASS_PATH=.:${JAVA_HOME}/lib:${JRE_HOME}/lib
export PATH=.:$JAVA_HOME/bin:$PATH
```
- 6. **生效环境变量**: 命令行运行`source /etc/profile`
- 7. **配置JAVA执行程序软连接**:

    ```
    # 删除系统自带的java程序 (视情况)
    rm /usr/bin/java
    # 软连接我们自己安装的java程序
    ln -s /export/server/jdk1.8.0/bin/java /usr/bin/java
    ```

- 8. **验证执行**:   `java -version`, `javac -version`


### 3. 安装并配置Hadoop

使用**Hadoop3.3.4**


#### 3.1. 主要文件配置


**对于Node1,2,3 执行以下操作：**

- 1. **上传并解压Hadoop安装包**: 解压到`/export/server`中`tar -zxvf hadoop-3.3.4.tar.gz -C /export/server` 

- 2. **重命名**: `cd /export/server` , `mv hadoop-3.3.4/ hadoop/`

**关于Hadoop文件夹里的内容请见附录**

<p>

**修改配置文件**: 配置HDFS集群, 主要涉及修改以下存放于 `/export/server/hadoop/etc/hadoop`中的文件
  
  
- 3. **workers: 配置从节点 DataNode**
 
```
# 进入workers文件
cd etc/hadoop
vim workers
# 删除localhost
# 填入以下内容 (表明集群记录了3个DataNode)
node1
node2
node3
```

- 4. **hadoop-env.sh: 配置Hadoop相关路径**
  
```
vim hadoop-env.sh
#填入以下内容
export JAVA_HOME=/export/server/jdk1.8.0
export HADOOP_HOME=/export/server/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export HADOOP_LOG_DIR=$HADOOP_HOME/logs
```
- 5. **core-site.xml: Hadoop核心配置文件**, 见**附录A2**

```
# 在文件内部填入如下内容
<configuration>
  <property>
  
    <name>fs.defaultFS</name>
    <value>hdfs://node1:9820</value>

  </property>
  
  <property>
    <name>hadoop.tmp.dir</name>
    <value>/export/server/hadoop/tmp</value>
  </property>

  <property>
    <name>io.file.buffer.size</name>
    <value>131072</value>
  </property>
<configuration>
```
- 6. **hdfs-site.xml: HDFS核心配置文件**, 见**附录A3**

```
# 在文件中填入以下内容
<configuration>
  <property>
    <name>dfs.datanode.data.dir.perm</name>
    <value>700</value>
  </property>

  <property>
    <name>dfs.namenode.secondary.http-address</name>
    <value>node1:9868</value>
  </property>

  <property>
    <name>dfs.namenode.http-address</name>
    <value>node1:9870</value>
  </property>

  <property>
    <name>dfs.namenode.name.dir</name>
    <value>/data/nn</value>
  </property>
  
  <property>
    <name>dfs.namenode.hosts</name>
    <value>node1,node2,node3</value>
  </property>

  <property>
    <name>dfs.blocksize</name>
    <value>268435456</value>
  </property>

  <property>
    <name>dfs.namenode.handler.count</name>
    <value>100</value>
  </property>

  <property>
    <name>dfs.datanode.data.dir</name>
    <value>/data/dn</value>
  </property>


  <property>
    <name>dfs.webhdfs.enabled</name>
    <value>true</value>
    <discription>指定可以通过web访问hdfs目录</discription>
  </property>

</configuration>

```


#### 3.2. 其他


**对于Node1,2,3 执行以下操作:**


- 1. **新建数据目录**: 在**node1**创建文件夹`mkdir -p /data/nn`, 在**node1,2,3**创建文件夹`mkdir -p /data/dn`, `mkdir /export/server/hadoop/tmp`
- 2. **配置环境变量**:
```
vim /etc/profile
# 添加
export HADOOP_HOME=/export/server/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
-----执行修改
source /etc/profile
```


- 3. **授权为Hadoop用户**: 为了保证安全, Hadoop系统不用root用户启动. 
```
#以root用户身份, 在node1 node2 node3上进行如下操作
chown -R hadoop:hadoop /data
chown -R hadoop:hadoop /export
```

- 4. **格式化namenode** :


  - **Notice:**格式化其实就是创建了一系列的文件夹, 这两个文件夹的是 **/export/server/hadoop/logs**和 **/export/server/hadoop/tmp**, 如果想要格式化第二次, 需要删除第一次格式化产生的文件夹( 即删除 **/export/server/hadoop/logs**, **/export/server/hadoop/tmp**), 否则会报错.

  <p>

  - 其实可以在格式化前看有哪些文件, 格式化后看有哪些文件, 就可以比较出格式化创建了哪些文件.

```
# 切换到hadoop用户
su - hadoop
# 格式化namenode
hadoop namenode -format
```


<p>





- 5. **启动Hadoop集群**
```
# hadoop用户下执行启动
start-dfs.sh
# hadoop用户下关闭启动
stop-dfs.sh
```
- 6. **网络查看**
在浏览器中搜索`node1公网ip:9870`  (记得在node1云服务器安全组配置9870,9820端口)




### 4. MapReduce运行配置

集群规划:
```
node1: ResourceManager, NodeManager, ProxyServer
node2, node3: NodeManager
```



在每个服务器进行下面所有的配置:



- 编辑`$HADOOP_HOME/etc/hadoop` 下的 `mapred-env.sh`文件并添加如下内容

```
# 设置JDK路径
export JAVA_HOME=/export/server/jdk1.8.0

# 设置JobHistoryServer进程内存为1G
export HADOOP_JOB_HISTORYSERVER_HEAPSIZE=1000

#设置日志级别为INFO
export HADOOP_MAPRED_ROOT_LOGGER=INFO,RFA

```
- 编辑`$HADOOP_HOME/etc/hadoop` 下的 `mapred-site.xml`文件并添加如下内容

```
<configuration>
  
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
    <discription>MapReduce的运行框架运行为YARN</discription>
  </property>

  <property>
    <name>mapreduce.jobhistory.address</name>
    <value>node1:10020</value>
    <discription>历史服务器通讯端口为node1:10020</discription>
  </property>

  <property>
    <name>mapreduce.jobhistory.webapp.address</name>
    <value>node1:19888</value>
    <discription>历史服务器端口为node1的19888</discription>
  </property>

  <property>
    <name>mapreduce.jobhistory.intermediate-done-dir</name>
    <value>/data/mr-history/tmp</value>
    <discription>历史信息在HDFS的记录临时路径</discription>
  </property>

  <property>
    <name>mapreduce.jobhistory.done-dir</name>
    <value>/data/mr-history/done</value>
    <discription>历史信息在HDFS的记录路径</discription>
  </property>

  <property>
    <name>yarn.app.mapreduce.am.env</name>
    <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
    <discription>MapRedece HOME设置为HADOOP_HOME</discription>
  </property>

  <property>
    <name>mapreduce.map.env</name>
    <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
    <discription>MapRedece HOME设置为HADOOP_HOME</discription>
  </property>

  <property>
    <name>mapreduce.reduce.env</name>
    <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
    <discription>MapRedece HOME设置为HADOOP_HOME</discription>
  </property>

</configuration>
```



### 5. YARN集群部署

集群规划:
```
node1: ResourceManager, NodeManager, ProxyServer
node2, node3: NodeManager
```

- 编辑`$HADOOP_HOME/etc/hadoop` 下的 `vim yarn-env.sh`文件并添加如下内容

```
export JAVA_HOME=/export/server/jdk1.8.0
export HADOOP_HOME=/export/server/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export HADOOP_LOG_DIR=$HADOOP_HOME/logs
```


- 编辑`$HADOOP_HOME/etc/hadoop` 下的 `vim yarn-site.xml`文件并添加如下内容

```
<configuration>


  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>node1</value>
    <discription>ResourceManager设置在node1节点</discription>
  </property>

  <property>
    <name>yarn.nodemanager.local-dirs</name>
    <value>/data/nm-local</value>
    <discription>NodeManager中间数据本地存储路径</discription>
  </property>

  <property>
    <name>yarn.nodemanager.log-dirs</name>
    <value>/data/nm-log</value>
    <discription>NodeManager数据日志本地存储路径</discription>
  </property>


  <property>
    <name>yarn.nodemanager.log.retain-seconds</name>
    <value>10800</value>
  </property>


  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
    <discription>为MapReduce程序开启Shuffle服务</discription>
  </property>

  <property>
    <name>yarn.log.server.url</name>
    <value>http://node1:19888/jobhistory/logs</value>
    <discription>历史服务器URL</discription>
  </property>

  <property>
    <name>yarn.web-proxy.address</name>
    <value>node1:8089</value>
    <discription>代理服务器主机和端口</discription>
  </property>

  <property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
    <discription>开启日志聚合</discription>
  </property>

  <property>
    <name>yarn.nodemanager.remote-app-log-dir</name>
    <value>/tmp/logs</value>
    <discription>程序日志HDFS的存储路径</discription>
  </property>

  <property>
    <name>yarn.resourcemanager.scheduler.class</name>
    <value>org.apache.hadoop.yarn.server.resourcemanager.scheduler.fair.FairScheduler</value>
    <discription>选择公平调度器</discription>
  </property>


</configuration>
```




**网络查看**
在浏览器中搜索`node1公网ip:8088`  (记得在node1云服务器安全组配置8088端口)



### 6. Hive配置
- Hive是单机工具, 只需要部署在一台服务器即可. Hive虽然是单机的, 但是它可以提交分布式运行的MapReduce程序运行.
- 为了方便起见, 将Hive本体和元数据服务所需的关系型数据库( MySQL) 都安装在node1上

#### 6.1. MySQL安装
- 我们在node1节点使用yum在线安装MySQL5.7版本

```shell
# 以下所有操作在root用户下执行

#卸载系统自带的mariadb
rpm -qa | grep mariadb | xargs sudo rpm -e --nodeps

#更新密钥
rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022

#安装Mysql yum库
rpm -Uvh http://repo.mysql.com//mysql57-community-release-el7-7.noarch.rpm

# yum安装Mysql
yum -y install mysql-community-server

# 启动Mysql设置开机启动
systemctl start mysqld
systemctl enable mysqld

#检查Mysql服务状态
systemctl status mysqld

#第一次启动mysql, 会在日志文件中生成root用户的一个随机密码, 使用下面命令查看该密码
cat /var/log/mysqld.log | grep 'password' 

#进入mysql  (然后输入密码, 回车)
mysql -uroot -p

#如果你想设置简单密码，需要降低Mysql的密码安全级别
set global validate_password_policy=LOW;
set global validate_password_length=4;

#修改root本机登录密码为123456
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';

#修改远程登录密码, 打开root用户从任意地方的主机远程登录的权限
grant all privileges on *.* to root@"%" identified by '123456' with grant option;  

#刷新权限
flush privileges;

# 按 Ctrl+ d 退出 mysql

```



#### 6. 2. Hive安装



**修改hadoop相关参数**

- Hive的运行依赖于Hadoop(HDFS/MapReduce/YARN都依赖), 同时涉及到HDFS文件系统的访问, 所以需要配置Hadoop的代理用户, 即设置hadoop用户允许代理(模拟)其它用户

```shell
su - hadoop
cd /export/server/hadoop/etc/hadoop/
vim core-site.xml
```

- 添加如下内容在Hadoop的`core-site.xml`的`<configuration></configuration>`之间, 并分发到其它节点, 且重启HDFS集群. 

```

  <property>
    <name>hadoop.proxyuser.hadoop.hosts</name>
    <value>*</value>
  </property>

  <property>
    <name>hadoop.proxyuser.hadoop.groups</name>
    <value>*</value>
  </property>
```

**Hive安装**
- 下载Hive安装包:`http://archive.apache.org/dist/hive/hive-3.1.3/apache-hive-3.1.3-bin.tar.gz`将下载好的文件拖拽上传

- 解压到node1服务器的`/export/server/`内 `tar -zxvf apache-hive-3.1.3-bin.tar.gz -C /export/server/`

<p>

- 下载MySQL驱动包 `https://repo1.maven.org/maven2/mysql/mysql-connector-java/5.1.34/mysql-connector-java-5.1.34.jar`, 将下载好的驱动jar包, 放入**Hive安装文件夹的lib目录内** `mv mysql-connector-java-5.1.34.jar /export/server/apache-hive-3.1.3-bin/lib/`

<p>

- 改名 `mv /export/server/apache-hive-3.1.3-bin hive/`

<p>

- 在Hive的conf目录内, 新建hive-env.sh文件, 填入以下环境变量内容:

```shell
cd /export/server/hive/conf
mv hive-env.sh.template hive-env.sh
vim hive-env.sh

## 添加
export HADOOP_HOME=/export/server/hadoop
export HIVE_CONF_DIR=/export/server/hive/conf
export HIVE_AUX_JARS_PATH=/export/server/hive/lib

```
- 在Hive的conf目录内, 新建hive-site.xml文件, 填入以下内容:

```shell
vim hive-site.xml

<configuration>
	<property>
		<name>javax.jdo.option.ConnectionURL</name>
		<value>jdbc:mysql://node1:3306/hive?createDatabaseIfNotExist=true&amp;useSSL=false&amp;useUnicode=true&amp;characterEncoding=UTF-8</value>
	</property>

	<property>
		<name>javax.jdo.option.ConnectionDriverName</name>
		<value>com.mysql.jdbc.Driver</value>
	</property>

	<property>
		<name>javax.jdo.option.ConnectionUserName</name>
		<value>root</value>
	</property>

	<property>
		<name>javax.jdo.option.ConnectionPassword</name>
		<value>123456</value>
	</property>

	<property>
		<name>hive.server2.thrift.bind.host</name>
		<value>node1</value>
	</property>

	<property>
		<name>hive.metastore.uris</name>
		<value>thrift://node1:9083</value>
	</property>

	<property>
		<name>hive.metastore.event.db.notification.api.auth</name>
		<value>false</value>
	</property>
</configuration>


```

#### 6.3. 初始化元数据库


```shell

mysql -uroot -p
show databases;
CREATE DATABASE hive CHARSET UTF8;
show databases;



# 执行元数据初始化命令
cd /export/server/hive/bin
./schematool -initSchema -dbType mysql -verbos

```


#### 6.4. 启动Hive(使用Hadoop用户)

```shell
#修改文件权限


cd /export/server
chown -R hadoop:hadoop hive hive

su hadoop

cd /export/server/hive
#创建一个hive的日志文件夹

mkdir logs
# 启动元数据管理服务（必须启动，否则无法工作）
#前台启动：
bin/hive --service metastore 
#后台启动：
nohup bin/hive --service metastore >> logs/metastore.log 2>&1 &

#启动客户端，二选一（当前先选择Hive Shell方式）
#确保metastore、hdfs和yarn都已经启动
#Hive Shell方式（可以直接写SQL）：

#在目录/export/server/hive下运行
bin/hive

#Hive ThriftServer方式（不可直接写SQL，需要外部客户端链接使用）：
bin/hive --service hiveserver2
```




### 7. Anaconda安装


- 下载anaconda的安装包, 这里我们需要在官网上查找自己需要的版本, 地址链接在下面为(https://repo.anaconda.com/archive/) ,  我自己下载的版本为(https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh)


```shell
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh

# 校验数据完整性
sha256sum Anaconda3-2023.03-1-Linux-x86_64.sh
# 运行安装脚本 
bash Anaconda3-2023.03-1-Linux-x86_64.sh
```

- 配置环境变量

```
vim /etc/profile
export ANACONDA_HOME=/export/server/anaconda3
export PATH=$PATH:$ANACONDA_HOME/bin
source /etc/profile
```


- 创建软连接(optional)

```shell
ln -s /export/server/anaconda3/bin/python3 /usr/bin/python3
```

### 8. Spark 单机模式

- 上传`spark-3.1.2-bin-hadoop3.2.tgz`到服务器.
<p>

- 解压`tar -zxvf spark-3.1.2-bin-hadoop3.2.tgz -C /export/server`

<p>

- 重命名并创建软连接

```
cd /export/server
mv spark-3.1.2-bin-hadoop3.2/ spark-local
ln -s spark-local spark
```

- 配置环境变量

```
vim /etc/profile
export SPARK_HOME=/export/server/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
source /etc/profile

```


- 启动Spark: `/export/server/spark/bin/pyspark --master local[2]`
- Web界面: `http://node:4040`
- 退出spark: `exit()`






### 9. Spark Standalone模式

- 每一台服务器都要安装Anaconda, 否则将找不到python3环境 (如果有 /usr/bin/python3, 则不需要安装Anaconda)
- 在**每一台机器**下配置以下内容:


#### 9.1 解压/重命名/创建软连接/配置环境变量

- **解压**`tar -zxvf spark-3.1.2-bin-hadoop3.2.tgz -C /export/server`

<p>

- **重命名并创建软连接**

```shell
cd /export/server

# 之前的spark-local可以不用删除
mv spark-3.1.2-bin-hadoop3.2/ spark-standalone
# 删除软连接
rm -rf spark
# 创建软连接
ln -s spark-standalone spark
```

- **配置环境变量** (如果部署saprk-local是改过了, 则不需要再改了)

```
vim /etc/profile
export SPARK_HOME=/export/server/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
source /etc/profile

```

#### 9.2 修改配置文件(spark-env.sh)


```shell
cd /export/server/spark/conf
# 重命名
mv spark-env.sh.template spark-env.sh

vim spark-env.sh

## 22行
export JAVA_HOME=/export/server/jdk1.8.0
export HADOOP_CONF_DIR=/export/server/hadoop/etc/hadoop

# 60行左右
export SPARK_MASTER_HOST=node1   # Spark主节点所在的地址
export SPARK_MASTER_PORT=7077    # Spark主节点内部通信端口, 用于接收客户端请求
export SPARK_MASTER_WEBUI_PORT=8080  # Spark主节点WebUI端口, 用于展示集群状态
export SPARK_WORKER_CORES=1       # 每个Spark工作节点可用的CPU核数
export SPARK_WORKER_MEMORY=1g   # 每个Spark工作节点可用的内存大小
export SPARK_WORKER_PORT=7078    # Spark工作节点内部通信端口, 用于接收Master节点请求
export SPARK_WORKER_WEBUI_PORT=8081  # Spark工作节点WebUI端口, 用于展示节点状态
export SPARK_DAEMON_MEMORY=1g   # Spark进程本身可用的内存大小

```

#### 9.3 添加jobHistoryServer (Optional)


- 9.3.1. **在hadoop文件系统种创建存放日志的目录**
  
```shell
start-dfs.sh
hdfs dfs -mkdir -p /spark/eventLogs/
```

- **9.3.2. 修改spark-defaults.conf.template文件**
```shell
cd /export/server/spark/conf
mv spark-defaults.conf.template spark-defaults.conf
vim spark-defaults.conf
# 在末尾添加
spark.eventLog.enabled     true
spark.eventLog.dir         hdfs://node1:9820/spark/eventLogs
spark.eventLog.compress    true 
```

- **9.3.3. 修改spark-env.sh文件**

```shell
vim spark-env.sh
# 在末尾添加
export SPARK_HISTORY_OPTS="
-Dspark.history.ui.port=18080 
-Dspark.history.fs.logDirectory=hdfs://node1:9820/spark/eventLogs 
-Dspark.history.retained-Applications=3
-Dspark.history.fs.cleaner.enabled=true"
```




#### 9.4. 修改workers文件


```shell
mv workers.template workers
vim workers
# 删掉localhoost, 添加以下内容
node1
node2 
node3
```

#### 9.5. 修改log4j.properties文件

```shell
mv log4j.properties.template log4j.properties
vim log4j.properties

# log4j的5种级别: DEBUG < INFO < WARN < ERROR < FATAL < OFF
# 19行, 修改日志级别为WARN
log4j.rootCategory=WARN, console

```

#### 9.6. 创建/tmp/spark-events  (optional, 报错再加)

服务器本地创建文件夹:`mkdir /tmp/spark-events`

#### 9.7. Spark集群启动与监控

- 启动集群

```shell
# 启动master
cd /export/server/spark
sbin/start-master.sh

# 启动所有worker
sbin/start-workers.sh

# 启动当前节点上的worker
sbin/start-worker.sh

# 启动jobHistoryServer
sbin/start-history-server.sh
```

- 停止集群

```shell
# 停止当前节点上的worker
sbin/stop-worker.sh
# 停止所有worker
sbin/stop-workers.sh
# 停止master
sbin/stop-master.sh
# 停止jobHistoryServer
sbin/stop-history-server.sh
```


- 监控

```shell

jps-cluster.sh 


监控页面: http://node1:8080

日志服务监控页面: http://node1:18080

```


#### 9.8 Spark集群提交任务--测试
```shell

# 提交任务 pi.py
/export/server/spark/bin/spark-submit --master spark://node1:7077 /export/server/spark/examples/src/main/python/pi.py 10

```


```shell
# 测试wordcount

## 把数据上传到hdfs
hdfs dfs -mkdir -p /spark/wordcount/input
hdfs dfs -put /root/data.txt /spark/wordcount/input


## 进入集群模式, 回顾本地模式为  /export/server/spark/bin/pyspark --master local[2]
/export/server/spark/bin/pyspark --master spark://node1:7077

##读取hdfs数据
inpu_rdd = sc.textFile("hdfs://node1:9820/spark/wordcount/input/data.txt")  
# inpu_rdd = sc.textFile("spark/wordcount/input/data.txt") 也行

# 处理数据
......

# 保存数据到hdfs
result_rdd.saveAsTextFile("hdfs://node1:9820/spark/wordcount/output")

```


### 10. PySpark本地环境( Windows)搭建

- 1. 安装Anaconda

<p>

- 2. 进入虚拟环境, 并`pip install pyspark==3.1.2` , **版本不需要太新**, 完成检查`conda list`, 看有没有**py4j & pyspark**这两个包

<p>

- 3. pycharm中创建项目, 使用虚拟环境.  项目下新建**文件夹:** `main , resource , data , test`  
   - 参考[pycharm 中package, directory, sources root, resources root的区别](https://blog.csdn.net/weixin_52120741/article/details/133070942)



### 11. Spark-YARN

- 每个服务器进行以下操作

#### 11.1 解压/重命名/创建软连接/配置环境变量

- **解压**`tar -zxvf spark-3.1.2-bin-hadoop3.2.tgz -C /export/server`

<p>

- **重命名并创建软连接**

```shell
cd /export/server

# 之前的spark-local可以不用删除
mv spark-3.1.2-bin-hadoop3.2/ spark-yarn
# 删除软连接
rm -rf spark
# 创建软连接
ln -s spark-yarn spark
```

- **配置环境变量** (如果部署saprk-local是改过了, 则不需要再改了)

```
vim /etc/profile
export SPARK_HOME=/export/server/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
source /etc/profile

```

#### 11.2 修改配置文件(spark-env.sh)


```shell
cd /export/server/spark/conf
# 重命名
mv spark-env.sh.template spark-env.sh

vim spark-env.sh

## 22行
export JAVA_HOME=/export/server/jdk1.8.0
export HADOOP_CONF_DIR=/export/server/hadoop/etc/hadoop
export YARN_CONF_DIR=/export/server/hadoop/etc/hadoop
export SPARK_DAEMON_MEMORY=1g   # Spark进程本身可用的内存大小
```

#### 11.3 添加jobHistoryServer (Optional)


- 11.3.1. **在hadoop文件系统种创建存放日志的目录**
  
```shell
start-dfs.sh
hdfs dfs -mkdir -p /spark/eventLogs/
```

- **11.3.2. 修改spark-defaults.conf.template文件**
```shell
cd /export/server/spark/conf
mv spark-defaults.conf.template spark-defaults.conf
vim spark-defaults.conf
# 在末尾添加
spark.eventLog.enabled     true
spark.eventLog.dir         hdfs://node1:9820/spark/eventLogs
spark.eventLog.compress    true 
spark.yarn.historyServer.address    node1:18080
spark.yarn.jars    hdfs://node1:9820/spark/jars/*
```

- **11.3.3. 修改spark-env.sh文件**

```shell
vim spark-env.sh
# 在末尾添加

export SPARK_HISTORY_OPTS="
-Dspark.history.ui.port=18080 
-Dspark.history.fs.logDirectory=hdfs://node1:9820/spark/eventLogs 
-Dspark.history.retained-Applications=3
-Dspark.history.fs.cleaner.enabled=true"
```




#### 11.4. 修改workers文件


```shell
mv workers.template workers
vim workers
# 删掉localhoost, 添加以下内容
node1
node2 
node3
```

#### 11.5. 修改log4j.properties文件

```shell
mv log4j.properties.template log4j.properties
vim log4j.properties

# log4j的5种级别: DEBUG < INFO < WARN < ERROR < FATAL < OFF
# 19行, 修改日志级别为WARN
log4j.rootCategory=WARN, console

```


#### 11.7. 创建jar包

```shell
hdfs dfs -mkdir -p /spark/jars/
hdfs dfs -put /export/server/spark/jars/* /spark/jars/
```


#### 11.8. 创建/tmp/spark-events  (optional, 报错再加)

服务器本地创建文件夹:`mkdir /tmp/spark-events`


#### 11.9 YARN的配置

```
cd /export/server/hadoop/etc/hadoop
vim yarn-site.xml

# 添加

  <property>
    <name>yarn.log-aggregation.retain-seconds</name>
    <value>604800</value>
  </property>

  <property>
    <name>yarn.nodemanager.pmem-check-enabled</name>
    <value>false</value>
    <discription>关闭yarn内存检查</discription>
  </property>

  <property>
    <name>yarn.nodemanager.vmem-check-enabled</name>
    <value>false</value>
    <discription>关闭yarn内存检查</discription>
  </property>

```

#### 11.10. 启动集群

```shell
# 启动hadoop集群
start-dfs.sh
start-yarn.sh
# 启动jobHistoryServer
mapred --daemon start historyserver
/export/server/spark/sbin/start-history-server.sh
```


#### 11.11. 提交任务

```shell
# 提交任务 pi.py



###  附录

#### A1 Hadoop文件夹目录解读

在进行3.1的第二步操作之后, `cd export/server/hadoop` 并 `ls -l`得到: 

<div style="text-align: center;">
    <img src="HadoopHive\Figures\hadoop_files.png" style="width: 80%; max-width: 600px; height: auto;">
</div>

其中: 

- **bin**: 存放Hadoop各种应用程序(命令)
- **etc**: 存放Hadoop的配置文件
- **sbin**: 管理员程序 (super bin)
- include: C语言的一些头文件
- lib: 存放Linux系统的动态链接库 (.so)
- libexec: 存放配置Hadoop系统的脚本文件 (.sh/.cmd)
- share: 存放二进制源码(Java jar包)


#### A2 Hadoop core-site.xml配置内容解读

<div style="text-align: center;">
    <img src=".\HadoopHive\Figures\附录2.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>

#### A3 hdfs-site.xml配置内容解读

<div style="text-align: center;">
    <img src=".\HadoopHive\Figures\附录3.1.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>



<div style="text-align: center;">
    <img src=".\HadoopHive\Figures\附录3.2.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>


#### A4 端口详情


- **HDFS-NameNode的通信端口(客户端请求)**: 在 **core-site.xml**中配置的`fs.defaultFS`的值, 默认为`hdfs://node1:9820`. 注意在hadoop1.x时代默认值是`hdfs://node1:9000`, 在hadoop2.x时代默认值是`hdfs://node1:8020`, 在hadoop3.x时代默认值是`hdfs://node1:9820`.



<p>


- **HDFS-NameNode的Web访问端口**: 在**hdfs-site.xml**中配置的`dfs.namenode.http-address`的值, 默认为`node1:9870`.

<p>

- **HDFS-SecondaryNameNode的通信端口**: 在**hdfs-site.xml**中配置的`dfs.namenode.secondary.http-address`的值, 默认为`node1:9868`.

- **HDFS-DataNode的通信端口**: 在**hdfs-site.xml**中配置的`dfs.datanode.address`的值, 默认为`node1:9866`.

```shell
<property>
  <name>dfs.datanode.address</name>
  <value> :9866</value>
</property>
```

<p>

- **MapReduce-JobHistoryServer的通信端口(客户端请求)**: 在**mapred-site.xml**中配置的`mapreduce.jobhistory.address`的值, 默认为`node1:10020`.

- **MapReduce-JobHistoryServer的Web访问端口**: 在**mapred-site.xml**中配置的`mapreduce.jobhistory.webapp.address`的值, 默认为`node1:19888`.

<p>

- **YARN ResourceManager的通信端口(客户端请求)**: 在**yarn-site.xml**中配置的`yarn.resourcemanager.address`的值, 默认为`node1:8032`.


<p>

- **YARN ResourceManager的Web访问端口**: 在**yarn-site.xml**中配置的`yarn.resourcemanager.webapp.address`的值, 默认为`node1:8088`.


<p>

- **YARN其他端口**: 见 **reference 1,2**.

- **HiveServer2的通信端口(客户端请求)**: 在**hive-site.xml**中配置的`hive.server2.thrift.port`的值, 默认为`10000`.

<p>

- **Hive Metastore Server的通信端口**: 在**hive-site.xml**中配置的`hive.metastore.uris`的值, 默认为`thrift://node1:9083`.


- **Spark HistoryServer的通信端口**: 默认为`18080`.


- **Spark其他端口**: 见 `9.2 spark-env.sh`的配置


### Reference

- 1. [关于hadoop的几个默认端口 hadoop3端口](https://blog.51cto.com/u_16099179/7009281)
- 2. [Hadoop集群配置之主要配置文件](https://blog.csdn.net/m0_60511809/article/details/135254570)
- 3. [通过日志聚合将YARN作业日志存储在HDFS中](https://www.cnblogs.com/yinzhengjie/p/13943340.html)