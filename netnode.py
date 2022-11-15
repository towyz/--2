import re
from io import BufferedWriter


class Node:
    name = ''
    port = ''
    portFile = ''
    topoFile = ''
    portDict = {}  # 接收信息的端口号
    costDict = {}  # 到达各个节点的开销

    def __init__(self, name: str, portFile: BufferedWriter,
                 topoFile: BufferedWriter) -> None:
        self.name = name
        self.portDict = self.initAllNodesPort(portFile)
        self.costDict = self.initNodeCost(topoFile)
        for node in self.portDict.keys():
            if node == self.name:
                self.port = int(self.portDict.get(node))

    def initAllNodesPort(self, file: BufferedWriter) -> dict:
        '''
        从nodeaddr.txt文件中取出各个节点对应的端口号备用
        '''
        portDict = {}
        for line in file:
            portList = re.findall(r"\w+", line)
            portDict.update({portList[0]: int(portList[1])})
        return portDict

    def initNodeCost(self, file: BufferedWriter) -> dict:
        '''
        从topology.txt中获取网络节点的拓扑结构\n
        返回相邻节点到本节点的开销字典，在初始化时开销都为1000\n
        默认本节点知道哪些是相邻节点\n
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
            if self.name == topoList[1]:
                # costDict.update({topoList[0]: int(topoList[2])})
                costDict.update({topoList[0]: 1000})  # 初始化的时候默认为1000，表示没有建立连接
        return costDict

    def updateCostFromCertainNode(self, nodeCertain: str) -> None:
        '''
        模拟确定开销的过程
        '''
        # 在这里用文件流没用，已经用过了，得重新打开
        file = open("./topology.txt", "r", encoding='utf-8')
        for line in file:
            topoList = re.findall(r"\w+", line)
            if (self.name == topoList[0] and nodeCertain == topoList[1]) or (
                    self.name == topoList[1] and nodeCertain == topoList[0]):
                self.costDict.update({nodeCertain: topoList[2]})

    def refreshNodeCost(self):
        '''
        接收到 PING_MSG_REPLY 或 PATH_DISTANCE_MSG 后，更新节点间通信的的开销
        '''
        pass

    def refreshRoute(self):
        pass

    def getRoute():
        pass
