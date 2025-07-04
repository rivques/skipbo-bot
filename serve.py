# an ASGI server for serving the Skip-Bo game
# serves static files from site/build on "/" and provides an API for model access on /get-move

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from bot_configs import configs
from env import SkipBoState

from bot_play import Agent

agent = Agent(configs["pasiphae"])

app = FastAPI()

# Serve static files from the "site/build" directory
app.mount("/site", StaticFiles(directory="site/build", html=True), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("site/build/index.html")

@app.post("/get-move", response_class=JSONResponse)
async def get_move(request: Request):
    data = await request.json()
    game_state_raw = data.get("game_state")
    game_state = SkipBoState.from_dict(game_state_raw)
    # print(f"Received game state: {game_state}")
    action = agent.get_action(game_state)
    print(f"Action taken: {action}")
    return {"action": action.to_dict()}

