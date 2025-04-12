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

- 以作为node1的服务器为例, 在命令行输入 `vim /etc/hosts`并在文件中添加:
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


#### 3.1. 对于Node1执行以下操作

- 1. **上传并解压Hadoop安装包**: 解压到`/export/server`中`tar -zxvf hadoop-3.3.4.tar.gz -C /export/server` 

- 2. **重命名**: `cd /export/server` , `mv hadoop-3.3.4/ hadoop/`

**关于Hadoop文件夹里的内容请见附录**

- 3. **修改配置文件**: 配置HDFS集群, 主要涉及修改以下存放于 `/export/server/hadoop/etc/hadoop`中的文件
  - workers: 配置从节点 DataNode
 
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
  - hadoop-env.sh: 配置Hadoop相关文件
  
```
vim hadoop-env.sh
#填入以下内容
export JAVA_HOME=/export/server/jdk1.8.0
export HADOOP_HOME=/export/server/hadoop
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export HADOOP_LOG_DIR=$HADOOP_HOME/logs
 ```
  - core-site.xml: Hadoop核心配置文件, 见附录4.2

```
# 在文件内部填入如下内容
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://node1:8020</value>
  </property>
  
  <property>
    <name>hadoop.tmp.dir</name>
    <value>/data/tmp</value>
  </property>

  <property>
    <name>io.file.buffer.size</name>
    <value>131072</value>
  </property>
<configuration>
```
  - hdfs-site.xml: HDFS核心配置文件, 见附录4.3

```
# 在文件中填入以下内容
<configuration>
  <property>
    <name>dfs.datanode.data.dir.perm</name>
    <value>700</value>
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
</configuration>

```


- 4. **将`hadoop`分发到node2,node3**: 在node1执行以下操作(可能会非常慢)
```
cd /export/server
scp -r hadoop node2:`pwd`/
scp -r hadoop node3:`pwd`/
```

#### 3.2. 对于Node1,2,3 执行以下操作


- 1. **新建数据目录**: 在node1创建文件夹`mkdir -p /data/nn`, 在node1,2,3创建文件夹`mkdir -p /data/dn`
- 2. **配置环境变量**:
```
vim /etc/profile
# 添加
export HADOOP_HOME=/export/server/hadoop
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
-----执行修改i
source /etc/profile
```


- 3. **授权为Hadoop用户**: 为了保证安全, Hadoop系统不用root用户启动. 
```
#以root用户身份, 在node1 node2 node3上进行如下操作
chown -R hadoop:hadoop /data
chown -R hadoop:hadoop /export
```
- 4. **格式化namenode**:
```
# 切换到hadoop用户
su - hadoop
# 格式化namenode
hadoop namenode -format
```
- 5. **启动Hadoop集群**
```
# hadoop用户下执行启动
start-dfs.sh
# hadoop用户下关闭启动
stop-dfs.sh
```
- 6. **网络查看**
在浏览器中搜索`node1公网ip:9870`  (记得在node1云服务器安全组配置9870端口)




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


- 创建软连接

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




###  附录

#### A1 Hadoop文件夹

在进行3.1的第二步操作之后, `cd export/server/hadoop` 并 `ls -l`得到: 

<div style="text-align: center;">
    <img src="Figures\hadoop_files.png" style="width: 80%; max-width: 600px; height: auto;">
</div>


#### A2

<div style="text-align: center;">
    <img src="Figures\附录2.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>

#### A3

<div style="text-align: center;">
    <img src="Figures\附录3.1.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>


#### A4

<div style="text-align: center;">
    <img src="Figures\附录3.2.jpg" style="width: 80%; max-width: 600px; height: auto;">
</div>



- **bin**: 存放Hadoop各种应用程序(命令)
- **etc**: 存放Hadoop的配置文件
- **sbin**: 管理员程序 (super bin)
- include: C语言的一些头文件
- lib: 存放Linux系统的动态链接库 (.so)
- libexec: 存放配置Hadoop系统的脚本文件 (.sh/.cmd)
- share: 存放二进制源码(Java jar包)