import json
import tkinter as tk
from tkinter import simpledialog, filedialog
from tkinter import ttk
from dijkstra import *

class TKNode(Node):
	def __init__(self, _id: int, position: tuple, name: str, tkText: int, tkCircle: int):
		super().__init__(_id, position, name)
		self._id = _id
		self.position = position
		self.neighbours = {}
		self.name = name
		self.dist = float("inf")
		self.prev = None
		self.visited = False
		self.tkText = tkText
		self.tkCircle = tkCircle

	def addNeighbour(self, node, distance: int, lineId: int, textId: int):
		if not isinstance(node, TKNode):
			raise TypeError("Node must be of type TKNode")
		self.neighbours[node._id] = [distance, node, lineId, textId]
		node.neighbours[self._id] = [distance, self, lineId, textId]

	def delNeighbour(self, node):
		if not isinstance(node, TKNode):
			raise TypeError("Node must be of type TKNode")
		del self.neighbours[node._id]
		del node.neighbours[self._id]

class TKDijkstra(Dijkstra):
	def __init__(self):
		super().__init__()
		self.nodes = []
		self.lastId = 0
		self.start = None
		self.startNode = None
		self.end = None
		self.endNode = None
		self.path = []
		self.distance = 0
		"""COLOURS"""
		self.StartNode = "#06d6a0"
		self.EndNode = "#ef476f"
		self.SelectedNode = "#073b4c"
		self.UnselectedNode = "#118ab2"
		self.NeighbourLine = "#5a189a"
		"""TKINTER INIT"""
		self.root = tk.Tk()
		self.root.wm_title("Dijkstra - Ev's Editor")
		self.root.geometry("800x600")
		self.root.resizable(False, False)
		self.root.bind("<Button-1>", self.onclick)
		self.modeLabel = ttk.Label(self.root, text="Mode: Add Node")
		self.modeLabel.grid(row=0, column=4, columnspan=6)
		self.modeAddNodeButton = ttk.Button(self.root, text="Add Node", command=lambda: self.setMode("ADDNODE", "Add Node"))
		self.modeAddNodeButton.grid(row=1, column=4, columnspan=2)
		self.modeDelNodeButton = ttk.Button(self.root, text="Delete Node", command=lambda: self.setMode("DELNODE", "Delete Node"))
		self.modeDelNodeButton.grid(row=1, column=6, columnspan=2)
		self.modeAddNeighbourButton = ttk.Button(self.root, text="Add Neighbour", command=lambda: self.setMode("ADDNEIGHBOUR", "Add Neighbour"))
		self.modeAddNeighbourButton.grid(row=1, column=8, columnspan=2)
		self.modeDelNeighbourButton = ttk.Button(text="Delete Neighbour", command=lambda: self.setMode("DELNEIGHBOUR", "Delete Neighbour"))
		self.modeDelNeighbourButton.grid(row=2, column=4, columnspan=2)
		self.modeStartButton = ttk.Button(text="Set Start", command=lambda: self.setMode("SETSTART", "Set Start"))
		self.modeStartButton.grid(row=2, column=6, columnspan=2)
		self.modeEndButton = ttk.Button(text="Set End", command=lambda: self.setMode("SETEND", "Set End"))
		self.modeEndButton.grid(row=2, column=8, columnspan=2)
		self.canvas = tk.Canvas(self.root, width=600, height=400, bg="white")
		self.canvas.grid(row=3, column=0, columnspan=12, rowspan=8)
		self.calculateButton = ttk.Button(self.root, text="Calculate using Dijkstra's", command=self.calculateDijkstra)
		self.calculateButton.grid(row=0, column=0, columnspan=4)
		self.exportButton = ttk.Button(self.root, text="Export to file", command=self.exportToFileCb)
		self.exportButton.grid(row=1, column=0, columnspan=4)
		self.importButton = ttk.Button(self.root, text="Import from file", command=self.importFromFileCb)
		self.importButton.grid(row=2, column=0, columnspan=4)
		self.errorLabel = ttk.Label(self.root, text="")
		self.errorLabel.grid(row=13, column=0, columnspan=12)
		"""VARS SETUP"""
		self.mode = "ADDNODE"
		self.addNeighbourSelections = []
		self.delNeighbourSelections = []

	def startTk(self):
		try:
			from ctypes import windll
			windll.shcore.SetProcessDpiAwareness(1)
		finally:
			self.root.mainloop()

	def calculateDijkstra(self):
		for node in range(len(self.nodes)):
			for _id, neighbour in self.nodes[node].neighbours.items():
				line = neighbour[2]
				self.canvas.itemconfig(line, width=1)
		try:
			path = self.calculatePath()
		except ValueError as e:
			self.errorLabel.config(text=f"An error has occured: {e}")
			return
		if path == False:
			self.errorLabel.config(text="No path found")
			return
		for idx in range(len(path)):
			if idx + 1 == len(path):
				break
			for _, neighbour in path[idx].neighbours.items():
				if neighbour[1]._id == path[idx + 1]._id:
					line = neighbour[2]
					self.canvas.itemconfig(line, width=3)

	def setMode(self, _mode, readable):
		self.mode = _mode
		self.addNeighbourSelections = []
		self.delNeighbourSelections = []
		self.modeLabel.config(text=f"Mode: {readable}")

	def onclick(self, eventorigin):  # sourcery no-metrics
		if not isinstance(eventorigin.widget, tk.Canvas):
			return
		x = eventorigin.x
		y = eventorigin.y
		for node in range(len(self.nodes)):
			for _, neighbour in self.nodes[node].neighbours.items():
				line = neighbour[2]
				self.canvas.itemconfig(line, width=1)
		if self.mode == "ADDNEIGHBOUR":
			overlap = self.canvas.find_overlapping(x, y, x, y)
			if len(overlap) == 0:
				return
			if overlap[0] in [x[2] for x in self.addNeighbourSelections]:
				return
			if self.searchForNodeByPosition((x, y)) is None:
				return
			self.addNeighbourSelections.append((x, y, overlap[0]))
			self.canvas.itemconfig(overlap[0], fill=self.SelectedNode)
			if len(self.addNeighbourSelections) > 1:
				node1 = self.searchForNodeByPosition(self.addNeighbourSelections[0][0:2])
				node2 = self.searchForNodeByPosition(self.addNeighbourSelections[1][0:2])
				distance = simpledialog.askfloat("Distance", f"Enter the distance between {node1.name} and {node2.name}:")
				if node2._id in node1.neighbours:
					node1.neighbours[node2._id][0] = distance
					node2.neighbours[node1._id][0] = distance
					self.canvas.itemconfig(node1.neighbours[node2._id][3], text=f"{distance}")
				else:
					line = self.canvas.create_line(node1.position, node2.position, fill=self.NeighbourLine, width=1)
					middleX = (self.addNeighbourSelections[0][0] + self.addNeighbourSelections[1][0]) / 2
					middleY = (self.addNeighbourSelections[0][1] + self.addNeighbourSelections[1][1]) / 2
					text = self.canvas.create_text((middleX, middleY), text=f"{distance}", fill="black", font=('Helvetica 9'))
					node1.addNeighbour(node2, distance, line, text)
					node2.addNeighbour(node1, distance, line, text)
				if node1._id not in [self.start, self.end]:
					self.canvas.itemconfig(node1.tkCircle, fill=self.UnselectedNode)
				if node2._id not in [self.start, self.end]:
					self.canvas.itemconfig(node2.tkCircle, fill=self.UnselectedNode)
				self.addNeighbourSelections = []
		elif self.mode == "ADDNODE":
			oval = x - 5, y - 5, x + 5, y + 5
			if self.searchForNodeByPosition((x, y)) != None:
				return
			name = simpledialog.askstring("Name", "Enter the node's name: ")
			if name is None:
				return
			dot = self.canvas.create_oval(oval, fill=self.UnselectedNode)
			text = self.canvas.create_text((x, y - 15), text=name, fill="black", font=('Helvetica 7'))
			self.addNode((x, y), name, text, dot)
		elif self.mode == "DELNEIGHBOUR":
			overlap = self.canvas.find_overlapping(x, y, x, y)
			if len(overlap) == 0:
				if len(self.delNeighbourSelections) == 1:
					self.canvas.itemconfig(self.delNeighbourSelections[0][2], fill=self.UnselectedNode)
				self.delNeighbourSelections = []
				return
			if self.searchForNodeByPosition((x, y)) is None:
				return
			self.delNeighbourSelections.append((x, y, overlap[0]))
			self.canvas.itemconfig(overlap[0], fill=self.SelectedNode)
			if len(self.delNeighbourSelections) > 1:
				node1 = self.searchForNodeByPosition(self.delNeighbourSelections[0][0:2])
				node2 = self.searchForNodeByPosition(self.delNeighbourSelections[1][0:2])
				if node2._id not in node1.neighbours:
					self.errorLabel.config(text="Selected nodes are not neighbours.")
					return
				lineId = node1.neighbours[node2._id][2]
				textId = node1.neighbours[node2._id][3]
				node1.delNeighbour(node2)
				self.canvas.itemconfig(lineId, width=10)
				self.canvas.itemconfig(textId, font=("Helvetica 16"))
				self.canvas.delete(lineId, textId)
				print(lineId, textId)
				if node1._id not in [self.start, self.end]:
					self.canvas.itemconfig(node1.tkCircle, fill=self.UnselectedNode)
				if node2._id not in [self.start, self.end]:
					self.canvas.itemconfig(node2.tkCircle, fill=self.UnselectedNode)
				self.delNeighbourSelections = []
		elif self.mode == "DELNODE":
			node = self.searchForNodeByPosition((x, y))
			if node is None:
				return
			self.canvas.delete(node.tkText)
			self.canvas.delete(node.tkCircle)
			self.deleteNode(node)
		elif self.mode == "SETEND":
			overlap = self.canvas.find_overlapping(x, y, x, y)
			if len(overlap) == 0:
				return
			node = self.searchForNodeByPosition((x, y))
			if node._id == self.start:
				self.errorLabel.config(text="Start and end nodes cannot be the same.")
			if self.endNode:
				self.canvas.itemconfig(self.endNode.tkCircle, fill=self.UnselectedNode)
			self.setEnd(node)
		elif self.mode == "SETSTART":
			overlap = self.canvas.find_overlapping(x, y, x, y)
			if len(overlap) == 0:
				return
			node = self.searchForNodeByPosition((x, y))
			if node._id == self.end:
				self.errorLabel.config(text="Start and end nodes cannot be the same.")
			if self.startNode:
				self.canvas.itemconfig(self.startNode.tkCircle, fill=self.UnselectedNode)
			self.setStart(node)
		if self.startNode:
			self.canvas.itemconfig(self.startNode.tkCircle, fill=self.StartNode)
		if self.endNode:
			self.canvas.itemconfig(self.endNode.tkCircle, fill=self.EndNode)

	def setStart(self, node: TKNode):
		self.start = node._id
		self.startNode = node

	def setEnd(self, node: TKNode):
		self.end = node._id
		self.endNode = node

	def addNode(self, position: tuple, name: str, tkText: int, tkCircle: int, _id: int = -1):
		if _id == -1:
			self.nodes.append(TKNode(self.lastId, position, name, tkText, tkCircle))
			self.lastId += 1
		else:
			self.nodes.append(TKNode(_id, position, name, tkText, tkCircle))
		return self.nodes[-1]

	def exportToFileCb(self):
		self.exportToFile(filedialog.asksaveasfile(title="Network Export", filetypes=[("JSON Files", "*.json")]))

	def importFromFileCb(self):
		self.canvas.delete("all")
		self.importFromFile(filedialog.askopenfile(title="Network Import", filetypes=[("JSON Files", "*.json")]))
		for node in self.nodes:
			x = node.position[0]
			y = node.position[1]
			name = node.name
			oval = x - 5, y - 5, x + 5, y + 5
			circle = self.canvas.create_oval(oval, fill=self.UnselectedNode)
			text = self.canvas.create_text((x, y - 15), text=name, fill="black", font=('Helvetica 7'))
			node.tkCircle = circle
			node.tkText = text
		linesDrew = []
		for node in self.nodes:
			overlap = self.canvas.find_overlapping(node.position[0] - 1, node.position[1] - 1, node.position[0] + 1, node.position[1] + 1)
			self.canvas.itemconfig(overlap[0], fill=self.UnselectedNode)
			for _id, neighbour in node.neighbours.items():
				if (node._id, _id) in linesDrew or (_id, node._id) in linesDrew:
					continue
				lineId = self.canvas.create_line(node.position, neighbour[1].position, fill=self.NeighbourLine, width=1)
				neighbour[2] = lineId
				neighbour[1].neighbours[node._id][2] = lineId
				middleX = (node.position[0] + neighbour[1].position[0]) / 2
				middleY = (node.position[1] + neighbour[1].position[1]) / 2
				text = self.canvas.create_text((middleX, middleY), text=f"{neighbour[0]}", fill="black", font=('Helvetica 9'))
				neighbour[3] = text
				neighbour[1].neighbours[node._id][3] = text
				overlap = self.canvas.find_overlapping(neighbour[1].position[0] - 1, neighbour[1].position[1] - 1, neighbour[1].position[0] + 1, neighbour[1].position[1] + 1)
				self.canvas.itemconfig(overlap[0], fill=self.UnselectedNode)
				linesDrew.append((node._id, _id))
		self.canvas.itemconfig(self.startNode.tkCircle, fill=self.StartNode)
		self.canvas.itemconfig(self.endNode.tkCircle, fill=self.EndNode)
	
	def deleteNode(self, node: TKNode):
		for n in self.nodes:
			if node._id in n.neighbours:
				del n.neighbours[node._id]
		self.nodes.remove(node)