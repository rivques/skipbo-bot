# skipbo-bot
Using reinforcement learning to play [Skip-Bo](https://en.wikipedia.org/wiki/Skip-Bo).

## Usage
Visit the website at [skipbo-bot.rivques.hackclub.app](https://skipbo-bot.rivques.hackclub.app) to play against the bot.

## Development
To run locally, clone the repo, then:
1. create a venv
2. `pip install -r requirements.txt`
3. in `site/`, run `npm install`

Now you can work on the site (backendless) by running `npm start` in the `site/` directory.

To work on the backend, run `fastapi dev serve.py` in the root directory. Incorporate changes to the frontend by running `npm run build` in the `site/` directory, which will update the static files served by FastAPI.

To work on the models themselves, adjust `rewards.py`, `env.py` as needed. Then adjust parameters like `run_name` and `timestep_limit` in `train.py`. Finally, run `python train.py` to train the model. That'll spit checkpoints into `agent_controllers_checkpoints/`. Once the model is trained, grab the last checkpoint's `.pt` file and put it in `agents/`, and add a config to `bot_config.py` to use it.

## Deployment
The Dockerfile _should_ Just Work if you build and run it.

The live website is deployed on Coolify (from Dockerfile on Git).

## AI usage disclosure:
The majority of this project is human-written with the assistance of copilot tab-complete. The website was written with frequent consultation with LLMs. `play_skipbo_external.py` was primarily written by agent mode.