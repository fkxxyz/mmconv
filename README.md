## mmconv

### 简介

一直想找一款跨平台的免费又好用的思维导图软件，可是哪有两全其美的事呢，个人感觉安卓版的 mindjet 相对好用一些，windows 和 linux 版的 xmind 相对好用一些，但是 xmind 和 mindjet 的格式肯定是不兼容的，而探索发现，他们的文档解压之后都是以 xml 方式储存的，压缩也是简单的 zip 压缩，也没有任何加密，于是，故事开始了。

这是一款用 python3 实现的简单的 xmind 与 mindjet 格式之间的互转工具，只保留树状思维导图以及折叠功能，另外还可以额外可以转化成 txt，用缩进来表示树状图。

后来发现 xmind-zen 保存的文档无法在 xmind8 中打开，所以又添加了 xmind-zen 文档的支持。

### 使用方法

命令格式

```shell
mmconv.py 源文件 [目标文件] [-t 格式]
```

参数详解

```
位置参数：
  源文件                 源文件。
  目标文件               目标文件。如果未指定目标文件，则打印源文件类型。

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



