# env.py
# this is all the logic that defines how the game is actually played
# plus a bit about how it's represented to agents

from typing import Dict, List, Any, Optional
import numpy as np
import random
from dataclasses import dataclass
from rlgym.api import TransitionEngine, StateMutator, ObsBuilder, ActionParser, RewardFunction, DoneCondition

# 0 means no card, 1-12 are the cards, 13 is the skipbo card
Card = int

@dataclass
class PlayerState:
    """A class to represent the state of a player in the game."""
    hand: List[Card] # up to 5 cards
    stock_pile: List[Card] # all the cards in the stock pile. index 0 is the bottom card
    discard_piles: List[List[Card]] # 4 discard piles. index 0 is the bottom card. Max 20.

@dataclass
class SkipBoAction:
    """A class to represent an action in the game."""
    card_source: int # 0: stock pile, 1-5: hand, 6-9: discard piles
    card_destination: int # 0-3: build piles, 4-7: discard piles

@dataclass
class SkipBoLastStep:
    """A class to represent the last step taken in the game."""
    action: SkipBoAction
    taken_by: int
    was_valid: bool

@dataclass
class SkipBoState:
    """A class to represent the state of the game."""
    player_states: List[PlayerState]
    current_player: int
    build_piles: List[List[Card]] # 4 build piles. index 0 is the bottom card
    draw_pile: List[Card] # the deck of cards. index 0 is the bottom card 
    completed_build_piles: List[Card] # the completed build piles, together.
    num_turns: int # the number of turns taken so far
    invalid_actions_count: int # the number of invalid actions taken in a row so far
    last_step: Optional[SkipBoLastStep]

