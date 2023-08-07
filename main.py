import argparse
import json

import docker
import requests
from docker import types

global Client
global Config
global Args


# 创建容器
def create(name):
    index = Args.index
    image_name = Config.get("image")

    name_list = image_name_list()
    if image_name not in name_list:
        # 拉取镜像
        print("镜像拉取中，请稍后...")
        result = Client.images.pull(repository=image_name)
        print(result)

    binder_index = (index - 1) * 3 + 1

    bridged_mode = Config.get("bridgedNetworkMode", False)
    ports = {}
    ex_ports = {}
    net_config = {}
    network_mode = "default"
    cmd = ["androidboot.hardware=rk30board",
           "androidboot.dobox_fps=24",
           "androidboot.selinux=permissive",
           "qemu=1",
           "androidboot.dobox_width=720",
           "androidboot.dobox_height=1280",
           "androidboot.dobox_dpi=320", ]
    if bridged_mode:
        # 桥接网络模式时的部分配置
        network_mode = "myt"
        net = find_network_by_name("myt")
        if net is None:
            create_network()
        net_config = {
            "EndpointsConfig": {
                network_mode: {
                    "IPAMConfig": {
                        "IPv4Address": Config.get("androidHost"),
                    }
                }
            }
        }
        cmd.append(f"net.dns1={Config.get('dns1')}")
        cmd.append(f"net.dns2={Config.get('dns2')}")

    else:
        # 一般模式下的
        tcp_port = 10000 + index * 3
        udp_port = tcp_port + 1
        web_port = tcp_port + 2
        adb_port = 5000 + index
        ports = {
            "10000/tcp": [
                {
                    "HostIp": "",
                    "HostPort": str(tcp_port)
                }
            ],
            "10001/udp": [
                {
                    "HostIp": "",
                    "HostPort": str(udp_port)
                }
            ],
            "5555/tcp": [
                {
                    "HostIp": "",
                    "HostPort": str(adb_port)
                }
            ],
            "9082/tcp": [
                {
                    "HostIp": "",
                    "HostPort": str(web_port)
                }
            ]
        }
        ex_ports = {
            "10000/tcp": {},
            "10001/udp": {},
            "5555/tcp": {},
            "9082/tcp": {}
        }

    # 创建容器的参数
    create_config = {
        "Cmd": cmd,
        "Image": image_name,
        "ExposedPorts": ex_ports,
        "HostConfig": {
            "Binds": [f"/mmc/custom/data{index}_{name}/data:/data", "/dev/net/tun:/dev/tun", "/dev/mali0:/dev/mali0"],
            "PortBindings": ports,
            "CapAdd": ["SYSLOG",
                       "AUDIT_CONTROL",
                       "SETGID",
                       "DAC_READ_SEARCH",
                       "SYS_ADMIN",
                       "NET_ADMIN",
                       "SYS_MODULE",
                       "SYS_NICE",
                       "SYS_TIME",
                       "SYS_TTY_CONFIG",
                       "NET_BROADCAST",
                       "IPC_LOCK",
                       "SYS_RESOURCE",
                       "SYS_PTRACE",
                       "WAKE_ALARM",
                       "BLOCK_SUSPEND"],
            "RestartPolicy": {
                "Name": "unless-stopped",
                "MaximumRetryCount": 0
            },
            "NetworkMode": network_mode,
            "Devices": [
                {
                    "PathOnHost": f"/dev/binder{binder_index}",
                    "PathInContainer": "/dev/binder",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": f"/dev/binder{binder_index + 1}",
                    "PathInContainer": "/dev/hwbinder",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": f"/dev/binder{binder_index + 2}",
                    "PathInContainer": "/dev/vndbinder",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/tee0",
                    "PathInContainer": "/dev/tee0",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/teepriv0",
                    "PathInContainer": "/dev/teepriv0",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/crypto",
                    "PathInContainer": "/dev/crypto",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/mali0",
                    "PathInContainer": "/dev/mali0",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/rga",
                    "PathInContainer": "/dev/rga",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/dri",
                    "PathInContainer": "/dev/dri",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/mpp_service",
                    "PathInContainer": "/dev/mpp_service",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/fuse",
                    "PathInContainer": "/dev/fuse",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/input/event0",
                    "PathInContainer": "/dev/input/event0",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/dma_heap/cma",
                    "PathInContainer": "/dev/dma_heap/cma",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/dma_heap/cma-uncached",
                    "PathInContainer": "/dev/dma_heap/cma-uncached",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/dma_heap/system",
                    "PathInContainer": "/dev/dma_heap/system",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/dma_heap/system-dma32",
                    "PathInContainer": "/dev/dma_heap/system-dma32",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/dma_heap/system-uncached",
                    "PathInContainer": "/dev/dma_heap/system-uncached",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/dma_heap/system-uncached-dma32",
                    "PathInContainer": "/dev/dma_heap/system-uncached-dma32",
                    "CgroupPermissions": "rwm"
                },
                {
                    "PathOnHost": "/dev/ashmem",
                    "PathInContainer": "/dev/ashmem",
                    "CgroupPermissions": "rwm"
                }
            ],
            "SecurityOpt": [
                "seccomp=unconfined"
            ],
            "Sysctls": {
                "net.ipv4.conf.eth0.rp_filter": "2"
            },
        },
        "NetworkingConfig": net_config
    }

    # api请求创建容器
    url = f'http://{Args.host}:2375/containers/create?name=mytCustom_{index}_{name}'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(create_config)
    response = requests.post(url, headers=headers, data=data)

    # 返回的结果
    content = json.loads(response.content)
    print(
        f"command:{Args.command}, host:{Args.host}, index:{Args.index}, name:{Args.name}, containerID:{content.get('Id')}, 桥接网络模式: {Config.get('bridgedNetworkMode')}")


