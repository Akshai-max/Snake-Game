import os
import pickle
import random

import numpy as np

from game import Direction


class QAgent:
    def __init__(
        self,
        alpha=0.1,
        gamma=0.9,
        epsilon=1.0,
        epsilon_min=0.02,
        epsilon_decay=0.995,
        q_path="q_table.pkl",
    ):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_path = q_path
        self.q_table = {}
        self.load()

    def get_state(self, game):
        head_x, head_y = game.head
        block = game.block_size

        point_l = (head_x - block, head_y)
        point_r = (head_x + block, head_y)
        point_u = (head_x, head_y - block)
        point_d = (head_x, head_y + block)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        danger_straight = (
            (dir_r and game.is_collision(point_r))
            or (dir_l and game.is_collision(point_l))
            or (dir_u and game.is_collision(point_u))
            or (dir_d and game.is_collision(point_d))
        )
        danger_left = (
            (dir_u and game.is_collision(point_l))
            or (dir_d and game.is_collision(point_r))
            or (dir_l and game.is_collision(point_d))
            or (dir_r and game.is_collision(point_u))
        )
        danger_right = (
            (dir_d and game.is_collision(point_l))
            or (dir_u and game.is_collision(point_r))
            or (dir_r and game.is_collision(point_d))
            or (dir_l and game.is_collision(point_u))
        )

        food_x, food_y = game.food
        state = [
            danger_straight,
            danger_left,
            danger_right,
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            food_x < head_x,
            food_x > head_x,
            food_y < head_y,
            food_y > head_y,
        ]
        return tuple(int(value) for value in state)

    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 2)
        return int(np.argmax(self.q_values(state)))

    def q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(3, dtype=float)
        return self.q_table[state]

    def train_step(self, state, action, reward, next_state, done):
        current_q = self.q_values(state)[action]
        future_q = 0 if done else np.max(self.q_values(next_state))
        target = reward + self.gamma * future_q
        self.q_table[state][action] = current_q + self.alpha * (target - current_q)

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self):
        with open(self.q_path, "wb") as file:
            pickle.dump(self.q_table, file)

    def load(self):
        if os.path.exists(self.q_path):
            with open(self.q_path, "rb") as file:
                self.q_table = pickle.load(file)
