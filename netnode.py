import re
from io import BufferedWriter


class Node:
    name = ''
    port = ''
    portFile = ''
    topoFile = ''
    portDict = {}  # 接收信息的端口号
    costDict = {}  # 到达各个节点的开销
    neighborName = []  # 能够发送消息到达的节点（邻居节点）的名称
    # [[nodeB, nodeB], [nodeD, nodeC]]
    routeList = []  # 路由表，每个子列表存放格式为[目的节点，路径节点]，路径节点只保留一个邻居节点

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

    def updateCostFromCertainNode(self, nodeCertain: str) -> None:
        '''
        在接收到 PING_MSG 之后，更新本节点和源节点间通信的的开销\n
        模拟确定开销的过程
        '''
        # 在这里用文件流没用，已经用完了的，得重新打开
        file = open("./topology.txt", "r", encoding='utf-8')
        for line in file:
            topoList = re.findall(r"\w+", line)
            if (self.name == topoList[0] and nodeCertain == topoList[1]) or (
                    self.name == topoList[1] and nodeCertain == topoList[0]):
                self.costDict.update({nodeCertain: topoList[2]})

    def updateNodeCost(self):
        '''
        接收到 PING_MSG_REPLY 或 PATH_DISTANCE_MSG 后，更新节点间通信的的开销
        '''
        pass

    def refreshRoute(self):
        pass

    def getRoute():
        pass
