# Final Report - Nunzio Messineo s315067

## Lab 1: Set cover problem using A* algorithm

I implemented the A* algorithm, utilizing a heuristic function that estimates the minimum number of steps required to cover all remaining elements, assuming each step covers the maximum possible number of elements. In this approach, the g function corresponds to the length of the set of current states taken. The chosen heuristic function satisfies the admissibility and consistency properties, ensuring the optimality of the solution through an optimistic heuristic estimate.

Upon reviewing the professor's solution, I found it to be superior to mine. Consequently, I opted to adopt the professor's approach in my implementation.

## Lab 10: Tic-Tac-Toe with Reinforcement Learning

In this lab, I developed two classes: TicTacToe and QLearningAgent. The TicTacToe class handles the game mechanics, while the QLearningAgent class implements the Q-learning algorithm, incorporating parameters such as exploration rate, learning rate, discount factor, and a dictionary (hashmap) to store quality values. Quality values are determined using the Bellman equation, where the reward at the end of the game is 0 for a draw, 1 if the agent wins, and -1 if the agent loses.

The agent is trained using the train method and can subsequently play using the play method. Initially, the agent was trained against another agent. However, in a subsequent implementation, I opted to train the agent against a random player. Additionally, I modified the updating values to consider only the current state and reward. For a losing game, I adjusted the reward to -0.5 to prioritize winning moves. Furthermore, I refined the visualization of results for clarity.

Despite these adjustments, both implementations yielded unsatisfactory results.

### Reviews received

#### Review 1
Name: Gabriele Tomatis (S313848)
Github: https://github.com/GabriTom/Computational-Intelligence/

Clarity of the code:
The code is well written and well structured. There are not text blocks, but the comments make the code very understandable and readable. Every section does its own and the class division helps the clarity of the code. Maybe you could define some variables instead of write the number of epochs as hard-coded (in main function). In my opinion results are too verbose, you could simply put the output of the matches and maybe some statistics of them instead of the reward every 1000 episodes; but this is not a big issue.

Q-Learning strategy:
The strategy seem well implemented. From the choice for the initial parameters (epsilon=0.05, alpha=0.5, gamma=0.9) to the update of the q-value done with an effective formula. All fo this passes through a dictionary that uses hashed keys. This is a good way to implement the structure for this problem. Consider varying initial parameters in order to obtain the optimal ones; they seem well estimated by the way. Since the print has no information about winning/loosing rate it is diffucult to say if this strategy is working for this problem, but is well implemented; so I guess that.

Overall Evaluation:
This code is very linear and understandable. Q-learning strategy is well implemented, so good job!

#### Review 2
Name: Rita Mendes
Github: https://github.com/class1c-j/polito-ci-labs

Hello, I'm doing a peer review on your lab 10 code, and here's what I found, in the hope that it can help you with the final project as well:

First, you don't show statistics like winning rate, which helps assess how the agent is doing;
You show the total reward across the training time, but that just seems to be getting lower and lower, meaning the agent is not improving. Did you think of anything that could explain or solve that?
You only reward your agent at the end of each game, but in q-learning, the goal is to reward each move, so the agent learns the best play for each state.
You calculate the max of the next state, which is the opponent's turn, which may lead to a naive agent.
I hope this was helpful, either way, good job and good luck for the exam!

### Reviews done

#### Review 1
Name: Raffaele Viola
Github: https://github.com/RaffaeleViola/computational-intelligence/

I found the code complete and highly modular, indicative of good programming practices. The readme is well-crafted and significantly simplifies the understanding of the code, although it's not strictly necessary since, thanks to the comments, it is quite self-explanatory. The Q-learning-based agent is well implemented with a good selection of parameters. In particular, the use of epsilon, which decreases exponentially with the progression of episodes, was an excellent choice.
A possible suggestion could be to reorganize the code to make it more linear.
Overall, I find it to be an excellent implementation of the Tic Tac Toe game algorithm with reinforcement learning, well done!

#### Review 2
Name: Gabriele Tomatis
Github: https://github.com/GabriTom/Computational-Intelligence/

The code is well-organized into classes and functions, making the program's structure clear and easily understandable. Furthermore, the comments provide valuable insights into its functioning across all its parts. The Q-learning-based agent is well-implemented with a good selection of parameters. In general, the MinMax algorithm provides a useful evaluation of the system's performance, and the code proves to be effective, winning the majority of the time against the random algorithm.

Regarding suggestions, perhaps additional comments on the results in the benchmark function would clarify the logic, making it easier to understand what they are doing and providing more context to the results.

Overall, I find it to be an excellent implementation of the Tic Tac Toe game algorithm with reinforcement learning, good job!

## Exam Project: Quixo Game


For this work I've decided to develop a player based on the **MinMax algorithm**. The `alpha-beta pruning` was implemented to optimize the search for the best move by pruning branches that are not likely to influece the final decision.

The **Evaluation function** used to estimate the value of a given state, ir returns 10 for a win, -10 for a loss and if the game is not over return a value based on the longest sequence of the mark player. In particular it returns +/- 1 if the longest sequence divided by the dimension of the board is equal to 1 otherwise this value is diveded by 2 [ 0;0.4 ]. (The positive value is for the max player and the negative for the opponent).

For convenience I modify the Game and Move classes to be more suitable for my code. 
- In *MyMove class* I simply modify the order of the possible move in a way that consent me to change the move based on the rotation of the board. 
- In *MyGame class* I modify the method __move that perform the move changing the order of the passed position coordinates to more suitable for my code. I also add two methods: get_possible_cubes and is_acceptable_slide.

To increase the performance of the algorithm I've implemented a cache to store the value of the states already evaluated. This `cache` is a dictionary (HashMap) that for each hash(cube, slide, board) corresponde the value. This cache is used to avoid to re-evaluate the same state multiple times (sort of Memoization) and it is reintialized at each move of the opponent. Also to avoid to store repeated states the board saved is an univesal cache that can be used by max and min player. The board is saved with '+' for the moving player and '-' for the opponent. 

Also to avoid to consider situation that are the same but rotated I've implemented a `rotation` of the board in a way to correspond at each rotation one only entry of the cache. For doing this I've implemented these methods in My_MinMax_Player class: rotate_board, rotate_cube, transform_slide and check_rotations.

The results against a Random player are quite good because My_MinMax_Player obtain a winning rate of around 98% both if it starts first or not.