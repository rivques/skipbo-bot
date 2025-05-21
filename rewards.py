from env import SkipBoState
from rlgym.api import RewardFunction

class IoReward(RewardFunction[int, SkipBoState, float]):
    """A class to represent the reward function for the game."""
    def reset(self, agents, initial_state, shared_info):
        pass
    def get_rewards(self, agents, state, is_terminated, is_truncated, shared_info) -> dict[int, float]:
        # reward for:
        # - winning (very large)
        # - playing card from stock pile (large)
        # - playing card from hand to build pile
        # - redrawing hand (small)
        # penalty for:
        # - invalid move
        # - next player plays from their stock pile

        reward = 0.0
        # print(f"Rewards for the active player, {agent}:")
        if not state.last_step.was_valid:
            # penalty for invalid move
            # print(f"-0.1 for invalid move")
            reward -= 0.1
            return {0: reward}

        if is_terminated and state.player_states[state.current_player].stock_pile == []:
            # reward for winning
            # print(f"1.0 for winning")
            reward = 1.0
        
        if state.last_step.action.card_source == 0:
            # reward for playing from stock pile
            # print(f"0.1 for playing from stock pile")
            reward += 0.1
        elif state.last_step.action.card_source >= 1 and state.last_step.action.card_source <= 4 and state.last_step.action.card_destination <= 4:
            # reward for playing from hand to build pile
            # print(f"0.05 for playing from hand to build pile")
            reward += 0.05
        
        if state.last_step.action.card_source < 5 and state.player_states[state.current_player].hand.count(0) == 0:
            # reward for redrawing hand
            # print(f"0.01 for redrawing hand")
            reward += 0.01

        return {0: reward}


class EuropaReward(RewardFunction[int, SkipBoState, float]):
    """A class to represent the reward function for the game."""
    def reset(self, agents, initial_state, shared_info):
        pass
    def get_rewards(self, agents, state, is_terminated, is_truncated, shared_info) -> dict[int, float]:
        # reward for:
        # - playing card from stock pile (large)
        # - playing card from hand to build pile
        # - redrawing hand (small)
        # penalty for:
        # - invalid move
        # - next player plays from their stock pile

        reward = 0.0
        # print(f"Rewards for the active player, {agent}:")
        if not state.last_step.was_valid:
            # penalty for invalid move
            # print(f"-0.1 for invalid move")
            reward -= 0.1
            return {0: reward}

        # if is_terminated and state.player_states[state.current_player].stock_pile == []:
        #     # reward for winning
        #     # print(f"1.0 for winning")
        #     reward = 1.0
        
        if state.last_step.action.card_source == 0:
            # reward for playing from stock pile
            # print(f"0.1 for playing from stock pile")
            reward += 0.5
        elif state.last_step.action.card_source >= 1 and state.last_step.action.card_source <= 4 and state.last_step.action.card_destination <= 4:
            # reward for playing from hand to build pile
            # print(f"0.05 for playing from hand to build pile")
            reward += 0.05
        
        if state.last_step.action.card_source < 5 and state.player_states[state.current_player].hand.count(0) == 0:
            # reward for redrawing hand
            # print(f"0.01 for redrawing hand")
            reward += 0.01

        return {0: reward}