class SkipBoEngine(TransitionEngine[int, SkipBoState, SkipBoAction]):
    """A class to represent the game engine."""
    def __init__(self, num_players: int = 2):
        self.num_players = num_players
        self._state: SkipBoState = None # type: ignore # this will be set by the mutator before anything gets called
    
    @property
    def agents(self) -> List[int]:
        """List of IDs of the agents in the game."""
        return [0]
    
    @property
    def max_num_agents(self) -> int:
        """Maximum number of agents in the game. This is 1 - the same agent will play all players."""
        return 1
    
    @property
    def state(self) -> SkipBoState:
        """Current state of the game."""
        return self._state
    
    @property
    def config(self) -> Dict[str, Any]:
        return {}
    
    @config.setter
    def config(self, value: Dict[str, Any]):
        pass
    
    @staticmethod
    def is_action_valid(action: SkipBoAction, state: SkipBoState) -> bool:
        """Check if an action is valid."""
        # check if the action is valid
        # 0: stock pile, 1-5: hand, 6-9: discard piles
        # 0-3: build piles, 4-7: discard piles
        card_source = action.card_source
        card_destination = action.card_destination

        ps = state.player_states[state.current_player]

        source_value = 0
        if card_source == 0:
            source_value = ps.stock_pile[-1] if len(ps.stock_pile) > 0 else 0
        elif card_source >= 1 and card_source <= 5:
            source_value = ps.hand[card_source - 1]
        elif card_source >= 6 and card_source <= 9:
            source_value = ps.discard_piles[card_source - 6][-1] if len(ps.discard_piles[card_source - 6]) > 0 else 0
        else:
            return False
        
        if card_destination >= 0 and card_destination <= 3:
            # build piles
            dest_value = len(state.build_piles[card_destination])
            if source_value == 13: # skipbo card
                return True
            else:
                return source_value == dest_value + 1
        elif card_destination >= 4 and card_destination <= 7:
            return card_source >= 1 and card_source <= 5 and source_value != 0 # can only discard from hand, and can't discard nothing
        else:
            return False

    def _src_name(self, src: int) -> str:
        """Get the name of the source."""
        if src == 0:
            return "stock pile"
        elif src >= 1 and src <= 5:
            return f"hand {src - 1}"
        elif src >= 6 and src <= 9:
            return f"discard pile {src - 6}"
        else:
            return "unknown"
    
    def _dst_name(self, dst: int) -> str:
        """Get the name of the destination."""
        if dst >= 0 and dst <= 3:
            return f"build pile {dst}"
        elif dst >= 4 and dst <= 7:
            return f"discard pile {dst - 4}"
        else:
            return "unknown"
        
    def _card_at_src(self, player_state: PlayerState, src: int) -> Card:
        """Get the card at the source."""
        if src == 0:
            return player_state.stock_pile[-1]
        elif src >= 1 and src <= 5:
            return player_state.hand[src - 1]
        elif src >= 6 and src <= 9:
            return player_state.discard_piles[src - 6][-1] if len(player_state.discard_piles[src - 6]) > 0 else 0
        else:
            return 0
    
    def _card_at_dst(self, player_state: PlayerState, dst: int) -> Card:
        """Get the card at the destination."""
        if dst >= 0 and dst <= 3:
            return len(self._state.build_piles[dst])
        elif dst >= 4 and dst <= 7:
            return player_state.discard_piles[dst - 4][-1] if len(player_state.discard_piles[dst - 4]) > 0 else 0
        else:
            return 0

    def step(self, actions: Dict[int, SkipBoAction], shared_info: Dict[str, Any]) -> SkipBoState:
        """Step the game forward by one action."""
        DO_LOG = False
        # first, pick out the action whose turn it is
        current_player = self._state.current_player
        action = actions[0]
        self._state.last_step = SkipBoLastStep(
            action=action,
            taken_by=current_player,
            was_valid=True
        )
        # check if the action is valid
        if not self.is_action_valid(action, self._state):
            # if the action is invalid, increment the invalid actions count
            self._state.invalid_actions_count += 1
            # set the last step to invalid
            self._state.last_step.was_valid = False
            if DO_LOG:
                print(f"Player {current_player} tried to play the {self._card_at_src(self._state.player_states[current_player], action.card_source)} from their {self._src_name(action.card_source)} to the {self._card_at_dst(self._state.player_states[current_player], action.card_destination)} at their {self._dst_name(action.card_destination)}, but it was invalid.")
            # if the action is invalid, return the state without changing it further
            return self._state
        
        # if the action is valid, reset the invalid actions count
        self._state.invalid_actions_count = 0
        # ok now we actually play skipbo
        # first, grab the card from the source
        card_source = action.card_source
        card_destination = action.card_destination
        ps = self._state.player_states[current_player]
        card_value = 0
        if card_source == 0:
            # move from stock pile
            card_value = ps.stock_pile.pop()
        elif card_source >= 1 and card_source <= 5:
            # move from hand
            card_value = ps.hand[card_source - 1]
            ps.hand[card_source - 1] = 0
        elif card_source >= 6 and card_source <= 9:
            # move from discard pile
            card_value = ps.discard_piles[card_source - 6].pop()
        
        if DO_LOG:
            print(f"Player {current_player} played the {card_value} from their {self._src_name(card_source)} to the {self._card_at_dst(ps, card_destination)} on their {self._dst_name(card_destination)}.")

        # now move the card to the destination
        if card_destination >= 0 and card_destination <= 3:
            # move to build pile
            self._state.build_piles[card_destination].append(card_value)
        elif card_destination >= 4 and card_destination <= 7:
            # move to discard pile
            ps.discard_piles[card_destination - 4].append(card_value)
        
        # now, check if we need to do any game maintenance
        # do we need to remove a completed build pile?
        if card_destination <= 3 and len(self._state.build_piles[card_destination]) == 12:
            # if the build pile is complete, remove it from the game
            self._state.completed_build_piles += self._state.build_piles[card_destination]
            self._state.build_piles[card_destination] = []
        # do we need to draw new cards because we emptied our hand?
        if ps.hand.count(0) == 5:
            # if the hand is empty, draw new cards
            self._draw_cards(current_player)
        # do we need to end the turn because we discarded a card?
        if  card_destination >= 4 and card_destination <= 7:
            # if we discarded a card, end the turn
            self._state.current_player = (self._state.current_player + 1) % self.num_players
            # increment the number of turns taken
            self._state.num_turns += 1
            # draw new cards for the next player
            self._draw_cards(self._state.current_player)
        if not DO_LOG:
            # 10 in 20k chance to print state anyways
            if random.randint(0, 80_000) == 0:
                print(self)
        return self._state

    def _draw_cards(self, player_id: int):
        """Draw up to 5 cards from the draw pile to the player's hand, reshuffling the draw pile if necessary."""
        ps = self._state.player_states[player_id]
        reshuffle_needed = ps.hand.count(0) > len(self._state.draw_pile)
        if reshuffle_needed:
            # reshuffle the draw pile
            self._state.draw_pile = self._state.completed_build_piles + self._state.draw_pile
            random.shuffle(self._state.draw_pile)
            self._state.completed_build_piles = []
        # draw cards
        for i in range(5):
            if ps.hand[i] == 0:
                if len(self._state.draw_pile) == 0:
                    # even tho we've reshuffled, we still don't have enough cards
                    # give up and let the truncation condition handle it
                    break
                card = self._state.draw_pile.pop()
                ps.hand[i] = card


    def create_base_state(self):
        """Create a minimal state for the game. The mutator will set up everything."""
        return SkipBoState(
            player_states=[PlayerState([0] * 5, [], [[],[],[],[]]) for _ in range(self.num_players)],
            current_player=0,
            build_piles=[[],[],[],[]],
            draw_pile=[],
            completed_build_piles=[],
            num_turns=0,
            invalid_actions_count=0,
            last_step=None
        )
    
    def reset(self, initial_state: Optional[SkipBoState] = None) -> None:
        """Reset the engine with an optional initial state"""
        self._state = initial_state if initial_state is not None else self.create_base_state()

    def set_state(self, desired_state, shared_info):
        """Set the state of the game to a desired state."""
        self._state = desired_state
        return self._state
    
    def close(self):
        """Close the engine."""
        pass

    def __str__(self):
        """human-readable representation of the game state"""
        if self._state is None:
            return "No game state set."
        result = f"It's player {self._state.current_player}'s turn.\n"
        result += f"Current player hand: {self._state.player_states[self._state.current_player].hand}\n"
        for i, player_state in enumerate(self._state.player_states):
            result += f"Player {i}: Stock pile: {len(player_state.stock_pile)} cards, top card: {player_state.stock_pile[-1] if len(player_state.stock_pile) > 0 else 0}, Discard piles tops: {[discard_pile[-1] if len(discard_pile) > 0 else 0 for discard_pile in player_state.discard_piles]}, discard piles sizes: {[len(discard_pile) for discard_pile in player_state.discard_piles]}\n"
        result += f"Build piles: {self._state.build_piles}\n"
        result += f"Draw pile: {len(self._state.draw_pile)} cards\n"
        result += f"Turns taken so far: {self._state.num_turns}\n"
        return result


