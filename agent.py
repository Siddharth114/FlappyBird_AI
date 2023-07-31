import torch
import random
import numpy as np
from ai_game import *
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(10, 200, 1)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
        state = [
            # player coordinates
            game.player_x,
            game.player_y,
            # upcoming upper pipes with coordinates
            game.upcoming_pipes[0]['x'],
            game.upcoming_pipes[0]['y'],
            game.upcoming_pipes[1]['x'],
            game.upcoming_pipes[1]['y'],
            # upcoming lower pipes with coordinates
            game.upcoming_pipes[2]['x'],
            game.upcoming_pipes[2]['y'],
            game.upcoming_pipes[3]['x'],
            game.upcoming_pipes[3]['y']
        ]
        return state

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))


    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        
        # states, actions, rewards, next_states, dones = zip(*mini_sample)
        # self.trainer.train_step(states, actions, rewards, next_states, dones)
        for state, action, reward, next_state, done in mini_sample:
            self.trainer.train_step(state, action, reward, next_state, done)


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)



    def get_action(self, state):
        self.epsilon = 80 - self.n_games
        final_move = False
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,1)
            final_move = move%2
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)

            move = round(prediction.item())
            final_move = move%2

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = FlappyBirdAI()
    while True:
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)

        reward, done, score = game.play_step(action = bool(final_move))


        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.n_games +=1 
            agent.train_long_memory()
            if score > record:
                record = score
                agent.model.save()

            print('Game=', agent.n_games, 'Score=', score, 'Record=', record)

            plot_scores.append(score)
            total_score += score
            mean_scores = total_score/agent.n_games
            plot_mean_scores.append(mean_scores)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()
