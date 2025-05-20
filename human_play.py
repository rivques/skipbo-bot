from env import SkipBoEngine, SkipBoMutator, SkipBoAction, SkipBoState, SkipBoTerminalCondition, SkipBoObsBuilder
from rewards import SkipBoReward

# a quick-n-dirty interface to allow a human to play the game thru the terminal

def show_rewards(rewarder: SkipBoReward, state: SkipBoState, did_terminate: bool):
    num_players = len(state.player_states)
    rewards = rewarder.get_rewards(list(range(num_players)), state, {i: did_terminate for i in range(num_players)}, {i: False for i in range(num_players)}, {})
    print(f"The rewards for that turn are: {rewards}")

def human_play():
    """A function to allow a human to play the game."""
    num_players = int(input("Number of players: "))
    if num_players < 1 or num_players > 4:
        print("Invalid number of players. Must be between 1 and 4.")
        return
    stock_pile_size = int(input("Stock pile size: "))
    engine = SkipBoEngine(num_players)
    mutator = SkipBoMutator(num_players=num_players, stock_pile_size=stock_pile_size)
    terminator = SkipBoTerminalCondition()
    initial_state = engine.create_base_state()
    mutator.apply(initial_state, {})
    engine.reset(initial_state)
    rewarder = SkipBoReward()
    obs_builder = SkipBoObsBuilder()
    while True:
        print(engine)
        print("Observation: ", end="")
        obs = obs_builder.build_obs(list(range(num_players)), engine.state, {})
        print(obs)
        card_source = int(input("Card source (stock pile, hand, discards): "))
        card_dest = int(input("Card destination (build piles, discards): "))
        print()
        action = SkipBoAction(card_source=card_source, card_destination=card_dest)
        if not engine.is_action_valid(action, engine.state):
            print("\033[31mInvalid action.\033[0m")
        engine.step({i: action for i in range(num_players)}, {})
        if terminator.is_done([], engine.state, {}):
            print("Game over!")
            print("Final state:")
            print(engine)
            winner = None
            for i in range(num_players):
                if len(engine.state.player_states[i].stock_pile) == 0:
                    winner = i
                    break
            print(f"Player {winner} wins!")
            show_rewards(rewarder, engine.state, True)
            break
        show_rewards(rewarder, engine.state, False)

if __name__ == "__main__":
    human_play()