class SkipBoMutator(StateMutator[SkipBoState]):
    """A class to represent the state mutator."""
    def __init__(self, num_players: int = 2, stock_pile_size: int = 20):
        super().__init__()
        self.num_players = num_players
        self.stock_pile_size = stock_pile_size
    
    def apply(self, state, shared_info):
        """Set up a new game."""
        # make a pile with 12 of each card from 1-12 and 18 skipbo cards
        state.draw_pile = [i % 12 + 1 for i in range(144)] + [13]*18
        random.shuffle(state.draw_pile)

        for player_state in state.player_states:
            player_state.hand = [0] * 5
            player_state.discard_piles = [[],[],[],[]]
            # draw the stock pile
            player_state.stock_pile = state.draw_pile[:self.stock_pile_size]
            state.draw_pile = state.draw_pile[self.stock_pile_size:]
        
        # draw the first hand for the first player
        state.player_states[0].hand = state.draw_pile[:5]
        state.draw_pile = state.draw_pile[5:]
        
        state.current_player = 0
        state.build_piles = [[],[],[],[]]
        state.completed_build_piles = []
        state.num_turns = 0
        state.invalid_actions_count = 0
        state.last_step = None

class IoObsBuilder(ObsBuilder[int, np.ndarray, SkipBoState, tuple]):
    """A class to represent the observation builder."""
    def get_obs_space(self, agent):
        return 'real', 33
    
    def reset(self, agents, initial_state, shared_info):
        pass

    def build_obs(self, agents, state, shared_info):
        observations = {}

        ps = state.player_states[state.current_player]
        nps = state.player_states[(state.current_player + 1) % len(state.player_states)]
        obs_py: list[int] = [
            ps.stock_pile[-1], # len 1
            len(ps.stock_pile), # len 1
        ]
        obs_py += ps.hand # len 5
        # len(build_pile) will give the effective value of each pile
        obs_py += [len(build_pile) for build_pile in state.build_piles] # len 4
        # the top 3 cards of each discard pile, left-padded with 0s, and the size of each pile
        discards = []
        for discard_pile in ps.discard_piles:
            discards += [0] * (3-len(discard_pile)) + discard_pile[-3:] + [len(discard_pile)]
        obs_py += discards # len 16
        obs_py += [
            nps.stock_pile[-1], # len 1
            len(nps.stock_pile)
        ] # len 1
        # the top card of each of nps's discard piles
        obs_py += [discard_pile[-1] if len(discard_pile) > 0 else 0 for discard_pile in nps.discard_piles] # len 4
        # total len 33
        obs = np.array(obs_py, dtype=np.int32)
        return {0: obs}

