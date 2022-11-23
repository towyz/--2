# 实验内容二：
# 距离矢量路由算法的模拟实现

import re
import socket
# import sys
import threading
import netnode

# [[msg.encode("utf-8"), ("127.0.0.1", neighborPort)],...]
global msgsToSend
msgsToSend = []


def myDecode(lock01: threading.Lock, lock02: threading.Lock, msgRecv: str,
             node: netnode.Node):
    type = ''
    fromNode = ''
    infoList = re.findall(r"\w+", msgRecv)
    # 如果type未被定义，则先判断type，和来源节点
    if type == '':
        if infoList[0] == 'PING_MSG':
            type = 'PING_MSG'
        elif infoList[0] == 'PING_MSG_REPLY':
            type = 'PING_MSG_REPLY'
        elif infoList[0] == 'PATH_DISTANCE_MSG':
            type = 'PATH_DISTANCE_MSG'
        fromNode = infoList[1]

    if type == 'PING_MSG':
        # 更新这两个节点间开销 and 自己节点的路由表
        node.updateCostAndRoute(lock02, type, fromNode)

        # 加入一条 REPLY 消息到消息队列中
        # REPLY 包含了源节点到本节点的开销，和本节点到已知的其他全部节点的开销
        # 本节点和源节点的开销应作为第一组数据
        msg = "PING_MSG_REPLY/" + node.name + "/"
        for key in node.costDict.keys():
            if key == fromNode:
                msg += key + "/" + str(node.costDict.get(key)) + "/"
        for key in node.costDict.keys():
            if key != fromNode:
                msg += key + "/" + str(node.costDict.get(key)) + "/"
        lock01.acquire()
        msgsToSend.append(
            [msg.encode("utf-8"), ("127.0.0.1", node.portDict.get(fromNode))])
        lock01.release()

        # 还需要向周围“其他”节点加入 PATH_DISTANCE_MSG
        # 包含了刚刚更新的信息
        msg = "PATH_DISTANCE_MSG/" + node.name + "/"
        msg += fromNode + "/" + str(node.costDict.get(fromNode)) + "/"
        for nodeToSend in node.neighborName:
            if nodeToSend != fromNode and nodeToSend != node.name:
                lock01.acquire()
                msgsToSend.append([
                    msg.encode("utf-8"),
                    ("127.0.0.1", node.portDict.get(nodeToSend))
                ])
                lock01.release()

    elif type == 'PING_MSG_REPLY' or type == 'PATH_DISTANCE_MSG':
        # 从第3条（index为2）开始是节点间开销数据
        costList = []
        for i in range(2, len(infoList), 2):
            costList.append([infoList[i], int(infoList[i + 1])])
        # print(costList)

        # 根据 REPLY 消息中的信息，更新开销路由表
        ifChangedCost = node.updateCostAndRoute(lock02, type, fromNode,
                                                costList)

        # 如果有开销的变化
        # 向其他邻居可用节点发送 PATH_DISTANCE_MSG 消息
        # 消息携带所有已知开销

        if ifChangedCost is True:
            msg = 'PATH_DISTANCE_MSG/' + node.name + "/"
            for key in node.costDict.keys():
                msg += key + "/" + str(node.costDict.get(key)) + "/"
            # print(msg)
            for otherNode in node.neighborName:
                if otherNode != fromNode and otherNode != node.name:
                    lock01.acquire()
                    msgsToSend.append([
                        msg.encode("utf-8"),
                        ("127.0.0.1", node.portDict.get(otherNode))
                    ])
                    lock01.release()

    # elif type == 'PATH_DISTANCE_MSG':
    #     # TODO 接收信息，更新开销表和路由表
    #     # 从第3条（index为2）开始是节点间开销数据
    #     costList = []
    #     for i in range(2, len(infoList), 2):
    #         costList.append([infoList[i], int(infoList[i + 1])])
    #     print(costList)

    #     # 根据 REPLY 消息中的信息，更新开销路由表
    #     node.updateCostAndRoute(type, fromNode, costList)

    #     # TODO 转发相关信息
    #     pass


def listenToOtherNode(lock01: threading.Lock, lock02: threading.Lock,
                      socket: socket.socket, node: netnode.Node) -> None:
    while True:
        msgRecv, addr = socket.recvfrom(1024)
        if not msgRecv:
            break
        print("receive " + msgRecv.decode() + "from" + str(addr))
        myDecode(lock01, lock02, msgRecv.decode(), node)


def sendToOtherNode(lock01: threading.Lock, socket: socket.socket) -> None:
    global msgsToSend
    while True:
        lock01.acquire()
        if len(msgsToSend) != 0:
            print("still " + str(len(msgsToSend)) + " msgs there to send")
            socket.sendto(msgsToSend[0][0], msgsToSend[0][1])
            msgToSend = msgsToSend.pop(0)
            print("send to " + str(msgToSend[1][1]) + ": " +
                  msgToSend[0].decode())
        lock01.release()


def listenToUser(node: netnode.Node) -> None:
    while True:
        cmd = input()
        if "disp_rt" == cmd:
            print(node.getRoute())
        elif "disp_cost" == cmd:
            print(node.costDict)


if __name__ == "__main__":
    # arg1 = sys.argv[1]
    # print(arg1)

    portFile = open("./nodeaddr.txt", "r", encoding='utf-8')

    topoFile = open("./topology.txt", "r", encoding='utf-8')

    node = netnode.Node("nodeB", portFile, topoFile)
    # print(node.costDict)

    # listen端口不变，send端口+100
    address_listen = ("127.0.0.1", node.port)
    udp_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_listen_socket.bind(address_listen)

    address_send = ("127.0.0.1", node.port + 100)
    udp_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_send_socket.bind(address_send)

    # 创建三个线程
    lock01 = threading.Lock()  # 给msgsToSend的锁
    lock02 = threading.Lock()  # 给ifChanged的锁
    # 监听其他端口的消息
    listen_port_thread = threading.Thread(target=listenToOtherNode,
                                          args=(
                                              lock01,
                                              lock02,
                                              udp_listen_socket,
                                              node,
                                          ))
    listen_port_thread.start()
    # 向其他端口发送消息
    send_thread = threading.Thread(target=sendToOtherNode,
                                   args=(
                                       lock01,
                                       udp_send_socket,
                                   ))
    send_thread.start()
    # 监听用户指令
    listen_cmd_thread = threading.Thread(target=listenToUser, args=(node, ))
    listen_cmd_thread.start()

    # 向相邻节点发送 PING_MSG
    for neighborNode in node.portDict:
        neighborPort = node.portDict.get(neighborNode)
        # 当前的 neighborCostDict 里存放的只有自己和相邻节点的开销
        if neighborNode in node.neighborName:
            msg = "PING_MSG/" + node.name
            # udp_socket.sendto(msg.encode("utf-8"),
            #                   ("127.0.0.1", neighborPort))
            msgsToSend.append(
                [msg.encode("utf-8"), ("127.0.0.1", neighborPort)])

    # # 下面两行用来测试用本节点端口发送给本节点端口，可以的
    # msg = "PING_MSG/" + node.name
    # msgsToSend.append([msg.encode("utf-8"), ("127.0.0.1", node.port)])
