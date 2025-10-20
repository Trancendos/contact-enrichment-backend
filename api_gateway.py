from fastapi import FastAPI, Request
from orchestrator import Orchestrator
from plugin_loader import PluginLoader

app = FastAPI()
orchestrator = Orchestrator()
plugin_loader = PluginLoader()
plugins = plugin_loader.load_plugins()

@app.post("/run_workflow")
async def run_workflow(request: Request):
    data = await request.json()
    result = orchestrator.run_workflow(data["workflow_def"], data.get("context", {}))
    return {"result": result}

@app.post("/register_plugin")
async def register_plugin(request: Request):
    data = await request.json()
    plugins[data["name"]] = data["plugin"]
    return {"status": "registered"}

@app.get("/dashboard")
def dashboard():
    return {
        "service_health": orchestrator.health_check(),
        "plugins": list(plugins.keys()),
        "workflows": "To be generated"
    }