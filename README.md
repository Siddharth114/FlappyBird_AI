# Flappy Bird AI using Reinforcement Learning and Neural Networks
## Introduction
This is a Flappy Bird AI project. In this project, I have created a basic clone of the popular Flappy Bird game and implemented an AI agent using reinforcement learning to play the game. The AI agent is trained using a neural network built with PyTorch.

## How to Play the Game
To play the game manually, simply run the Python script and press the space bar to make the bird flap and avoid the pipes. The objective is to keep the bird alive for as long as possible and score points by passing through the gaps between the pipes.

![Screenshot 2023-08-04 at 7 55 38 AM](https://github.com/Siddharth114/FlappyBird_AI/assets/90757474/835f5752-a790-437a-82a8-837ec5f31116)

## AI Controlled Game
In addition to the manual gameplay, I have incorporated an AI-controlled game where an agent learns to play Flappy Bird through reinforcement learning. The AI agent observes the current state of the game and takes actions (flapping or not flapping) to maximize its cumulative reward over time. By using reinforcement learning, the agent learns from its actions and iteratively improves its gameplay strategy.

## Neural Network Architecture
To facilitate the AI agent's decision-making process, I built a neural network using PyTorch. The neural network takes the state of the game as input and predicts the best action to take. The state space consists of three variables: the player's position, the distance to the next pipe, and the vertical position of the opening of the pipe. These variables are fed into the neural network, which outputs the action (flap or not flap) that the AI agent should take in the current state.

## Reward System
The AI agent's learning process is driven by a reward system. I designed the reward system as follows:

* **Death**: If the AI agent crashes into a pipe or goes out of bounds, it receives a penalty of -1000 to discourage such behavior.
* **Staying Alive**: Initially, the agent receives a negative reward for each frame that it stays alive. This negative reward diminishes over time, motivating the agent to find a more optimal strategy.
* **Scoring Points**: The agent receives a reward of 0 for staying alive without scoring points, and an additional reward of 0 for scoring a point by passing through a gap between the pipes. If a reward were to be given for scoring a point, after a certain point in the game, the AI would be rewarded with a net positive reward.

## Limitations and Future Work
Despite the promising progress of the AI agent, there are some limitations and areas for future improvement:

* **Computing Power**: Due to limited facilities and resources, I was unable to let the model run for a large number of epochs, which would result in an optimally trained model that surpasses any form of human play. However, I observed that the model shows signs of improvement after approximately 100 epochs, indicating the potential for further enhancement with increased computing power.

* **Exploding Gradients/Vanishing Gradients**: One challenge encountered during training is the issue of the model getting stuck in a loop of vanishing or exploding gradients, where it returns only one action (either jump or no jump) regardless of the state space. This phenomenon occurs intermittently and takes around 20 episodes to get the model back on track. To address this, I plan to explore techniques to circumvent this problem, such as implementing gradient clipping or adjusting the neural network architecture.

## Project Objective
The main objective of this project was not to build the best AI for playing Flappy Bird, as that has been done before. Instead, I focused on visualizing how the AI evolves and improves its gameplay as it learns and relearns from its experiences. The learning process showcases the power of reinforcement learning and the potential of neural networks in teaching AI agents to excel at complex tasks.


https://github.com/Siddharth114/FlappyBird_AI/assets/90757474/18db1d6f-c2c5-4741-b8ae-d9d6d56f7945

