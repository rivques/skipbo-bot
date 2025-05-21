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
    
    def is_action_valid(self, action: SkipBoAction, state: SkipBoState) -> bool:
        """Check if an action is valid."""
        # check if the action is valid
        # 0: stock pile, 1-5: hand, 6-9: discard piles
        # 0-3: build piles, 4-7: discard piles
        card_source = action.card_source
        card_destination = action.card_destination

        ps = state.player_states[state.current_player]

        source_value = 0
        if card_source == 0:
            source_value = ps.stock_pile[-1]
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
            return card_source >= 1 and card_source <= 5 # can only discard from hand
        else:
            return False


    def step(self, actions: Dict[int, SkipBoAction], shared_info: Dict[str, Any]) -> SkipBoState:
        """Step the game forward by one action."""
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
            result += f"Player {i}: Stock pile: {len(player_state.stock_pile)} cards, top card: {player_state.stock_pile[-1] if len(player_state.stock_pile) > 0 else 0}, Discard piles tops: {[discard_pile[-1] if len(discard_pile) > 0 else 0 for discard_pile in player_state.discard_piles]}\n"
        result += f"Build piles: {self._state.build_piles}\n"
        result += f"Draw pile: {len(self._state.draw_pile)} cards\n"
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

class SkipBoObsBuilder(ObsBuilder[int, np.ndarray, SkipBoState, tuple]):
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

class SkipBoActionParser(ActionParser[int, np.ndarray, SkipBoAction, SkipBoState, tuple]):
    """A class to represent the action parser."""
    def get_action_space(self, agent):
        return 'real', 2
    def reset(self, agents, initial_state, shared_info):
        pass
    def parse_actions(self, actions, state, shared_info):
        parsed_actions = {}
        action = actions[0]
        parsed_action = SkipBoAction(
            card_source=int(action[0]),
            card_destination=int(action[1])
        )
        parsed_actions[0] = parsed_action
        return parsed_actions

class SkipBoTerminalCondition(DoneCondition[int, SkipBoState]):
    """Determines when episodes end naturally (the game has been won)"""
    def reset(self, agents, initial_state, shared_info):
        pass
    def _is_done(self, agents, state, shared_info):
        return any([len(player_state.stock_pile) == 0 for player_state in state.player_states])
    def is_done(self, agents: List[int], state: SkipBoState, shared_info: Dict[str, Any]) -> Dict[int, bool]:
        done = self._is_done(agents, state, shared_info)
        return {0: done}

class SkipBoTruncationCondition(DoneCondition[int, SkipBoState]):
    """Determines when episodes are cut short (time limit reached, out of cards)"""
    def __init__(self, max_turns: int = 250):
        super().__init__()
        self.max_turns = max_turns
    
    def reset(self, agents, initial_state, shared_info):
        pass
    
    def _is_done(self, agents, state, shared_info):
        # if the game has been going on for too long
        if state.num_turns >= self.max_turns:
            return True
        # if there aren't enough cards in the draw pile + completed build piles
        if len(state.draw_pile) + len(state.completed_build_piles) < 20:
            return True
        # if the invalid actions count is too high
        if state.invalid_actions_count >= 5:
            return True
        return False
    
    def is_done(self, agents: List[int], state: SkipBoState, shared_info: Dict[str, Any]) -> Dict[int, bool]:
        # check if the game is done
        done = self._is_done(agents, state, shared_info)
        return {0: done}