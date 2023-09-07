import json

class Node:
	def __init__(self, _id: int, position: tuple, name: str):
		self._id = _id
		self.position = position
		self.neighbours = {}
		self.name = name
		self.dist = float("inf")
		self.prev = None
		self.visited = False

	def addNeighbour(self, node, distance: int):
		if not isinstance(node, Node):
			raise TypeError("Node must be of type Node")
		self.neighbours[node._id] = [distance, node]
		node.neighbours[self._id] = [distance, self]

	def delNeighbour(self, node):
		if not isinstance(node, Node):
			raise TypeError("Node must be of type Node")
		del self.neighbours[node._id]
		del node.neighbours[self._id]

class Dijkstra:
	def __init__(self):
		self.nodes = []
		self.lastId = 0
		self.start = None
		self.startNode = None
		self.end = None
		self.endNode = None
		self.path = []
		self.distance = 0

	def setStart(self, node: Node):
		self.start = node._id
		self.startNode = node

	def setEnd(self, node: Node):
		self.end = node._id
		self.endNode = node

	def addNode(self, position: tuple, name: str, _id: int = -1):
		if _id == -1:
			self.nodes.append(Node(self.lastId, position, name))
			self.lastId += 1
		else:
			self.nodes.append(Node(_id, position, name))
		return self.nodes[-1]

	def searchForNodeByPosition(self, position: tuple):
		for node in self.nodes:
			if abs(node.position[0] - position[0]) <= 5 and abs(node.position[1] - position[1]) <= 5:
				return node
		return None

	def searchForNodeByPositionAccurate(self, position: tuple):
		for node in self.nodes:
			if node.position == position:
				return node
		return None

	def searchForNodeByName(self, name: str):
		for node in self.nodes:
			if node.name == name:
				return node
		return None
	
	def searchForNodeById(self, _id: int):
		for node in self.nodes:
			if node._id == _id:
				return node
		return None
	
	def calculatePath(self):
		if self.start is None or self.end is None:
			raise ValueError("Start and end must be set")
		start = self.startNode
		end = self.endNode
		if len(start.neighbours) == 0:
			return False
		if len(end.neighbours) == 0:
			return False
		nodeQueue = []
		for node in self.nodes:
			node.dist = -1
			node.prev = None
			node.visited = False
			if node._id != start:
				nodeQueue.append(node)
		start.dist = 0
		start.visited = True
		for node in start.neighbours:
			start.neighbours[node][1].dist = start.neighbours[node][0]
			start.neighbours[node][1].prev = start
		while nodeQueue:
			currentNode = min(nodeQueue, key=lambda x: float("inf") if x.dist == -1 else x.dist)
			for _id, neighbour in currentNode.neighbours.items():
				n = neighbour[1]
				if n.visited:
					continue
				tempDist = currentNode.dist + neighbour[0]
				if neighbour[0] == -1:
					tempDist += 1
				if tempDist < n.dist or n.dist == -1:
					n.dist = tempDist
					n.prev = currentNode
			nodeQueue.remove(currentNode)
		path = []
		currentNode = end
		while currentNode != start:
			path.append(currentNode)
			currentNode = currentNode.prev
		path.append(start)
		path.reverse()
		return path
	
	def exportToFile(self, fp):
		data = {"version": 2, "nodes": [], "start": self.start, "end": self.end, "lastId": self.lastId}
		for node in self.nodes:
			data["nodes"].append({"_id": node._id, "position": node.position, "name": node.name, "neighbours": []})
			for _, neighbour in node.neighbours.items():
				n = neighbour[1]
				data["nodes"][-1]["neighbours"].append({"_id": n._id, "dist": neighbour[0]})
		json.dump(data, fp, indent="\t")
		fp.close()

	def importFromFile(self, fp):
		data = json.load(fp)
		fp.close()
		if "version" not in data or data["version"] == 1:
			return self.fileV1Load(data)
		elif data["version"] == 2:
			return self.fileV2Load(data)
		else:
			print(f"ERROR: Unknown file version '${data['version']}'")
	
	def fileV1Load(self, data):
		self.nodes = []
		self.lastId = data["lastId"]
		for node in data["nodes"]:
			self.addNode(node["position"], node["name"], node["_id"])
			for neighbour in node["neighbours"]:
				self.nodes[node["_id"]].addNeighbour(self.nodes[neighbour["_id"]], neighbour["dist"])
		for node in self.nodes:
			if node._id == data["start"]:
				self.start = node._id
				self.startNode = node
				continue
			elif node._id == data["end"]:
				self.end = node._id
				self.endNode = node
				continue
		return data
	
	def fileV2Load(self, data):
		self.nodes = []
		self.lastId = data["lastId"]
		for node in data["nodes"]:
			self.addNode(node["position"], node["name"], node["_id"])
		for node in data["nodes"]:
			for neighbour in node["neighbours"]:
				self.nodes[node["_id"]].addNeighbour(self.nodes[neighbour[1]], neighbour[0])
		for node in self.nodes:
			if node._id == data["start"]:
				self.start = node._id
				self.startNode = node
				continue
			elif node._id == data["end"]:
				self.end = node._id
				self.endNode = node
				continue
		return data
	
	def deleteNode(self, node: Node):
		for n in self.nodes:
			if node._id in n.neighbours:
				del n.neighbours[node._id]
		self.nodes.remove(node)