import chess
import random

OPENING_BOOK = {
    (): ["e2e4", "d2d4", "c2c4"],
    ("e2e4",): ["e7e5", "c7c5", "e7e6", "c7c6", "g8f6", "d7d5"],
    ("e2e4", "e7e5"): ["g1f3", "f1c4", "b1c3"],
    ("e2e4", "e7e5", "g1f3"): ["b8c6", "g8f6", "d7d6"],
    ("e2e4", "e7e5", "g1f3", "b8c6"): ["f1c4", "f1b5", "d2d4"],
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4"): ["f8c5", "g8f6", "f8e7"],
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"): ["c2c3", "b2b4", "d2d3"],
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5"): ["a7a6", "g8f6", "f8c5", "d7d6"],
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6"): ["b5a4", "b5c6"],
    ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6", "b5a4"): ["g8f6", "b7b5", "d7d6"],
    ("d2d4",): ["d7d5", "g8f6", "e7e6", "f7f5"],
    ("d2d4", "d7d5"): ["c2c4", "g1f3", "e2e3"],
    ("d2d4", "d7d5", "c2c4"): ["e7e6", "c7c6", "d5c4", "e7e5"],
    ("d2d4", "d7d5", "c2c4", "e7e6"): ["b1c3", "g1f3"],
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3"): ["g8f6", "f8e7", "c7c5"],
    ("e2e4", "c7c5"): ["g1f3", "b1c3", "c2c3"],
    ("e2e4", "c7c5", "g1f3"): ["d7d6", "b8c6", "e7e6", "g8f6"],
    ("e2e4", "c7c5", "g1f3", "d7d6"): ["d2d4"],
    ("e2e4", "c7c5", "g1f3", "d7d6", "d2d4"): ["c5d4"],
    ("e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4"): ["f3d4"],
    ("e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4"): ["g8f6", "a7a6", "b8c6"],
    ("e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4", "g8f6"): ["b1c3"],
    ("e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4", "f3d4", "g8f6", "b1c3"): ["a7a6", "g7g6", "b8c6"], # Najdorf, Dragon, Scheveningen
    ("e2e4", "c7c5", "b1c3"): ["b8c6", "d7d6", "e7e6"],
    ("e2e4", "c7c5", "b1c3", "b8c6"): ["g2g3", "f1b5", "g1f3"],
    ("e2e4", "e7e6"): ["d2d4", "b1c3", "g1f3"],
    ("e2e4", "e7e6", "d2d4"): ["d7d5"],
    ("e2e4", "e7e6", "d2d4", "d7d5"): ["e4e5", "b1c3", "g1f3"],
    ("e2e4", "e7e6", "d2d4", "d7d5", "e4e5"): ["c7c5", "b8c6"],
    ("e2e4", "e7e6", "d2d4", "d7d5", "b1c3"): ["g8f6", "f8b4", "d5e4"],
    ("e2e4", "c7c6"): ["d2d4", "b1c3"],
    ("e2e4", "c7c6", "d2d4"): ["d7d5"],
    ("e2e4", "c7c6", "d2d4", "d7d5"): ["e4e5", "b1c3", "e3d5"],
    ("e2e4", "c7c6", "d2d4", "d7d5", "e4e5"): ["c8f5", "c7c5"],
    ("e2e4", "d7d5"): ["e4d5"],
    ("e2e4", "d7d5", "e4d5"): ["d8d5", "g8f6"],
    ("e2e4", "d7d5", "e4d5", "d8d5"): ["b1c3"],
    ("e2e4", "d7d5", "e4d5", "d8d5", "b1c3"): ["d5a5", "d5d8"],
    ("d2d4", "g8f6"): ["c2c4", "g1f3", "e2e3"],
    ("d2d4", "g8f6", "c2c4"): ["g7g6", "e7e6", "c7c6", "d7d5"],
    ("d2d4", "g8f6", "c2c4", "g7g6"): ["b1c3", "g1f3"],
    ("d2d4", "g8f6", "c2c4", "g7g6", "b1c3"): ["f8g7", "d7d5"],
    ("d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7"): ["e2e4", "g1f3"],
    ("d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7", "e2e4"): ["d7d6", "e8g8"],
    ("d2d4", "g8f6", "c2c4", "e7e6"): ["b1c3", "g1f3"],
    ("d2d4", "g8f6", "c2c4", "e7e6", "b1c3"): ["f8b4", "d7d5"],
    ("d2d4", "d7d5", "c2c4"): ["e7e6", "c7c6", "d5c4"],
    ("d2d4", "d7d5", "c2c4", "e7e6"): ["b1c3", "g1f3"],
    ("d2d4", "d7d5", "c2c4", "e7e6", "b1c3"): ["g8f6", "f8e7", "c7c5"],
    ("d2d4", "d7d5", "c2c4", "c7c6"): ["g1f3", "b1c3"],
    ("d2d4", "d7d5", "c2c4", "c7c6", "g1f3"): ["g8f6", "d5c4"],
}
def get_opening_move(board):
    if len(board.move_stack) > 20:
        return None
    history = tuple(m.uci() for m in board.move_stack)
    if history in OPENING_BOOK:
        candidates = OPENING_BOOK[history]
        if candidates:
            random.shuffle(candidates)
            for move_str in candidates:
                move = chess.Move.from_uci(move_str)
                if move in board.save_move if hasattr(board, 'save_move') else (move in board.legal_moves):
                    return move
    return None