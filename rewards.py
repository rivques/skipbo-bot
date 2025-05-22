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

class GanymedeReward(RewardFunction[int, SkipBoState, float]):
    """A class to represent the reward function for the game."""
    def reset(self, agents, initial_state, shared_info):
        pass
    def get_rewards(self, agents, state, is_terminated, is_truncated, shared_info) -> dict[int, float]:
        DO_LOG = False
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
            if DO_LOG:
                print(f"0.5 for playing from stock pile")
            reward += 0.5
        elif state.last_step.action.card_source >= 1 and state.last_step.action.card_source <= 4 and state.last_step.action.card_destination <= 4:
            # reward for playing from hand to build pile
            if DO_LOG:
                print(f"0.05 for playing from hand to build pile")
            reward += 0.05
        
        if state.last_step.action.card_source < 5 and state.player_states[state.current_player].hand.count(0) == 0:
            # reward for redrawing hand
            # print(f"0.01 for redrawing hand")
            reward += 0.01

        return {0: reward}
    

class CallistoReward(RewardFunction[int, SkipBoState, float]):
    """A class to represent the reward function for the game."""
    def reset(self, agents, initial_state, shared_info):
        pass
    def get_rewards(self, agents, state, is_terminated, is_truncated, shared_info) -> dict[int, float]:
        DO_LOG = False
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
            reward -= 0.01
            return {0: reward}

        # if is_terminated and state.player_states[state.current_player].stock_pile == []:
        #     # reward for winning
        #     # print(f"1.0 for winning")
        #     reward = 1.0
        
        if state.last_step.action.card_source == 0:
            # reward for playing from stock pile
            if DO_LOG:
                print(f"0.5 for playing from stock pile")
            reward += 0.5
        elif state.last_step.action.card_source >= 1 and state.last_step.action.card_source <= 4 and state.last_step.action.card_destination <= 4:
            # reward for playing from hand to build pile
            if DO_LOG:
                print(f"0.05 for playing from hand to build pile")
            reward += 0.05
        
        if state.last_step.action.card_source < 5 and state.player_states[state.current_player].hand.count(0) == 0:
            # reward for redrawing hand
            # print(f"0.01 for redrawing hand")
            reward += 0.01
        
        if state.last_step.action.card_destination >= 5 and state.last_step.action.card_destination <= 9:
            # penalty for huge discard piles
            discard_pile_size = len(state.player_states[state.current_player].discard_piles[state.last_step.action.card_destination - 5])
            if discard_pile_size > 5:
                reward -= 0.05 * discard_pile_size
                if DO_LOG:
                    print(f"-0.05 * {discard_pile_size} for huge discard pile")
        
        # penalty for playing to discard when it was possible to play to a build pile
        if state.last_step.action.card_destination >= 5 and state.last_step.action.card_destination <= 9:
            # penalty for playing to discard when it was possible to play to a build pile
            for card in state.player_states[state.current_player].hand:
                for build_pile in state.build_piles:
                    if card == len(build_pile) + 1:
                        reward -= 0.03
                        if DO_LOG:
                            print(f"-0.03 for playing to discard when it was possible to play to a build pile")
        
        # general reward for smaller stock piles
        stock_pile_size = len(state.player_states[state.current_player].stock_pile)
        if stock_pile_size > 0:
            reward += (20-stock_pile_size) * 0.1
            if DO_LOG:
                print(f"{(20-stock_pile_size) * 0.1} for cards off stock pile")

        return {0: reward}

class AmaltheaReward(RewardFunction[int, SkipBoState, float]):
    """A class to represent the reward function for the game."""
    def reset(self, agents, initial_state, shared_info):
        pass
    def get_rewards(self, agents, state, is_terminated, is_truncated, shared_info) -> dict[int, float]:
        DO_LOG = False
        reward = 0.0
        if not state.last_step.was_valid:
            # the move was invalid
            if state.last_step.action.card_source == -1:
                # the move was invalid because the player played to the discard pile with another move available
                reward -= 0.1
                if DO_LOG:
                    print(f"-0.1 for avoidable discard")
            else:
                # the move was just invalid (e.g. tried to play a 7 on a 2)
                reward -= 0.1
                if DO_LOG:
                    print(f"-0.1 for invalid move")
            return {0: reward}
        # now, reward plays to the stock pile, plays from the hand, and small stock piles
        if state.last_step.action.card_source == 0:
            # reward for playing from stock pile
            if DO_LOG:
                print(f"0.5 for playing from stock pile")
            reward += 0.5
        elif state.last_step.action.card_source >= 1 and state.last_step.action.card_source <= 4 and state.last_step.action.card_destination <= 4:
            # reward for playing from hand to build pile
            if DO_LOG:
                print(f"0.05 for playing from hand to build pile")
            reward += 0.05
        if state.last_step.action.card_source < 5 and state.player_states[state.current_player].hand.count(0) == 0:
            # reward for redrawing hand
            # print(f"0.01 for redrawing hand")
            reward += 0.01
        # reward for smaller stock piles
        stock_pile_size = len(state.player_states[state.current_player].stock_pile)
        if stock_pile_size > 0:
            reward += (20-stock_pile_size) * 0.1
            if DO_LOG:
                print(f"{(20-stock_pile_size) * 0.1} for cards off stock pile")
        return {0: reward}

class HimaliaReward(RewardFunction[int, SkipBoState, float]):
    """A class to represent the reward function for the game."""
    def reset(self, agents, initial_state, shared_info):
        pass
    def get_rewards(self, agents, state, is_terminated, is_truncated, shared_info) -> dict[int, float]:
        DO_LOG = False
        reward = 0.0
        if not state.last_step.was_valid:
            # the move was invalid
            # this should really not be possible
            print(f"\033[31mInvalid move:\033[0m {state.last_step.action} from choices {shared_info['possible_moves'] if 'possible_moves' in shared_info else 'N/A'} at state {state}")
            return {0: reward}
        # now, reward plays to the stock pile, plays from the hand, and small stock piles
        if state.last_step.action.card_source == 0:
            # reward for playing from stock pile
            if DO_LOG:
                print(f"0.5 for playing from stock pile")
            reward += 0.5
        elif state.last_step.action.card_source >= 1 and state.last_step.action.card_source <= 4 and state.last_step.action.card_destination <= 4:
            # reward for playing from hand to build pile
            if DO_LOG:
                print(f"0.05 for playing from hand to build pile")
            reward += 0.05
        if state.last_step.action.card_source < 5 and state.player_states[state.current_player].hand.count(0) == 0:
            # reward for redrawing hand
            # print(f"0.01 for redrawing hand")
            reward += 0.01
        # reward for smaller stock piles
        stock_pile_size = len(state.player_states[state.current_player].stock_pile)
        if stock_pile_size > 0:
            reward += (20-stock_pile_size) * 0.1
            if DO_LOG:
                print(f"{(20-stock_pile_size) * 0.1} for cards off stock pile")
        # small penalty for not picking one of the options
        if 'raw_action_idx' in shared_info and 'possible_moves' in shared_info:
            if shared_info['possible_moves'][shared_info['raw_action_idx']][0] == -1:
                reward -= 0.005
                if DO_LOG:
                    print(f"-0.005 for not picking one of the options")
        else:
            print(f"Warning: 'raw_action_idx' or 'possible_moves' not in shared_info")
        
        return {0: reward}