class GanymedeObsBuilder(ObsBuilder[int, np.ndarray, SkipBoState, tuple]):
    """A class to represent the observation builder."""
    def get_obs_space(self, agent):
        return 'real', 34
    
    def reset(self, agents, initial_state, shared_info):
        pass

    def build_obs(self, agents, state, shared_info):
        observations = {}

        stock_pile_is_playable = state.player_states[state.current_player].stock_pile[-1] == len(state.build_piles[0]) + 1 or state.player_states[state.current_player].stock_pile[-1] == 13

        ps = state.player_states[state.current_player]
        nps = state.player_states[(state.current_player + 1) % len(state.player_states)]
        obs_py: list[int] = [
            ps.stock_pile[-1], # len 1
            len(ps.stock_pile), # len 1
            int(stock_pile_is_playable), # len 1
        ]
        obs_py += ps.hand # len 5
        # len(build_pile) will give the effective value of each pile
        obs_py += [len(build_pile) for build_pile in state.build_piles] # len 4
        # the top 3 cards of each discard pile, left-padded with 0s, and the size of each pile
        discards = []
        for discard_pile in ps.discard_piles:
            discards += [0] * (3-len(discard_pile)) + discard_pile[-3:] + [len(discard_pile)]
        obs_py += discards # len 16
        obs_py += [
            nps.stock_pile[-1], # len 1
            len(nps.stock_pile)
        ] # len 1
        # the top card of each of nps's discard piles
        obs_py += [discard_pile[-1] if len(discard_pile) > 0 else 0 for discard_pile in nps.discard_piles] # len 4
        # total len 34
        obs = np.array(obs_py, dtype=np.int32)
        return {0: obs}

