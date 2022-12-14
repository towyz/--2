import re
from io import BufferedWriter
import threading


class Node:
    name = ''
    port = ''
    ifChangedCost = False
    portDict = {}  # 接收信息的端口号
    costDict = {}  # 到达各个节点的开销
    neighborName = []  # 能够发送消息到达的节点（邻居节点）的名称
    routeDict = {}  # 路由表，每个子列表存放格式为{目的节点：路径节点}，路径节点只保留一个邻居节点

    def __init__(self, name: str, portFile: BufferedWriter,
                 topoFile: BufferedWriter) -> None:
        self.name = name
        self.initAllNodesPort(portFile)
        self.initNodeCost(topoFile)
        for node in self.portDict.keys():
            if node == self.name:
                self.port = int(self.portDict.get(node))

    def initAllNodesPort(self, file: BufferedWriter) -> None:
        '''
        从nodeaddr.txt文件中取出各个节点对应的端口号备用
        '''
        portDict = {}
        for line in file:
            portList = re.findall(r"\w+", line)
            portDict.update({portList[0]: int(portList[1])})
        self.portDict = portDict

    def initNodeCost(self, file: BufferedWriter) -> None:
        '''
        从topology.txt中获取网络节点的拓扑结构\n
        返回其他节点(或者说是消息能传送到的节点)到本节点的开销字典\n
        在初始化时，只录入相邻节点，且开销都为1000\n
        默认本节点知道哪些是相邻节点(模拟能够发送消息到达这个过程)\n
        后续更新其他节点到本节点的开销到 costDict
        '''
        costDict = {}
        # 将自己与自己的距离设置为0
        costDict.update({self.name: 0})
        for line in file:
            topoList = re.findall(r"\w+", line)
            if self.name == topoList[0]:
                # costDict.update({topoList[1]: int(topoList[2])})
                costDict.update({topoList[1]: 1000})  # 初始化的时候默认为1000，表示没有建立连接
                # 添加到邻居节点列表
                self.neighborName.append(topoList[1])
            if self.name == topoList[1]:
                # costDict.update({topoList[0]: int(topoList[2])})
                costDict.update({topoList[0]: 1000})  # 初始化的时候默认为1000，表示没有建立连接
                # 添加到邻居节点列表
                self.neighborName.append(topoList[0])
        self.costDict = costDict

    def updateNodeCost(self, fromNode: str, costList=[]):
        '''
        接收到 PING_MSG_REPLY 或 PATH_DISTANCE_MSG 后，更新节点间通信的的开销
        '''
        pass

    def updateCostAndRoute(self,
                           lock: threading.Lock,
                           msgtype: str,
                           fromNode: str,
                           costList=[]) -> bool:
        '''
        根据接收到的信息类型处理数据，更新路由表
        '''
        if msgtype == "PING_MSG":
            # 在这里用文件流没用，已经用完了的，得重新打开
            # 在接收到 PING_MSG 之后，更新本节点和源节点间通信的的开销
            # 模拟确定开销的过程
            file = open("./topology.txt", "r", encoding='utf-8')
            for line in file:
                topoList = re.findall(r"\w+", line)
                if (self.name == topoList[0] and fromNode == topoList[1]) or (
                        self.name == topoList[1] and fromNode == topoList[0]):
                    self.costDict.update({fromNode: int(topoList[2])})
            # 只需要加入一条新路由即可
            self.routeDict.update({fromNode: fromNode})
        elif msgtype == "PING_MSG_REPLY" or msgtype == "PATH_DISTANCE_MSG":
            self.ifChangedCost = False
            for i in costList:
                # 传回的开销不是 fromNode 到 fromNode ，也不是未连接状态
                if i[1] != 0 and i[1] < 1000:
                    # 如果是到本节点的开销，不能直接更新，需要进一步判断
                    if i[0] == self.name:
                        # 如果到fromNode节点的开销还没有更新过，就直接更新
                        if self.routeDict.get(fromNode) is None:
                            self.costDict.update({fromNode: int(i[1])})
                            self.routeDict.update({fromNode: fromNode})
                            lock.acquire()
                            self.ifChangedCost = True
                            lock.release()
                        # 如果有记录了，且本条消息携带的开销更小，则更新处境路由和开销
                        elif (i[1] +
                              self.costDict.get(fromNode)) < self.costDict.get(
                                  i[0]):
                            self.costDict.update(
                                {i[0]: (i[1] + self.costDict.get(fromNode))})
                            self.routeDict.update({i[0]: fromNode})
                            lock.acquire()
                            self.ifChangedCost = True
                            lock.release()
                    # 如果到某一节点的开销为空，直接更新，置ifChangedCost为True
                    elif self.costDict.get(i[0]) is None:
                        self.costDict.update(
                            {i[0]: (i[1] + int(self.costDict.get(fromNode)))})
                        self.routeDict.update({i[0]: fromNode})
                        lock.acquire()
                        self.ifChangedCost = True
                        lock.release()
                    # 大于本节点到 fromNode 再到该节点的开销，应该先删原来的，再添加新的路由项，置ifChangedCost为True
                    elif (i[1] +
                          self.costDict.get(fromNode)) < self.costDict.get(
                              i[0]):
                        self.costDict.update(
                            {i[0]: (i[1] + self.costDict.get(fromNode))})
                        self.routeDict.update({i[0]: fromNode})
                        lock.acquire()
                        self.ifChangedCost = True
                        lock.release()
            # print(self.costDict)
            # print(self.routeDict)
            # 接下来要给周围其他可发消息的邻居路由，发送本节点与fromNode建立通信
            # 消息类型是 PATH_DISTANCE_MSG
        else:
            self.ifChangedCost = False
        return self.ifChangedCost

    def getRoute(self) -> dict:
        return self.routeDict
