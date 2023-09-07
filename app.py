import json, io, base64
from flask import Flask, request
from dijkstra import Dijkstra
from dijkstraImage import imageGen
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/v1/dijkstra/<model>/<start>/<end>")
def dijkstra(model, start, end):
    model = model.lower()
    try:
        start = int(start)
        end = int(end)
    except ValueError:
        return {"code": 404, "error": "Invalid start or end node"}
    d = Dijkstra()
    try:
        d.importFromFile(open(f"{model}.json", "r"))
    except FileNotFoundError:
        return {"code": 404, "error": f"Model not found: {model}.json"}
    s = d.searchForNodeById(start)
    if s is None:
        return {"code": 404, "error": f"Start node not found: {start}"}
    e = d.searchForNodeById(end)
    if e is None:
        return {"code": 404, "error": f"End node not found: {end}"}
    d.setStart(s)
    d.setEnd(e)
    path = d.calculatePath()
    if path == False:
        return {"code": 404, "error": f"No path found from {start} to {end}"}
    finalPath = []
    currentDist = 0
    for node in path:
        finalPath.append({"_id": node._id, "name": node.name, "dist": node.dist - currentDist})
        currentDist = node.dist
    return {"code": 200, "path": finalPath}

@app.route("/api/v1/dijkstra/getmodel/<model>")
def getModel(model):
    model = model.lower()
    try:
        with open(f"{model}.json", "r") as f:
            return {"code": 200, "model": json.load(f)}
    except FileNotFoundError:
        return {"code": 404, "error": f"Model not found: {model}.json"}

@app.route("/api/v1/dijkstra/upload/<start>/<end>")
def dijkstra_upload(start, end):
    try:
        start = int(start)
        end = int(end)
    except ValueError:
        return {"code": 404, "error": "Invalid start or end node"}
    try:
        reqJson = request.get_json(
            force=True
        )
    except:
        return {"code": 404, "error": "Invalid JSON"}
    strJson = json.dumps(reqJson)
    d = Dijkstra()
    try:
        f = io.StringIO(strJson)
        d.importFromFile(f)
    except:
        return {"code": 404, "error": "Invalid JSON"}
    
@app.route("/api/v1/dijkstra/image/<model>/<start>/<end>")
def dijkstra_image(model, start, end):
    try:
        start = int(start)
        end = int(end)
    except ValueError:
        return {"code": 404, "error": "Invalid start or end node"}
    d = Dijkstra()
    try:
        d.importFromFile(open(f"{model}.json", "r"))
    except FileNotFoundError:
        return {"code": 404, "error": f"Model not found: {model}.json"}
    s = d.searchForNodeById(start)
    if s is None:
        return {"code": 404, "error": f"Start node not found: {start}"}
    e = d.searchForNodeById(end)
    if e is None:
        return {"code": 404, "error": f"End node not found: {end}"}
    d.setStart(s)
    d.setEnd(e)
    path = d.calculatePath()
    print([node.name for node in path])
    if path == False:
        return {"code": 404, "error": f"No path found from {start} to {end}"}
    image = imageGen(d, path)
    fileIO = BytesIO()
    image.save(fileIO, "PNG")
    fileIO.seek(0)
    b64 = base64.b64encode(fileIO.getvalue()).decode("utf-8")
    return f'<img src="data:image/png;base64,{b64}">'
    #return {"code": 200, "imageB64": b64}