class CallistoObsBuilder(ObsBuilder[int, np.ndarray, SkipBoState, tuple]):
    """A class to represent the observation builder."""
    def get_obs_space(self, agent):
        return 'real', 39
    
    def reset(self, agents, initial_state, shared_info):
        pass

    def build_obs(self, agents, state, shared_info):
        observations = {}

        stock_pile_is_playable = len(state.player_states[state.current_player].stock_pile) > 0 and (state.player_states[state.current_player].stock_pile[-1] == len(state.build_piles[0]) + 1 or state.player_states[state.current_player].stock_pile[-1] == 13)
        if len(state.player_states[state.current_player].stock_pile) == 0:
            print("Stock pile is empty, so it can't be played.")

        ps = state.player_states[state.current_player]
        nps = state.player_states[(state.current_player + 1) % len(state.player_states)]
        obs_py: list[int] = [
            ps.stock_pile[-1] if len(ps.stock_pile) > 0 else 0, # len 1
            len(ps.stock_pile), # len 1
            int(stock_pile_is_playable), # len 1
        ]
        obs_py += ps.hand # len 5
        hand_cards_are_playable = [card == 13 or any([card == len(pile) + 1 for pile in state.build_piles]) for card in ps.hand]
        obs_py += hand_cards_are_playable # len 5
        # len(build_pile) will give the effective value of each pile
        obs_py += [len(build_pile) for build_pile in state.build_piles] # len 4
        # the top 3 cards of each discard pile, left-padded with 0s, and the size of each pile
        discards = []
        for discard_pile in ps.discard_piles:
            discards += [0] * (3-len(discard_pile)) + discard_pile[-3:] + [len(discard_pile)]
        obs_py += discards # len 16
        obs_py += [
            nps.stock_pile[-1] if len(nps.stock_pile) > 0 else 0, # len 1
            len(nps.stock_pile)
        ] # len 1
        # the top card of each of nps's discard piles
        obs_py += [discard_pile[-1] if len(discard_pile) > 0 else 0 for discard_pile in nps.discard_piles] # len 4
        # total len 34
        obs = np.array(obs_py, dtype=np.int32)
        return {0: obs}

class HimaliaObsBuilder(ObsBuilder[int, np.ndarray, SkipBoState, tuple]):
    """A class to represent the observation builder."""
    def get_obs_space(self, agent):
        return 'real', 73
    
    def reset(self, agents, initial_state, shared_info):
        pass

    def build_obs(self, agents, state, shared_info):
        observations = {}

        ps = state.player_states[state.current_player]
        nps = state.player_states[(state.current_player + 1) % len(state.player_states)]
        obs_py: list[int] = [
            ps.stock_pile[-1] if len(ps.stock_pile) > 0 else 0, # len 1
            len(ps.stock_pile), # len 1
        ]
        obs_py += ps.hand # len 5
        # len(build_pile) will give the effective value of each pile
        obs_py += [len(build_pile) for build_pile in state.build_piles] # len 4
        # the top 3 cards of each discard pile, left-padded with 0s, and the size of each pile
        discards = []
        for discard_pile in ps.discard_piles:
            discards += [0] * (3-len(discard_pile)) + discard_pile[-3:] + [len(discard_pile)]
        obs_py += discards # len 16
        obs_py += [
            nps.stock_pile[-1] if len(nps.stock_pile) > 0 else 0, # len 1
            len(nps.stock_pile)
        ] # len 1
        # the top card of each of nps's discard piles
        obs_py += [discard_pile[-1] if len(discard_pile) > 0 else 0 for discard_pile in nps.discard_piles] # len 4
        # total len 33

        # now, find possible moves
        # here, dst is slightly different: 3 for build pile, 5-9 for discard pile
        possible_moves = []
        for src in range(10):
            for dst in range(4):
                action = SkipBoAction(src, dst)
                if SkipBoEngine.is_action_valid(action, state):
                    possible_moves.append((src, dst))
        if len(possible_moves) == 0:
            # we can't play anything, so we have to discard
            for src in range(1, 6):
                if ps.hand[src - 1] != 0:
                    for dst in range(4, 8):
                        possible_moves.append((src, dst))
        if len(possible_moves) > 20:
            print(f"Too many possible moves, reducing to 20: {possible_moves}")
            print(f"from state: {state}")
            # first, try to remove moves that are effectively duplicates (playing to two build piles with the same value, or sourcing from two cards from the hand with the same value)
            for i in range(len(possible_moves)):
                for j in range(i + 1, len(possible_moves)):
                    source_is_same_value = False
                    if possible_moves[i][0] >= 1 and possible_moves[i][0] <= 5 and possible_moves[j][0] >= 1 and possible_moves[j][0] <= 5:
                        # both moves are from the hand
                        if ps.hand[possible_moves[i][0] - 1] == ps.hand[possible_moves[j][0] - 1]:
                            source_is_same_value = True
                    dest_is_same_value = False
                    if possible_moves[i][1] >= 0 and possible_moves[i][1] <= 3 and possible_moves[j][1] >= 0 and possible_moves[j][1] <= 3:
                        # both moves are to build piles
                        if len(state.build_piles[possible_moves[i][1]]) == len(state.build_piles[possible_moves[j][1]]):
                            dest_is_same_value = True
                    if source_is_same_value or dest_is_same_value:
                        # remove the second move
                        removed = possible_moves.pop(j)
                        print(f"Removed duplicate move: {removed} at index {j}")
                        break
            # if we still have too many moves, just take the first 20
            if len(possible_moves) > 20:
                print(f"Too many possible moves, reducing to 20: {possible_moves}")
                possible_moves = possible_moves[:20]

        # fill the rest of possible moves with (-1, -1) to a length of 20
        while len(possible_moves) < 20:
            possible_moves.append((-1, -1))
        random.shuffle(possible_moves)
        # make sure the action parser knows the order of the moves
        shared_info['possible_moves'] = possible_moves
        for i in range(20):
            obs_py += [possible_moves[i][0], possible_moves[i][1]]
        # total len 73

        obs = np.array(obs_py, dtype=np.int32)
        return {0: obs}

