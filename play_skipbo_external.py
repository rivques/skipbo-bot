# external mode: a human acts as the "eyes and hands" of the agent, managing its observations.
# in external mode, the human inputs the following things:
# - size and top card of the stock pile
# - cards in hand
# - effective value of each of the 4 build piles
# - size and top 3 cards of each of the 4 discard piles
# - size and top card of the opponent's stock pile
# - top card of the opponent's discard piles

from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Static, Select
from textual.containers import Vertical, Horizontal, Container
from textual.reactive import reactive
from textual.message import Message
from textual import events
import ast
from rich.markup import escape

from env import SkipBoAction

class SkipBoStateBuilder(Static):
    """Widget to build a SkipBoState interactively."""
    def compose(self) -> ComposeResult:
        # Player hand
        yield Static("Player Hand (comma-separated, 0 for empty):")
        self.hand_input = Input(placeholder="e.g. 1,2,0,0,13", id="hand")
        yield self.hand_input
        # Stock pile (top card and size)
        yield Static("Stock Pile Top Card:")
        self.stock_top_input = Input(placeholder="e.g. 5", id="stock_top")
        yield self.stock_top_input
        yield Static("Stock Pile Size:")
        self.stock_size_input = Input(placeholder="e.g. 10", id="stock_size")
        yield self.stock_size_input
        # Discard piles
        yield Static("Discard Piles (4, bottom-to-top, semicolon-separated):")
        self.discard_input = Input(placeholder="e.g. 1,2;3;0;4,5", id="discard")
        yield self.discard_input
        # Build piles (top card only)
        yield Static("Build Piles Top Card (4, comma-separated, 0 for empty):")
        self.build_top_input = Input(placeholder="e.g. 3,0,5,2", id="build_top")
        yield self.build_top_input
        # Opponent stock pile (top card and size)
        yield Static("Opponent Stock Pile Top Card:")
        self.opp_stock_top_input = Input(placeholder="e.g. 7", id="opp_stock_top")
        yield self.opp_stock_top_input
        yield Static("Opponent Stock Pile Size:")
        self.opp_stock_size_input = Input(placeholder="e.g. 8", id="opp_stock_size")
        yield self.opp_stock_size_input
        # Opponent discard piles (top card only)
        yield Static("Opponent Discard Piles Top Card (4, comma-separated, 0 for empty):")
        self.opp_discard_top_input = Input(placeholder="e.g. 0,0,2,1", id="opp_discard_top")
        yield self.opp_discard_top_input
        # Submit
        yield Button("Build State", id="build_state")
        self.status = Static("")
        yield self.status

    def append_status(self, msg: str):
        prev = str(self.status.renderable) if self.status.renderable else ""
        # Escape markup so it is shown as literal text
        self.status.update((prev + "\n" + msg.replace("[", "\\[")).strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "build_state":
            try:
                #self.append_status("Parsing hand...")
                hand = [int(x) for x in self.hand_input.value.split(",")]
                #self.append_status(f"Hand: {hand}")
                # Stock pile: backfill with zeroes to match size
                #self.append_status("Parsing stock pile...")
                stock_top = int(self.stock_top_input.value)
                stock_size = int(self.stock_size_input.value)
                stock = [0] * (stock_size - 1) + [stock_top] if stock_size > 0 else []
                #self.append_status(f"Stock: {stock}")
                #self.append_status("Parsing discards...")
                discards = [[int(y) for y in x.split(",") if y.strip()] for x in self.discard_input.value.split(";")]
                #self.append_status(f"Discards: {discards}")
                # Build piles: only top card, so create piles with that card if not 0
                #self.append_status("Parsing build piles...")
                build_tops = [int(x) for x in self.build_top_input.value.split(",")]
                build = [[v] * v if v > 0 else [] for v in build_tops]
                #self.append_status(f"Build piles: {build}")
                # Opponent stock pile: backfill with zeroes to match size
                #self.append_status("Parsing opponent stock pile...")
                opp_stock_top = int(self.opp_stock_top_input.value)
                opp_stock_size = int(self.opp_stock_size_input.value)
                opp_stock = [0] * (opp_stock_size - 1) + [opp_stock_top] if opp_stock_size > 0 else []
                #self.append_status(f"Opponent stock: {opp_stock}")
                # Opponent discard piles: only top card, so create piles with that card if not 0
                #self.append_status("Parsing opponent discards...")
                opp_discard_tops = [int(x) for x in self.opp_discard_top_input.value.split(",")]
                opp_discards = [[v] if v > 0 else [] for v in opp_discard_tops]
                #self.append_status(f"Opponent discards: {opp_discards}")
                from env import PlayerState, SkipBoState
                player_states = [
                    PlayerState(hand, stock, discards),
                    PlayerState([0]*5, opp_stock, opp_discards)
                ]
                #self.append_status("Building state object...")
                # Fill in missing info with reasonable defaults
                state = SkipBoState(
                    player_states=player_states,
                    current_player=0,
                    build_piles=build,
                    draw_pile=[],
                    completed_build_piles=[],
                    num_turns=0,
                    invalid_actions_count=0,
                    last_step=None
                )
                self.append_status(str(state))
                self.append_status("State built! Use below to select bot and get action.")
                self.post_message(self.StateBuilt(state))
            except Exception as e:
                self.append_status(f"Error: {e}")

    class StateBuilt(Message):
        def __init__(self, state):
            self.state = state
            super().__init__()

class BotActionPanel(Static):
    """Widget to select bot config and show action for a state."""
    state = reactive(None)
    agent = None
    def compose(self) -> ComposeResult:
        from bot_configs import configs
        yield Static("Select Bot Config:")
        self.bot_select = Select([(k, k) for k in configs.keys()], id="bot_select")
        yield self.bot_select
        yield Button("Get Action", id="get_action")
        self.action_out = Static("")
        yield self.action_out

    def append_status(self, msg: str):
        prev = str(self.action_out.renderable) if self.action_out.renderable else ""
        self.action_out.update((prev + "\n" + msg.replace("[", "\\[")).strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "get_action":
            self.action_out.update("")
            if self.state is None:
                self.append_status("No state set!")
                return
            from bot_configs import configs
            from bot_play import Agent
            bot_key = str(self.bot_select.value) if self.bot_select.value is not None else None
            if bot_key not in configs:
                self.append_status("Invalid bot config selected!")
                return
            config = configs[bot_key]
            # Only re-create the agent if the config changes
            if not hasattr(self, 'agent') or self.agent is None or getattr(self, '_agent_config', None) != config:
                self.agent = Agent(config)
                self._agent_config = config  # Save config for comparison
            try:
                obs = config.obs_builder.build_obs([0], self.state, {})[0]
                self.append_status(f"Obs: {obs}")
                action: SkipBoAction = self.agent.get_action(self.state)
                self.append_status(f"Action: {action}")
                # convert the action into the form "Play the {} from your {} onto the {} of the {}"
                # sources: 0 = stock pile, 1-5 = hand, 6-9 = discard piles
                # targets: 0-3 = build piles, 4-7 = discard piles
                src = action.card_source
                dest = action.card_destination
                src_card_value = 0
                dest_card_value = 0
                if src == 0:
                    src_str = "stock pile"
                    src_card_value = self.state.player_states[0].stock_pile[-1] if self.state.player_states[0].stock_pile else 0
                elif src in range(1, 6):
                    src_str = f"hand ({src})"
                    src_card_value = self.state.player_states[0].hand[src-1] if self.state.player_states[0].hand else 0
                elif src in range(6, 10):
                    src_str = f"discard pile ({src-5})"
                    src_card_value = self.state.player_states[0].discard_piles[src-6][-1] if self.state.player_states[0].discard_piles[src-6] else 0
                else:
                    src_str = "unknown source"
                if dest in range(0, 4):
                    dest_str = f"build pile ({dest})"
                    dest_card_value = self.state.build_piles[dest][-1] if self.state.build_piles[dest] else 0
                elif dest in range(4, 8):
                    dest_str = f"discard pile ({dest-3})"
                    dest_card_value = self.state.player_states[0].discard_piles[dest-4][-1] if self.state.player_states[0].discard_piles[dest-4] else 0
                else:
                    dest_str = "unknown destination"
                self.append_status(f"Action: Play the {src_card_value} from your {src_str} onto the {dest_card_value} of the {dest_str}")
            except Exception as e:
                self.append_status(f"Error: {e}")

class SkipBoExternalApp(App):
    CSS_PATH = None
    BINDINGS = [ ("q", "quit", "Quit") ]
    def compose(self) -> ComposeResult:
        self.state_builder = SkipBoStateBuilder()
        self.bot_panel = BotActionPanel()
        yield Vertical(
            self.state_builder,
            self.bot_panel
        )
    def on_skip_bo_state_builder_state_built(self, message: SkipBoStateBuilder.StateBuilt):
        self.bot_panel.state = message.state

if __name__ == "__main__":
    SkipBoExternalApp().run()
