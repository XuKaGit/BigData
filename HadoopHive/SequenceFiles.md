# SequenceFiles in Hadoop

## 1. 什么是SequenceFile


SequenceFile是一种由Hadoop提供的高效的二进制文件格式，用于存储键值对`([Key,Value])`数据。
- 可以把SequenceFile当做是一个**容器**，把所有的文件打包到`SequenceFile`类中可以高效的对小文件进行存储和处理。
- `SequenceFile`文件并不按照其存储的Key进行**排序存储**，`SequenceFile`的内部类`Writer`提供了`append`功能。
- `SequenceFiles`支持多种压缩算法，能够有效减少存储空间；支持文件分割，便于分布式处理。
- 适用于大规模数据集，能够在分布式环境中高效读写。

## 2. Python 操作SequenceFile

在Python中处理SequenceFile，我们主要依赖于`hadoop`和`pydoop`这两个库。首先，确保已经安装了Java和Hadoop环境，然后通过pip安装pydoop.
```
pip install pydoop
```

以下是一个简单的示例，展示如何使用pydoop读取SequenceFile文件：

```python
import pydoop.hdfs as hdfs
from pydoop import sequencefile

def read_sequence_file(file_path):
    with hdfs.open(file_path) as f:
        reader = sequencefile.Reader(f)
        for key, value in reader:
            print(f"Key: {key}, Value: {value}")

file_path = 'hdfs://path/to/your/sequencefile.seq'
read_sequence_file(file_path)
```

## reference
- [使用Python高效处理SequenceFile数据格式：从入门到进阶指南](https://www.oryoy.com/news/shi-yong-python-gao-xiao-chu-li-sequencefile-shu-ju-ge-shi-cong-ru-men-dao-jin-jie-zhi-nan.html)