class GeneralActionParser(ActionParser[int, np.ndarray, SkipBoAction, SkipBoState, tuple]):
    """A class to represent the action parser."""
    def __init__(self):
        self._lookup_table = self._generate_lookup_table()
    def get_action_space(self, agent):
        return 'discrete', len(self._lookup_table) # 10 sources, 8 destinations
    def reset(self, agents, initial_state, shared_info):
        pass
    def parse_actions(self, actions, state, shared_info):
        # print(f"actions: {actions}")
        parsed_actions = {}
        action = actions[0]
        parsed_action = SkipBoAction(
            card_source=self._lookup_table[action[0]][0], 
            card_destination=self._lookup_table[action[0]][1]
        )
        parsed_actions[0] = parsed_action
        return parsed_actions
    
    def _generate_lookup_table(self):
        """Generate a lookup table for the actions."""
        # 0: stock pile, 1-5: hand, 6-9: discard piles
        # 0-3: build piles, 4-7: discard piles
        # stock pile and discard piles can only play to build piles
        # hand can play to build piles and discard piles
        lut = []
        for src in range(10):
            for dest in range(8):
                if src == 0 or src >= 6:
                    # stock pile and discard piles can only play to build piles
                    if dest >= 0 and dest <= 3:
                        lut.append((src, dest))
                elif src >= 1 and src <= 5:
                    # hand can play to build piles and discard piles
                    lut.append((src, dest))
        return lut

class AmaltheaActionParser(ActionParser[int, np.ndarray, SkipBoAction, SkipBoState, tuple]):
    """A class to represent the action parser."""
    def __init__(self):
        self._lookup_table = self._generate_lookup_table()
    def get_action_space(self, agent):
        return 'discrete', len(self._lookup_table)
    def reset(self, agents, initial_state, shared_info):
        pass
    def parse_actions(self, actions, state, shared_info):
        # print(f"actions: {actions}")
        parsed_actions = {}
        action = actions[0]
        parsed_action = SkipBoAction(
            card_source=self._lookup_table[action[0]][0], 
            card_destination=self._lookup_table[action[0]][1]
        )
        # if the action is to discard, check if there are any other valid actions
        # if there are, don't allow the discard
        if parsed_action.card_destination >= 4 and parsed_action.card_destination <= 7:
            # check if there are any other valid actions
            for src in range(10):
                for dest in range(4):
                    if SkipBoEngine.is_action_valid(SkipBoAction(src, dest), state):
                        if src != parsed_action.card_source or dest != parsed_action.card_destination:
                            # there is another valid action, so block the discard by giving an invalid action
                            return {0: SkipBoAction(-1, -1)}
        parsed_actions[0] = parsed_action
        return parsed_actions
    
    def _generate_lookup_table(self):
        """Generate a lookup table for the actions."""
        # 0: stock pile, 1-5: hand, 6-9: discard piles
        # 0-3: build piles, 4-7: discard piles
        # stock pile and discard piles can only play to build piles
        # hand can play to build piles and discard piles
        lut = []
        for src in range(10):
            for dest in range(8):
                if src == 0 or src >= 6:
                    # stock pile and discard piles can only play to build piles
                    if dest >= 0 and dest <= 3:
                        lut.append((src, dest))
                elif src >= 1 and src <= 5:
                    # hand can play to build piles and discard piles
                    lut.append((src, dest))
        return lut

