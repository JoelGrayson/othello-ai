import numpy as np
from utils import check_move, check_terminal, get_score, number_of_empty_squares
from heuristic import heuristic

# <Typing
from typing import List, Tuple, Dict, Literal
scoreT=int
moveT=Tuple[int, int]
move_scoreT=Dict[Literal['score'] | Literal['best_move'], scoreT | moveT | None]
    # { score: scoreT | null, best_move: moveT | null }
    # need to use type: ignore whenever accessing dict's key ∵ of unknown typeof key
turnT=Literal[-1] | Literal[1]
boardT=np.ndarray
# >

# <Constants
INFINITY=9999999999 #instead of float(-inf) so it is an int, not a float
NEGATIVE_INFINITY=-9999999999
PASS_MOVE=(-1, -1)
SIZE=8
NUM_SQUARES=SIZE*SIZE
# max_depth=4 #variable
# >

def get_move(board, turn, time_left_seconds) -> moveT:
    # higher depth towards the start. Lower depth towards the end.
    max_depth=4

    if number_of_empty_squares(board)<NUM_SQUARES**2/2: #past halfway point
        max_depth=3
    if time_left_seconds<20: #lower depth to not run out of time
        max_depth=2
    move: moveT=ab_prune(NEGATIVE_INFINITY, INFINITY, PASS_MOVE, turn, board, max_depth, 0)['best_move'] #type: ignore
    return move

getMove=get_move #exported as camelCase

def ab_prune(
    alpha_score: scoreT,
    beta_score: scoreT,
    move: moveT,
    turn: turnT, #1 = black = max, -1 = white = min
    board: boardT,
    max_depth: int,
    depth: int=0,
) -> move_scoreT:
    # base case
    if check_terminal(board): #game over
        black_score, white_score=get_score(board)
        if black_score>white_score: #max wins
            return {'score': INFINITY-1, 'best_move': move }
        if white_score>black_score: #min wins
            return {'score': NEGATIVE_INFINITY+1, 'best_move': move }
        if white_score==black_score: #tie
            return { 'score': 0, 'best_move': move }
    
    all_moves=get_all_moves(board, turn)

    if len(all_moves)==0: #no legal moves
        return {
            "best_move": (-1, -1),
            "score": ab_prune(alpha_score, beta_score, move, -turn, board, max_depth, depth+1)['score']
        }


    if depth>max_depth:
        #  and number_of_empty_squares(board)>8 #exceeded depth and still have to recurse more (so use heuristic not continue calculating)
        return {
            "best_move": move,
            "score": heuristic(board)
        }

    # recursive step
    best_move=None #alpha or beta is score

    for move in all_moves:
        new_board=board.copy()
        stones_to_flip=check_move(new_board, move[0], move[1], turn)
        for stone in stones_to_flip:
            new_board[stone]=turn
        new_board[move]=turn
        
        new_score: scoreT=ab_prune(
            alpha_score,
            beta_score,
            move,
            -turn,
            new_board,
            max_depth,
            depth+1
        )['score'] #type: ignore

        if turn==1: #max
            # custom max/min function
            if new_score>alpha_score: #type: ignore # better score
                best_move=move
                alpha_score=new_score
        if turn==-1: #min
            if new_score<beta_score: #type: ignore # better score
                best_move=move
                beta_score=new_score

        if alpha_score>beta_score: #pruning
            return {
                "best_move": best_move,
                "score": alpha_score if turn==1 else beta_score #undesriable
            }
    
    if turn==1:
        return {
            "best_move": best_move,
            "score": alpha_score
        }
    if turn==-1:
        return {
            "best_move": best_move,
            "score": beta_score
        }
    


def get_all_moves(board, turn):
    moves: List[moveT]=[]
    for row in range(SIZE):
        for col in range(SIZE):
            if check_move(board, row, col, turn):
                moves.append((row, col))
    return moves
