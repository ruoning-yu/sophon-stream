# 目标跟踪算法结果推流Demo

[English](README_EN.md) | 简体中文

## 目录
- [目标跟踪算法结果推流Demo](#目标跟踪算法结果推流demo)
  - [目录](#目录)
  - [1. 简介](#1-简介)
  - [2. 特性](#2-特性)
  - [3. 准备模型与数据](#3-准备模型与数据)
  - [4. 环境准备](#4-环境准备)
    - [4.1 x86/arm PCIe平台](#41-x86arm-pcie平台)
    - [4.2 SoC平台](#42-soc平台)
  - [5. 程序编译](#5-程序编译)
    - [5.1 x86/arm PCIe平台](#51-x86arm-pcie平台)
    - [5.2 SoC平台](#52-soc平台)
  - [6. 程序运行](#6-程序运行)
    - [6.1 Json配置说明](#61-json配置说明)
    - [6.2 运行](#62-运行)
  - [7. 性能测试](#7-性能测试)

## 1. 简介

本例程用于说明如何使用sophon-stream快速构建视频目标跟踪应用，并将算法结果推流输出；

本例程插件的连接方式如下图所示:

![elements.jpg](pics/dec_det_track_osd_enc.png)

## 2. 特性
* 检测模型使用yolox；
* 跟踪模型使用bytetrack；
* 支持BM1684X(x86 PCIe、SoC)，BM1684(x86 PCIe、SoC、arm PCIe)，BM1688(SoC)
* 支持多路视频流
* 支持多线程

## 3. 准备模型与数据

​在`scripts`目录下提供了相关模型和数据的下载脚本[download.sh](./scripts/download.sh)。

脚本执行完毕后，会在当前目录下生成`data`目录，其中包含`models`和`videos`两个子目录。

```bash
# 安装unzip，若已安装请跳过，非ubuntu系统视情况使用yum或其他方式安装
sudo apt install unzip
chmod -R +x scripts/
./scripts/download.sh
```

下载的模型包括：
```bash
./models/
├── BM1684
│   ├── yolox_bytetrack_s_fp32_1b.bmodel    # 用于BM1684的FP32 BModel，batch_size=1
│   ├── yolox_bytetrack_s_fp32_4b.bmodel    # 用于BM1684的FP32 BModel，batch_size=4
│   ├── yolox_bytetrack_s_int8_1b.bmodel    # 用于BM1684的INT8 BModel，batch_size=1
│   ├── yolox_bytetrack_s_int8_4b.bmodel    # 用于BM1684的INT8 BModel，batch_size=4
│   ├── yolox_s_fp32_1b.bmodel              # 用于BM1684的FP32 BModel，batch_size=1
│   ├── yolox_s_fp32_4b.bmodel              # 用于BM1684的FP32 BModel，batch_size=4
│   ├── yolox_s_int8_1b.bmodel              # 用于BM1684的INT8 BModel，batch_size=1
│   └── yolox_s_int8_4b.bmodel              # 用于BM1684的INT8 BModel，batch_size=4
├── BM1684X
│   ├── yolox_bytetrack_s_fp32_4b.bmodel    # 用于BM1684X的FP32 BModel，batch_size=4
│   ├── yolox_bytetrack_s_fp32_1b.bmodel    # 用于BM1684X的FP32 BModel，batch_size=1
│   ├── yolox_bytetrack_s_int8_1b.bmodel    # 用于BM1684X的INT8 BModel，batch_size=1
│   ├── yolox_bytetrack_s_int8_4b.bmodel    # 用于BM1684X的INT8 BModel，batch_size=4
│   ├── yolox_s_fp32_1b.bmodel              # 用于BM1684X的FP32 BModel，batch_size=1
│   ├── yolox_s_fp32_4b.bmodel              # 用于BM1684X的FP32 BModel，batch_size=4
│   ├── yolox_s_int8_1b.bmodel              # 用于BM1684X的INT8 BModel，batch_size=1
│   └── yolox_s_int8_4b.bmodel              # 用于BM1684X的INT8 BModel，batch_size=4
└── BM1688_2cores
    ├── yolox_s_int8_1b.bmodel              # 用于BM1688的INT8 BModel，batch_size=1
    └── yolox_s_int8_4b.bmodel              # 用于BM1688的INT8 BModel，batch_size=4
```
模型说明:

1.`yolox_bytetrack_s`系列模型移植于[bytetrack官方](https://github.com/ifzhang/ByteTrack)，插件配置`mean=[0.485, 0.456, 0.406]`，`std=[0.229, 0.224, 0.225]`，支持person类别的检测任务。

2.`yolox_s`系列模型移植于[yolox官方](https://github.com/Megvii-BaseDetection/YOLOX)，插件配置`mean=[0,0,0]`，`std=[0.0039216,0.0039216,0.0039216]`，支持COCO数据集的80分类检测任务。

下载的数据包括：
```bash
./data/videos                             # 测试视频
├── mot17_01_frcnn.mp4
├── mot17_03_frcnn.mp4
├── mot17_06_frcnn.mp4
├── mot17_07_frcnn.mp4
├── mot17_08_frcnn.mp4
├── mot17_12_frcnn.mp4
├── mot17_14_frcnn.mp4
└── sample_1080p_h265.mp4
```

## 4. 环境准备

### 4.1 x86/arm PCIe平台

如果您在x86/arm平台安装了PCIe加速卡（如SC系列加速卡），可以直接使用它作为开发环境和运行环境。您需要安装libsophon、sophon-opencv和sophon-ffmpeg，具体步骤可参考[x86-pcie平台的开发和运行环境搭建](../../docs/EnvironmentInstallGuide.md#3-x86-pcie平台的开发和运行环境搭建)或[arm-pcie平台的开发和运行环境搭建](../../docs/EnvironmentInstallGuide.md#5-arm-pcie平台的开发和运行环境搭建)。


### 4.2 SoC平台

如果您使用SoC平台（如SE、SM系列边缘设备），刷机后在`/opt/sophon/`下已经预装了相应的libsophon、sophon-opencv和sophon-ffmpeg运行库包，可直接使用它作为运行环境。通常还需要一台x86主机作为开发环境，用于交叉编译C++程序。


## 5. 程序编译
程序运行前需要编译可执行文件。
### 5.1 x86/arm PCIe平台
可以直接在PCIe平台上编译程序，具体请参考[sophon-stream编译](../../docs/HowToMake.md)

### 5.2 SoC平台
通常在x86主机上交叉编译程序，您需要在x86主机上使用SOPHON SDK搭建交叉编译环境，将程序所依赖的头文件和库文件打包至sophon_sdk_soc目录中，具体请参考[sophon-stream编译](../../docs/HowToMake.md)。本例程主要依赖libsophon、sophon-opencv和sophon-ffmpeg运行库包。

## 6. 程序运行

### 6.1 Json配置说明

配置文件位于 [./config](../yolox_bytetrack_osd_encode/config)

其中，[yolox_bytetrack_osd_encode_demo.json](../yolox_bytetrack_osd_encode/config/yolox_bytetrack_osd_encode_demo.json)是例程的整体配置文件，管理输入码流等信息。在一张图上可以支持多路数据的输入，channels中包含每一路码流url等信息。

```json
{
  "channels": [
    {
      "channel_id": 2,
      "url": "../yolox_bytetrack_osd_encode/data/videos/mot17_01_frcnn.mp4",
      "source_type": "VIDEO",
      "loop_num": 1
    },
    {
      "channel_id": 3,
      "url": "../yolox_bytetrack_osd_encode/data/videos/mot17_03_frcnn.mp4",
      "source_type": "VIDEO",
      "loop_num": 1
    },
    {
      "channel_id": 20,
      "url": "../yolox_bytetrack_osd_encode/data/videos/mot17_06_frcnn.mp4",
      "source_type": "VIDEO",
      "loop_num": 1
    },
    {
      "channel_id": 30,
      "url": "../yolox_bytetrack_osd_encode/data/videos/mot17_08_frcnn.mp4",
      "source_type": "VIDEO",
      "loop_num": 1
    }
  ],
  "engine_config_path": "../yolox_bytetrack_osd_encode/config/engine_group.json"
}
```

[engine.json](../yolox_bytetrack_osd_encode/config/engine.json) 包含对graph的配置信息，这部分配置确定之后基本不会发生更改。

需要注意，部署环境下的NPU等设备内存大小会显著影响例程运行的路数。如果默认的输入路数运行中出现了申请内存失败等错误，可以考虑把输入路数减少，即删去`channels`里的部分元素，再进行测试。

这里摘取配置文件的一部分作为示例：在该文件内，需要初始化每个element的信息和element之间的连接方式。element_id是唯一的，起到标识身份的作用。element_config指向该element的详细配置文件地址，port_id是该element的输入输出端口编号，多输入或多输出的情况下，输入/输出编号也不可以重复。is_src标志当前端口是否是整张图的输入端口，is_sink标识当前端口是否是整张图的输出端口。
connection是所有element之间的连接方式，通过element_id和port_id确定。

```json
[
    {
        "graph_id": 0,
        "device_id": 0,
        "graph_name": "yolox_osd_encode",
        "elements": [
            {
                "element_id": 5000,
                "element_config": "../yolox_bytetrack_osd_encode/config/decode.json",
                "ports": {
                    "input": [
                        {
                            "port_id": 0,
                            "is_sink": false,
                            "is_src": true
                        }
                    ],
                    "output": [
                        {
                            "port_id": 0,
                            "is_sink": false,
                            "is_src": false
                        }
                    ]
                }
            },
            {
                "element_id": 5001,
                "element_config": "../yolox_bytetrack_osd_encode/config/yolox_group.json",
                "inner_elements_id": [10001, 10002, 10003]
            },
            {
                "element_id": 5004,
                "element_config": "../yolox_bytetrack_osd_encode/config/bytetrack.json"
            },
            {
                "element_id": 5005,
                "element_config": "../yolox_bytetrack_osd_encode/config/osd.json"
            },
            {
                "element_id": 5006,
                "element_config": "../yolox_bytetrack_osd_encode/config/encode.json",
                "ports": {
                    "input": [
                        {
                            "port_id": 0,
                            "is_sink": false,
                            "is_src": false
                        }
                    ],
                    "output": [
                        {
                            "port_id": 0,
                            "is_sink": true,
                            "is_src": false
                        }
                    ]
                }
            }
        ],
        "connections": [
            {
                "src_element_id": 5000,
                "src_port": 0,
                "dst_element_id": 5001,
                "dst_port": 0
            },
            {
                "src_element_id": 5001,
                "src_port": 0,
                "dst_element_id": 5004,
                "dst_port": 0
            },
            {
                "src_element_id": 5004,
                "src_port": 0,
                "dst_element_id": 5005,
                "dst_port": 0
            },
            {
                "src_element_id": 5005,
                "src_port": 0,
                "dst_element_id": 5006,
                "dst_port": 0
            }
        ]
    }
]
```

[osd.json](../yolox_bytetrack_osd_encode/config/osd.json)等配置文件是对具体某个element的配置细节，设置了模型参数、动态库路径、阈值等信息。该配置文件不需要指定`id`字段和`device_id`字段，例程会将`engine.json`中指定的`element_id`和`device_id`传入。
其中，thread_number是element内部的工作线程数量，一个线程会对应一个数据队列，多路输入情况下，需要合理设置数据队列数目，来保证线程工作压力均匀且合理。
```json
{
  "configure": {
    "osd_type": "TRACK",
    "class_names_file": "../yolox_bytetrack_osd_encode/data/coco.names",
    "draw_utils": "OPENCV",
    "draw_interval": false,
    "put_text": false
  },
  "shared_object": "../../build/lib/libosd.so",
  "name": "osd",
  "side": "sophgo",
  "thread_number": 1
}
```

### 6.2 运行
对于PCIe平台，可以直接在PCIe平台上运行测试；对于SoC平台，需将交叉编译生成的动态链接库、可执行文件、所需的模型和测试数据拷贝到SoC平台中测试。

SoC平台上，动态库、可执行文件、配置文件、模型、视频数据的目录结构关系应与原始sophon-stream仓库中的关系保持一致。

测试的参数及运行方式是一致的，下面主要以PCIe模式进行介绍。

运行可执行文件
```bash
./main --demo_config_path=../yolox_bytetrack_osd_encode/config/yolox_bytetrack_osd_encode_demo.json
```

运行结果如下
```bash
total time cost 74520023 us.
frame count is 3077 | fps is 41.2909 fps.
```
如果encode选择RTSP模式，需要启动推流服务器。您可以使用vlc软件打开推流地址查看视频算法结果，详细说明查看[encode插件文档](../../element/multimedia/encode/README.md)说明。

## 7. 性能测试
由于Osd插件画图速度慢，本例程暂不提供性能测试结果，如需各模型推理性能，请到对应模型例程查看。