class HimaliaActionParser(ActionParser[int, np.ndarray, SkipBoAction, SkipBoState, tuple]):
    """A class to represent the action parser."""
    def get_action_space(self, agent):
        return 'discrete', 20 # 20 possible moves max
    def reset(self, agents, initial_state, shared_info):
        pass
    def parse_actions(self, actions, state, shared_info):
        # print(f"actions: {actions}")
        parsed_actions = {}
        action_idx = actions[0][0]
        shared_info["raw_action_idx"] = action_idx
        if 'possible_moves' not in shared_info:
            raise ValueError("No possible actions in shared info.")
        possible_actions = shared_info['possible_moves']
        # pick the valid action from the possible actions closest to the action
        # for example, if action_idx is 2, then try 2,3,1,4,0,5,6, etc. until there's a valid possible action
        # generate a list of indices to try
        indices_to_try = [action_idx]
        for i in range(1, 11):
            indices_to_try += [action_idx + i, action_idx - i]
        indices_to_try = [i % 20 for i in indices_to_try]
        for i in indices_to_try:
            src, dst = possible_actions[i]
            if src != -1 and dst != -1:
                # found an action
                parsed_action = SkipBoAction(src, dst)
                break
        else:
            # if no action was found, return an invalid action
            print(f"\033[31mNo valid action found for action idx {action_idx}. Choices: {shared_info['possible_moves']}\033[0m")
            parsed_action = SkipBoAction(-1, -1)
        parsed_actions[0] = parsed_action
        return parsed_actions

class SkipBoTerminalCondition(DoneCondition[int, SkipBoState]):
    """Determines when episodes end naturally (the game has been won)"""
    def reset(self, agents, initial_state, shared_info):
        pass
    def _is_done(self, agents, state: SkipBoState, shared_info):
        return any([len(player_state.stock_pile) == 0 for player_state in state.player_states])
    def is_done(self, agents: List[int], state: SkipBoState, shared_info: Dict[str, Any]) -> Dict[int, bool]:
        done = self._is_done(agents, state, shared_info)
        if done:
            # print("\033[32mF\033[0m", end="")
            pass
        return {0: done}

class SkipBoTruncationCondition(DoneCondition[int, SkipBoState]):
    """Determines when episodes are cut short (time limit reached, out of cards)"""
    def __init__(self, max_turns: int = 1000):
        super().__init__()
        self.max_turns = max_turns
    
    def reset(self, agents, initial_state, shared_info):
        pass
    
    def _is_done(self, agents, state, shared_info):
        # if the game has been going on for too long
        if state.num_turns >= self.max_turns:
            print("\033[31mGame has been going on for too long.\033[0m")
            return True
        # if there aren't enough cards in the draw pile + completed build piles
        if len(state.draw_pile) + len(state.completed_build_piles) < 20:
            print("\033[31mN\033[0m", end="")
            return True
        # if the invalid actions count is too high
        if state.invalid_actions_count >= 500:
            print("\033[31mI\033[0m", end="")
            return True
        return False
    
    def is_done(self, agents: List[int], state: SkipBoState, shared_info: Dict[str, Any]) -> Dict[int, bool]:
        # check if the game is done
        done = self._is_done(agents, state, shared_info)
        return {0: done}