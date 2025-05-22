from env import AmaltheaActionParser, HimaliaActionParser, HimaliaObsBuilder, CallistoObsBuilder, GanymedeObsBuilder, GeneralActionParser, IoObsBuilder

from rlgym.api import ObsBuilder, ActionParser
from dataclasses import dataclass

@dataclass
class AgentConfig:
    data_path: str
    input_size: int
    n_actions: int
    layer_sizes: list
    obs_builder: ObsBuilder
    action_parser: ActionParser
    description: str
    skill_rating: str


configs = {
    "io": AgentConfig(
        data_path="agents/io/ppo_learner/actor.pt",
        input_size=33,
        n_actions=60,
        layer_sizes=[256, 256, 256],
        obs_builder=IoObsBuilder(),
        action_parser=GeneralActionParser(),
        description="The first agent successfully trained. However, it only knows how to discard.",
        skill_rating="0 - discard only",
    ),
    "europa": AgentConfig(
        data_path="agents/europa.pt",
        input_size=33,
        n_actions=60,
        layer_sizes=[256, 256, 256],
        obs_builder=IoObsBuilder(),
        action_parser=GeneralActionParser(),
        description="Eliminated the win reward and rewarded the stock pile more heavily.",
        skill_rating="0 - discard only",
    ),
    "ganymede": AgentConfig(
        data_path="agents/ganymede.pt",
        input_size=34,
        n_actions=60,
        layer_sizes=[256, 256, 256],
        obs_builder=GanymedeObsBuilder(),
        action_parser=GeneralActionParser(),
        description="Properly trained for 2 players, and also gets explicitly told when it can play the stock pile card.",
        skill_rating="0 - discard only",
    ),
    "callisto": AgentConfig(
        data_path="agents/callisto.pt",
        input_size=39,
        n_actions=60,
        layer_sizes=[256, 256, 256],
        obs_builder=CallistoObsBuilder(),
        action_parser=GeneralActionParser(),
        description="More strongly encouraged to play cards not to the discard pile.",
        skill_rating="0 - discard only",
    ),
    "amalthea": AgentConfig(
        data_path="agents/amalthea.pt",
        input_size=39,
        n_actions=60,
        layer_sizes=[256, 256, 256],
        obs_builder=CallistoObsBuilder(),
        action_parser=AmaltheaActionParser(),
        description="Entirely forbidden from playing to the discard pile when other moves are available.",
        skill_rating="1 - plays to the build piles, but not intelligently",
    ),
    "himalia": AgentConfig(
        data_path="agents/himalia.pt",
        input_size=73,
        n_actions=20,
        layer_sizes=[256, 256, 256],
        obs_builder=HimaliaObsBuilder(),
        action_parser=HimaliaActionParser(),
        description="Only allowed to pick from a list of possible moves.",
        skill_rating="1 - plays to build piles, but not intelligently",
    ),
    "elara": AgentConfig(
        data_path="agents/elara.pt",
        input_size=73,
        n_actions=20,
        layer_sizes=[256, 256, 256],
        obs_builder=HimaliaObsBuilder(),
        action_parser=HimaliaActionParser(),
        description="Same setup as Himalia, but trained for much longer.",
        skill_rating="2 - some signs of intelligent play",
    ),
}