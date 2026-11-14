import sys
import chess
import chess_tools
from openings import get_opening_move

def uci_loop():
    board = chess.Board()
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line:
            continue
        tokens = line.strip().split()
        command = tokens[0]
        if command == "uci":
            print("id name ChessAI")
            print("id name Author: Vard")
            print("uciok")
            sys.stdout.flush()
        elif command == "isready":
            print("readyok")
            sys.stdout.flush()
        elif command == "ucinewgame":
            board = chess.Board()
        elif command == "position":
            if tokens[1] == "startpos":
                board = chess.Board()
                if len(tokens) > 2 and tokens[2] == "moves":
                    for move_str in tokens[3:]:
                        board.push(chess.Move.from_uci(move_str))
            elif tokens[1] == "fen":
                fen_parts = []
                idx = 2
                while idx < len(tokens) and tokens[idx] != "moves":
                    fen_parts.append(tokens[idx])
                    idx += 1
                board = chess.Board(" ".join(fen_parts))
                if idx < len(tokens) and tokens[idx] == "moves":
                    for move_str in tokens[idx+1:]:
                        board.push(chess.Move.from_uci(move_str))    
        elif command == "go":
            best_move = get_best_move(board, tokens) 
            if best_move:
                print(f"bestmove {best_move.uci()}")
            else:
                print(f"bestmove {list(board.legal_moves)[0].uci()}")
            sys.stdout.flush()
        elif command == "quit":
            break
def get_best_move(board, tokens):
    try:
        book_move = get_opening_move(board)
        if book_move:
            return book_move
    except Exception:
        pass
    depth = 5
    if "depth" in tokens:
        try:
            depth_idx = tokens.index("depth")
            depth = int(tokens[depth_idx + 1])
        except (ValueError, IndexError):
            pass
    if hasattr(chess_tools, "get_best_move"):
        return chess_tools.get_best_move(board, depth)
    else:
        return list(board.legal_moves)[0]
if __name__ == "__main__":
    uci_loop()