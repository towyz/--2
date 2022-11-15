# 实验内容二：
# 距离矢量路由算法的模拟实现

import socket
import sys
import threading

import netnode

# [[msg.encode("utf-8"), ("127.0.0.1", neighborPort)],...]
global msgsToSend
msgsToSend = []


def listenToOtherNode(socket: socket.socket) -> None:
    while True:
        msgRecv, addr = socket.recvfrom(1024)
        print("receive " + msgRecv.decode() + "from" + str(addr))


def sendToOtherNode(socket: socket.socket) -> None:
    global msgsToSend
    while len(msgsToSend) != 0:
        socket.sendto(msgsToSend[0][0], msgsToSend[0][1])
        msgToSend = msgsToSend.pop(0)
        print("send to " + str(msgToSend[1][1]) + ": " + msgToSend[0].decode())


def listenToUser(node: netnode.Node) -> None:
    cmd = input()
    if "disp_rt" == cmd:
        print(node.getRoute())


if __name__ == "__main__":
    # arg1 = sys.argv[1]
    # print(arg1)

    portFile = open("./nodeaddr.txt", "r", encoding='utf-8')

    topoFile = open("./topology.txt", "r", encoding='utf-8')

    node = netnode.Node("nodeA", portFile, topoFile)
    # print(node.costDict)

    # listen端口不变，send端口+100
    address_listen = ("127.0.0.1", node.port)
    udp_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_listen_socket.bind(address_listen)

    address_send = ("127.0.0.1", node.port + 100)
    udp_send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_send_socket.bind(address_send)

    listen_thread = threading.Thread(target=listenToOtherNode,
                                     args=(udp_listen_socket, ))
    listen_thread.start()

    send_thread = threading.Thread(target=sendToOtherNode,
                                   args=(udp_send_socket, ))
    send_thread.start()

    # 向相邻节点发送 PING_MSG
    for neighborNode in node.portDict:
        neighborPort = node.portDict.get(neighborNode)
        # 当前的 neighborCostDict 里存放的只有相邻节点的开销
        if neighborNode in node.costDict.keys():
            msg = "PING_MSG/" + node.name
            # udp_socket.sendto(msg.encode("utf-8"),
            #                   ("127.0.0.1", neighborPort))
            msgsToSend.append(
                [msg.encode("utf-8"), ("127.0.0.1", neighborPort)])

    # 下面两行用来测试用本节点端口发送给本节点端口，可以的
    msg = "PING_MSG/" + node.name
    # udp_socket.sendto(msg.encode("utf-8"), ("127.0.0.1", node.port))
    msgsToSend.append([msg.encode("utf-8"), ("127.0.0.1", node.port)])
