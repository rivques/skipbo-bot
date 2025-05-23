import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"

def build_rlgym_v2_env():
    from env import SkipBoMutator, HimaliaObsBuilder, HimaliaActionParser, SkipBoEngine, SkipBoTerminalCondition, SkipBoTruncationCondition
    from rewards import HimaliaReward

    from rlgym.api import RLGym

    return RLGym(
        state_mutator=SkipBoMutator(2, 20),
        obs_builder=HimaliaObsBuilder(),
        action_parser=HimaliaActionParser(),
        reward_fn=HimaliaReward(),
        transition_engine=SkipBoEngine(2),
        termination_cond=SkipBoTerminalCondition(),
        truncation_cond=SkipBoTruncationCondition(),
    )

if __name__ == "__main__":
    from typing import Tuple

    import numpy as np
    from rlgym_learn_algos.logging import (
        WandbMetricsLogger,
        WandbMetricsLoggerConfigModel,
    )
    from rlgym_learn_algos.ppo import (
        BasicCritic,
        DiscreteFF,
        ExperienceBufferConfigModel,
        GAETrajectoryProcessor,
        GAETrajectoryProcessorConfigModel,
        NumpyExperienceBuffer,
        PPOAgentController,
        PPOAgentControllerConfigModel,
        PPOLearnerConfigModel,
        PPOMetricsLogger,
    )

    from rlgym_learn import (
        BaseConfigModel,
        LearningCoordinator,
        LearningCoordinatorConfigModel,
        NumpySerdeConfig,
        ProcessConfigModel,
        PyAnySerdeType,
        SerdeTypesModel,
        generate_config,
    )

    # The obs_space_type and action_space_type are determined by your choice of ObsBuilder and ActionParser respectively.
    # The logic used here assumes you are using the types defined by the DefaultObs and LookupTableAction above.
    DefaultObsSpaceType = tuple[str, int]
    DefaultActionSpaceType = tuple[str, int]

    def actor_factory(
        obs_space: DefaultObsSpaceType,
        action_space: DefaultActionSpaceType,
        device: str,
    ):
        return DiscreteFF(obs_space[1], action_space[1], (256, 256, 256), device)

    def critic_factory(obs_space: DefaultObsSpaceType, device: str):
        return BasicCritic(obs_space[1], (256, 256, 256), device)

    ppo_agent_controller_config = PPOAgentControllerConfigModel(
                timesteps_per_iteration=50_000,
                save_every_ts=1_000_000,
                add_unix_timestamp=False,
                learner_config=PPOLearnerConfigModel(
                    ent_coef=0.01,  # Sets the entropy coefficient used in the PPO algorithm
                    actor_lr=5e-5,  # Sets the learning rate of the actor model
                    critic_lr=5e-5,  # Sets the learning rate of the critic model
                ),
                experience_buffer_config=ExperienceBufferConfigModel(
                    max_size=150_000,  # Sets the number of timesteps to store in the experience buffer. Old timesteps will be pruned to only store the most recently obtained timesteps.
                    trajectory_processor_config=GAETrajectoryProcessorConfigModel(),
                ),
                metrics_logger_config=WandbMetricsLoggerConfigModel(
                    project="skipbo",
                    group="rlgym-learn-prod",
                    run="pasiphae",
                ),
                run_name="pasiphae"
            )

    # Create the config that will be used for the run
    config = LearningCoordinatorConfigModel(
        base_config=BaseConfigModel(
            serde_types=SerdeTypesModel(
                agent_id_serde_type=PyAnySerdeType.INT(),
                action_serde_type=PyAnySerdeType.NUMPY(np.int64, config=NumpySerdeConfig.STATIC(shape=(1,))),
                obs_serde_type=PyAnySerdeType.NUMPY(np.int32),
                reward_serde_type=PyAnySerdeType.FLOAT(),
                obs_space_serde_type=PyAnySerdeType.TUPLE(
                    (PyAnySerdeType.STRING(), PyAnySerdeType.INT())
                ),
                action_space_serde_type=PyAnySerdeType.TUPLE(
                    (PyAnySerdeType.STRING(), PyAnySerdeType.INT())
                ),
            ),
            timestep_limit=2_000_100_000,  # Train for 2B steps
        ),
        process_config=ProcessConfigModel(
            n_proc=128,  # Number of processes to spawn to run environments. Increasing will use more RAM but should increase steps per second, up to a point
        ),
        agent_controllers_config={
            "PPO1": ppo_agent_controller_config,
            # "PPO2": ppo_agent_controller_config,
        },
        agent_controllers_save_folder="agent_controllers_checkpoints",  # (default value) WARNING: THIS PROCESS MAY DELETE ANYTHING INSIDE THIS FOLDER. This determines the parent folder for the runs for each agent controller. The runs folder for the agent controller will be this folder and then the agent controller config key as a subfolder.
    )

    # Generate the config file for reference (this file location can be
    # passed to the learning coordinator via config_location instead of defining
    # the config object in code and passing that)
    generate_config(
        learning_coordinator_config=config,
        config_location="config.json",
        force_overwrite=True,
    )

    learning_coordinator = LearningCoordinator(
        build_rlgym_v2_env,
        agent_controllers={
            "PPO1": PPOAgentController(
                actor_factory=actor_factory,
                critic_factory=critic_factory,
                experience_buffer=NumpyExperienceBuffer(GAETrajectoryProcessor()),
                metrics_logger=WandbMetricsLogger(PPOMetricsLogger()),
                obs_standardizer=None,
            ),
            # "PPO2": PPOAgentController(
            #     actor_factory=actor_factory,
            #     critic_factory=critic_factory,
            #     experience_buffer=NumpyExperienceBuffer(GAETrajectoryProcessor()),
            #     metrics_logger=WandbMetricsLogger(PPOMetricsLogger()),
            #     obs_standardizer=None,
            # )
        },
        config=config,
    )
    learning_coordinator.start()