# 启动容器
def start(name):
    container = find_container_by_name(name)
    if container is None:
        print("此容器不存在")
        return

    container.start()
    print(f"command:{Args.command}, host:{Args.host}, name:{name}, containerID:{container.id}")


# 停止容器
def stop(name):
    container = find_container_by_name(name)
    if container is None:
        print("此容器不存在")
        return

    container.stop()
    print(f"command:{Args.command}, host:{Args.host}, name:{name}, containerID:{container.id}")


# 删除容器
def remove(name):
    container = find_container_by_name(name)
    if container is None:
        print("此容器不存在")
        return

    container.remove(force=True)
    print(f"command:{Args.command}, host:{Args.host}, name:{name}, containerID:{container.id}")


# 备份容器
def backup(name, back_name):
    container = find_container_by_name(name)
    if container is None:
        print("此容器不存在")
        return

    container.stop()
    if Args.backName is None:
        print("备份镜像时，备份别名为必传参数")
        return
    container.rename(container.attrs.get("Name").replace(name, back_name))
    print(
        f"command:{Args.command}, host:{Args.host}, name:{name}, backName:{back_name}, containerID:{container.id}")


# 获取容器列表
def container_list():
    all_list = Client.containers.list(all=True)
    for i, item in enumerate(all_list):
        name = item.attrs.get('Name')
        name_self = name.split("_")[-1]
        print(
            f"序号 {i + 1} \n"
            f"容器名称: {name} \n"
            f"自定义的名称: {name_self} \n"
            f"镜像名: {item.attrs.get('Config').get('Image')} \n"
            f"创建时间: {item.attrs.get('Created')} \n"
            f"当前状态: {item.attrs.get('State').get('Status')} \n"
        )


# 通过容器名查找容器
def find_container_by_name(name):
    all_list = Client.containers.list(all=True)
    for item in all_list:
        if name in item.attrs.get("Name"):
            return item
    return None


# 获取镜像列表
def image_name_list() -> list:
    name_list = []
    images = Client.images.list()
    for i in images:
        if len(i.tags) > 0:
            name_list.append(i.tags[0])

    return name_list


# 查看所有docker网络
def networks():
    networks_list = Client.networks.list()
    for i, item in enumerate(networks_list):
        print(f"序号 {i + 1} \n"
              f"网络id: {item.attrs.get('Id')} \n"
              f"网路名称: {item.attrs.get('Name')} \n"
              f"DRIVER: {item.attrs.get('Driver')} \n"
              f"SCOPE: {item.attrs.get('Scope')} \n"
              )


# 通过名称删除网络
def network_remove(name):
    net = find_network_by_name(name)
    if net is None:
        print("此网络不存在")
        return
    net.remove()
    print(f"command:{Args.command}, host:{Args.host}, network:{name}, ID:{net.id}")


# 通过网络名称查找网络
def find_network_by_name(name):
    networks_list = Client.networks.list()
    for item in networks_list:
        if item.attrs.get("Name") == name:
            return item
    return None


# 创建网络
def create_network():
    ipam_pool = docker.types.IPAMPool(
        subnet=Config.get("subnet"),
        gateway=Config.get("gateway")
    )
    ipam_config = docker.types.IPAMConfig(
        pool_configs=[ipam_pool]
    )

    net = Client.networks.create(
        name="myt",
        driver="macvlan",
        ipam=ipam_config,
        options={"parent": "eth0"}
    )
    return net


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-H", "--host", type=str, required=True, help="主机host，例192.168.100.10")
    parser.add_argument("-n", "--name", type=str, required=False, help="容器名称，例t001")
    parser.add_argument("-back", "--backName", type=str, required=False,
                        help="备份时一次只能操作一个容器，备份镜像时传的别名，例t101")
    parser.add_argument("-i", "--index", type=int, choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                        help="安卓容器序号")
    parser.add_argument("-c", "--command", type=str, default="list",
                        help="操作命令，create--创建容器，start--启动容器，stop--停止容器，backup--备份容器,备份时一次只能操作一个容器，remove--删除容器，networks--查看所有网络，rmNetwork--删除网络")
    parser.add_argument("-net", "--networkName", type=str, required=False,
                        help="docker网络名称, 删除网络时需要指定此名称，例myt")
    Args = parser.parse_args()

    # 创建docker client
    Client = docker.DockerClient(f"http://{Args.host}:2375")

    # 读取配置文件数据
    with open("config.json", "r") as f:
        config = f.read()
        Config = json.loads(config)

    command_dict = {"list": container_list, "create": create, "start": start, "stop": stop, "backup": backup,
                    "remove": remove, "networks": networks, "rmNetwork": network_remove}

    if Args.command not in command_dict.keys():
        print("command有误")
        exit()

    # 根据command字符串调用对应的方法
    command_func = command_dict.get(Args.command)
    if Args.command in ["create", "start", "stop", "remove"]:
        name_list = Args.name.split(",")
        for name in name_list:
            command_func(name.strip())

    elif Args.command == "backup":
        command_func(Args.name.strip(), Args.backName.strip())

    elif Args.command == "rmNetwork":
        nets = Args.networkName.split(",")
        for n in nets:
            command_func(n.strip())

    else:
        command_func()
