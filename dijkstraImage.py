from PIL import Image, ImageDraw

def imageGen(dijkstraModel, path = None):
	d = dijkstraModel
	im = Image.new("RGB", (800, 600), (200, 200, 200))
	draw = ImageDraw.Draw(im)
	for node in d.nodes:
		draw.ellipse((node.position[0] - 5, node.position[1] - 5, node.position[0] + 5, node.position[1] + 5), fill = (17, 138, 178))
		draw.text((node.position[0] - 2, node.position[1] - 20), node.name, fill = (0, 0, 0))
	if path:
		for i in range(len(path) - 1):
			draw.line((path[i].position[0], path[i].position[1], path[i + 1].position[0], path[i + 1].position[1]), fill = (90, 24, 154))
	return im