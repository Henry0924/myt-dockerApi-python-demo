# myt-dockerApi-python-demo

1.安装python docker SDK
    
    pip install docker

2.运行main.py

    python main.py -h   查看帮助
    usage: main.py [-h] -H HOST [-n NAME] [-back BACKNAME] [-i {1,2,3,4,5,6,7,8,9,10,11,12}] [-c COMMAND] [-net NETWORKNAME]

    optional arguments:
    -h, --help            show this help message and exit

    -H HOST, --host HOST  主机host，例192.168.100.10

    -n NAME, --name NAME  容器名称，例t001

    -back BACKNAME, --backName BACKNAME  备份时一次只能操作一个容器，备份镜像时传的别名，例t101

    -i {1,2,3,4,5,6,7,8,9,10,11,12}, --index {1,2,3,4,5,6,7,8,9,10,11,12} 安卓容器序号

    -c COMMAND, --command COMMAND  操作命令，create--创建容器，start--启动容器，stop--停止容器，backup--备份容器,备份时一次只能操作一个容器，
                                    remove--删除容器，networks--查看所有网络，rmNetwork--删除网络

    -net NETWORKNAME, --networkName NETWORKNAME docker网络名称, 删除网络时需要指定此名称，例myt

3.在config.json文件里设置镜像地址 配置文件参数说明：

    image - 镜像地址
    bridgedNetworkMode - 是否开启桥接网络模式，默认为false，开启则填true，下面的参数均为开启桥接网络模式后用到的参数
    androidHost - 桥接网络模式下启动的安卓的ip
    dns1 - dns1
    dns2 - dns2
    gateway - 网关，例如192.168.100.1
    subnet - 子网，例如192.168.100.0/24， 192.168.0.0/16

4.查看所有容器

    python main.py -H 192.168.100.10 -c list

5.创建容器
    
    python main.py -H 192.168.100.10 -c create -i 1 -n t001

6.启动容器

    python main.py -H 192.168.100.10 -c start -n t001

7.停止容器

    python main.py -H 192.168.100.10 -c stop -n t001

8.删除容器

    python main.py -H 192.168.100.10 -c remove -n t001

9.备份容器

    python main.py -H 192.168.100.10 -c backup -n t001 -back t101

10.查看docker所有网络

    python main.py -H 192.168.100.10 -c networks

11.删除docker网络

    python main.py -H 192.168.100.10 -c rmNetwork -net networkName

