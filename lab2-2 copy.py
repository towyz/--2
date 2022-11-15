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


def myDecode(msgRecv: str, node: netnode.Node):
    type = ''
    fromNode = ''
    index = 2  # 读指针的位置，从2开始需要遍历读，初始化为2
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
        # 更新这两个节点间开销
        node.updateCostFromCertainNode(fromNode)
        # 加入一条 REPLY 消息到消息队列中
        msg = "PING_MSG_REPLY/" + node.name + "/"
        for key in node.costDict.keys():
            msg += key + "/" + str(node.costDict.get(key)) + "/"
        # TODO 发送好像出了问题
        msgsToSend.append(
            [msg.encode("utf-8"), ("127.0.0.1", node.portDict.get(fromNode))])
    elif type == 'PING_MSG_REPLY':
        for i in range(2, len(infoList)):
            print(infoList[i])
    elif type == 'PATH_DISTANCE_MSG':
        pass


def listenToOtherNode(socket: socket.socket, node: netnode.Node) -> None:
    while True:
        msgRecv, addr = socket.recvfrom(1024)
        print("receive " + msgRecv.decode() + "from" + str(addr))
        myDecode(msgRecv.decode(), node)


def sendToOtherNode(socket: socket.socket) -> None:
    global msgsToSend
    while True:
        if len(msgsToSend) != 0:
            socket.sendto(msgsToSend[0][0], msgsToSend[0][1])
            msgToSend = msgsToSend.pop(0)
            print("send to " + str(msgToSend[1][1]) + ": " +
                  msgToSend[0].decode())


def listenToUser(node: netnode.Node) -> None:
    cmd = input()
    if "disp_rt" == cmd:
        print(node.getRoute())


if __name__ == "__main__":
    # arg1 = sys.argv[1]
    # print(arg1)

    portFile = open("./nodeaddr.txt", "r", encoding='utf-8')

    topoFile = open("./topology.txt", "r", encoding='utf-8')

    node = netnode.Node("nodeF", portFile, topoFile)
    # print(node.costDict)

    # listen端口不变，send端口+100
    address_listen = ("127.0.0.1", node.port)
    udp_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_listen_socket.bind(address_listen)

    address_send = ("127.0.0.1", node.port + 100)
    udp_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_send_socket.bind(address_send)

    # 创建三个线程
    # 监听其他端口的消息
    listen_thread = threading.Thread(target=listenToOtherNode,
                                     args=(
                                         udp_listen_socket,
                                         node,
                                     ))
    listen_thread.start()
    # 向其他端口发送消息
    send_thread = threading.Thread(target=sendToOtherNode,
                                   args=(udp_send_socket, ))
    send_thread.start()

    # 向相邻节点发送 PING_MSG
    for neighborNode in node.portDict:
        neighborPort = node.portDict.get(neighborNode)
        # 当前的 neighborCostDict 里存放的只有自己和相邻节点的开销
        if neighborNode in node.costDict.keys(
        ) and node.costDict.get(neighborNode) != 0:
            msg = "PING_MSG/" + node.name
            # udp_socket.sendto(msg.encode("utf-8"),
            #                   ("127.0.0.1", neighborPort))
            msgsToSend.append(
                [msg.encode("utf-8"), ("127.0.0.1", neighborPort)])

    # # 下面两行用来测试用本节点端口发送给本节点端口，可以的
    # msg = "PING_MSG/" + node.name
    # msgsToSend.append([msg.encode("utf-8"), ("127.0.0.1", node.port)])
