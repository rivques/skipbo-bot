import torch
import numpy as np
from rlgym_learn_algos.ppo.discrete_actor import DiscreteFF
from colored import Fore, Style

from bot_configs import configs, AgentConfig
from env import SkipBoEngine, SkipBoMutator, SkipBoTerminalCondition, SkipBoState, SkipBoAction

class Agent:
    def __init__(self, config: AgentConfig):
        self.model = DiscreteFF(
            input_size=config.input_size,
            n_actions=config.n_actions,
            layer_sizes=config.layer_sizes,
            device="cpu"
        )
        self.model.load_state_dict(torch.load(config.data_path, map_location="cpu"))
        self.model.eval()
        self.obs_builder = config.obs_builder
        self.action_parser = config.action_parser

    def get_action(self, state: SkipBoState):
        # Convert the observation to the format expected by the model
        shared_info = {}
        obs = self.obs_builder.build_obs([0], state, shared_info)[0]
        out, weights = self.model.get_action([0], [obs])
        action = self.action_parser.parse_actions({0: out[0]}, state, shared_info)[0]
        print(f"action: {action}")
        return action

if __name__ == "__main__":
    # offer the user a choice of agent
    print("Choose an agent:")
    for i, agent_name in enumerate(configs.keys()):
        print(f"{i}: {agent_name} - {configs[agent_name].description}")
    choice = int(input("Enter the number of the agent you want to use: "))
    agent_name = list(configs.keys())[choice]
    config = configs[agent_name]
    print(f"Using agent: {agent_name}")
    agent = Agent(config)
    print("Agent loaded.")
    num_players = 2
    stock_pile_size = int(input("Stock pile size: "))
    engine = SkipBoEngine(num_players)
    mutator = SkipBoMutator(num_players=num_players, stock_pile_size=stock_pile_size)
    terminator = SkipBoTerminalCondition()
    initial_state = engine.create_base_state()
    mutator.apply(initial_state, {})
    engine.reset(initial_state)
    while True:
        if not engine.state.last_step or engine.state.last_step.was_valid:
            print(engine)
        action = None
        if engine.state.current_player == 0:
            print(Fore.green + "Your turn!" + Style.reset)
            card_source = int(input("Card source (stock pile, hand, discards): "))
            card_dest = int(input("Card destination (build piles, discards): "))
            action = SkipBoAction(card_source=card_source, card_destination=card_dest)
        else:
            print(Fore.red + "AI's turn!" + Style.reset)
            action = agent.get_action(engine.state)
        if not engine.is_action_valid(action, engine.state):
            print("\033[31mInvalid action.\033[0m")
        print(Fore.blue, end="")
        engine.step({0: action}, {})
        print(Style.reset)
        if terminator.is_done([0], engine.state, {})[0]:
            print("Game over!")
            print("Final state:")
            print(engine)
            winner = None
            for i in range(num_players):
                if len(engine.state.player_states[i].stock_pile) == 0:
                    winner = i
                    break
            print(f"{'The human' if winner == 0 else 'The computer'} wins!")
            break
        