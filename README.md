## mmconv

### 简介

一直想找一款跨平台的免费又好用的思维导图软件，可是哪有两全其美的事呢，个人感觉安卓版的 mindjet 相对好用一些，windows 和 linux 版的 xmind 相对好用一些，但是 xmind 和 mindjet 的格式肯定是不兼容的，而探索发现，他们的文档解压之后都是以 xml 方式储存的，压缩也是简单的 zip 压缩，也没有任何加密，于是，故事开始了。

这是一款用 python3 实现的简单的 xmind 与 mindjet 格式之间的互转工具，只保留树状思维导图以及折叠功能，另外还可以额外可以转化成 txt，用缩进来表示树状图。

后来发现 xmind-zen 保存的文档无法在 xmind8 中打开，所以又添加了 xmind-zen 文档的支持。

### 实现原理

#### 数据结构

利用 python 的列表嵌套列表来储存思维导图的树状结构，例如

```
o
├── a
│   ├── 1
│   ├── 2
│   └── 3
├── b
└── c
```

以上树状结构在代码中被储存为

```python
['o',
 False,
 [['a', False, [['1', False, []], ['2', False, []], ['3', False, []]]],
  ['b', False, []],
  ['c', False, []]]]
```

其中 `False` 表示未被折叠

#### 各个文档格式的存取

1. xmind 8

   xmind 8 保存的格式是 zip 格式，解压后得到若干个文件，树状图数据以 xml 格式保存在 content.xml 里面。

2. xmind-zen

   xmind-zen 保存的格式是 zip 格式，解压后得到若干个文件，树状图数据以 json 格式保存在 content.json 里面。

3. Mindjet Maps

   Mindjet Maps 保存的格式是 zip 格式，解压后得到一个文件 Document.xml，树状图数据以 xml 格式保存在其中。

4. txt

   这是我自己创建的文本文档格式方便调试储存和转换，用缩进的方式表示树状图，用垂直制表符表示是否被折叠

代码风格易扩展，后续随时可以添加更多格式的支持，可以在 Issues 里面提出，有时间我会补充。

### 使用方法

命令格式

```shell
mmconv.py 源文件 [目标文件] [-t 格式]
```

参数详解

```
位置参数：
  源文件                 表示要转换的文件。
  目标文件               目标文件名。转换成功的保存的文件路径。
                       如果未指定目标文件，则直接打印源文件类型。

可选参数：
  -h, --help            显示此帮助消息并退出
  --type {txt,mmap,xmind,zen}, -t {txt,mmap,xmind,zen}
                        指定目标文件的类型。目前支持以下类型：
                        xmind - XMind 8 文档
                        zen - XMind zen 文档
                        txt - txt 文本文档
                        mmap - Mindjet maps 文档
```

若未指定 --type 类型参数，则默认为 txt。

源文件的格式不用指定，会自己识别，详见 --help



