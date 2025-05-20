from env import SkipBoState
from rlgym.api import RewardFunction

class SkipBoReward(RewardFunction[int, SkipBoState, float]):
    """A class to represent the reward function for the game."""
    def reset(self, agents, initial_state, shared_info):
        pass
    def get_rewards(self, agents, state, is_terminated, is_truncated, shared_info) -> dict[int, float]:
        # TODO
        pass