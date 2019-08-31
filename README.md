## Sudoku-Creater-Solver

### About
This project was created in an attempt to better understand Sudoku and learn strategies for solving NP-Hard problems. It is a simple Sudoku game; one that is playable, can load and save game states, can generate boards, and lastly can also solve them.

The program is able to solve sudoku problems extremely quickly, solving a board in under 0.01 seconds on average, with 99% of boards tested being solved in under 0.1 seconds.

Generating a board depends on the number of empty squares requested. With less than 40 empty squares, the script generates a board in about 0.1 seconds, but once we reach 55 empty squares, it takes ~2 seconds per generated board.

### Algorithms Used
Two main principles were used to solve a puzzle: 1. Searching and 2. Constraint propagation. To put it simply, we do a depth-first-search on the board, taking the square with the fewest possibilities left and randomly picking a value to insert there. We then eliminate this value from all the squares that can no longer contain this value. We continue to do this until there is a contradiction (or we are unable to add anymore values to the board), and thus at some point we went wrong. We cancel out of this branch, and continue on with another, every time eliminating an extremely large number of possibilities compared to a brute force search. We do this until we solve the board, and thus we can return it.

To create a board, we employ the solve_board function described above, however a little bit differently. We randomly create a solved board by picking a random square and then a random value and running our solve board function. This creates 81^9 different possible boards to begin with. We then randomly pick a square, remove it, and try all other number in that square and run our solve_board funciton. If it results in a solved board, we put the original number back, and try again with a different square. This is done inorder to ensure every board presented has only one solution.

### Main Code
To run the code, simply run *python sudoku.py*. I have provided 50 pre-made boards for you to load if you wish. 

Have fun!
