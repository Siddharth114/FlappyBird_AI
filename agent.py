import torch
import random
from ai_game import *
from collections import deque
from model import Linear_QNet, QTrainer
from helper import plot

# global variables
MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.05

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(input_size=5, hidden_size=256, output_size=2)  # Make sure these dimensions are correct
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)


    def get_state(self, game):
        state = [
            # player coordinates
            game.player_y,
            # upcoming pipes with y coordinates
            game.upcoming_pipes[0]['y'] + game.pipe_height,
            game.upcoming_pipes[1]['y'],
            #distance to next pipe
            game.upcoming_pipes[0]['x'] - game.player_x,
            # vertical velocity
            game.player_velocity_y

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
        final_move = [0, 0]  # [don't flap, flap]
        
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 1)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            if len(state0.shape) == 1:  # Add this check to ensure proper dimensions
                state0 = torch.unsqueeze(state0, 0)  # Add batch dimension
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        
        return final_move



def train():
    move_history = []
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = FlappyBirdAI()
    total_reward = 0
    try:
        while True:
            state_old = agent.get_state(game)

            final_move = agent.get_action(state_old)
            
            # Convert one-hot action to boolean - index 1 represents "flap"
            action = final_move[1] == 1  # This converts to boolean
            
            # Safety checks for staying in bounds (can keep or remove these)
            if game.player_y >= 0.8*game.display_height:
                action = True
            elif game.player_y <= 0.2*game.display_height:
                action = False

            reward, done, score = game.play_step(action=action)  # Pass the boolean action

            total_reward += reward

            state_new = agent.get_state(game)

            # For training, pass the full final_move (one-hot encoded action)
            agent.train_short_memory(state_old, final_move, reward, state_new, done)
            agent.remember(state_old, final_move, reward, state_new, done)

            if done:
                total_reward = 0
                move_history = []
                game.reset()
                agent.n_games += 1 
                agent.train_long_memory()
                if score > record:
                    record = score
                    agent.model.save()

                plot_scores.append(score)
                total_score += score
                mean_scores = total_score/agent.n_games
                plot_mean_scores.append(mean_scores)
                plot(plot_scores, plot_mean_scores, False)
    except KeyboardInterrupt:
        plot(plot_scores, plot_mean_scores, True)


if __name__ == '__main__':
    train()
