"""
Sample python script to show the process of choosing a Stable Baselines model,
training it with a chosen policy, and then evaluating the trained model on the
environment while visualising it
"""

import gym
import time

from datetime import datetime

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv

from code.wrappers import F110_Wrapped
from code.utility import make_vec_env


TRAIN_STEPS = pow(10, 5)  # for reference, it takes about one sec per 500 steps
MIN_EVAL_EPISODES = 5
NUM_PROCESS = 4
MAP_PATH = './f1tenth_gym/examples/example_map'
MAP_EXTENSION = '.png'


def main():

    #       #
    # TRAIN #
    #       #

    # create parallelised environments
    envs = make_vec_env('f110_gym:f110-v0',
                        n_envs=NUM_PROCESS,
                        wrapper_class=F110_Wrapped,
                        vec_env_cls=SubprocVecEnv,
                        env_kwargs={'map': MAP_PATH,
                                    'map_ext': MAP_EXTENSION,
                                    'num_agents': 1})

    # choose RL model and policy here
    model = PPO('MlpPolicy', envs, verbose=1)

    # train model and record time taken
    start_time = time.time()
    model.learn(total_timesteps=TRAIN_STEPS)
    print(f"Training time {time.time() - start_time:.2f}s")
    print('Training cycle complete.')

    # save model with unique timestamp
    timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    model.save(f"./train/ppo-f110-{timestamp}")

    #          #
    # EVALUATE #
    #          #

    # create evaluation environment (same as train environment in this case)
    eval_env = gym.make('f110_gym:f110-v0',
                        map='./f1tenth_gym/examples/example_map',
                        map_ext='.png',
                        num_agents=1)

    # wrap evaluation environment
    eval_env = F110_Wrapped(eval_env)

    # simulate a few episodes and render them, ctrl-c to cancel an episode
    episode = 0
    while episode < MIN_EVAL_EPISODES:
        try:
            episode += 1
            obs = eval_env.reset()
            done = False
            while not done:
                # use trained model to predict some action, using observations
                action, _ = model.predict(obs)
                obs, _, done, _ = eval_env.step(action)
                eval_env.render()
            # this section just asks the user if they want to run more episodes
            if episode == (MIN_EVAL_EPISODES - 1):
                choice = input('Another episode? (Y/N) ')
                if choice.replace(" ", "").lower() in ['y', 'yes']:
                    episode -= 1
                else:
                    episode = MIN_EVAL_EPISODES
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()