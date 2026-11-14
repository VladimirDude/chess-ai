import sys
import os
import traceback
import chess
import chess_tools
from openings import get_opening_move
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash.log")
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
            print("id author Vard")
            print("uciok")
            sys.stdout.flush()
        elif command == "isready":
            print("readyok")
            sys.stdout.flush()
        elif command == "ucinewgame":
            board = chess.Board()
        elif command == "position":
            try:
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
            except Exception as e:
                sys.stderr.write(f"Error parsing position: {e}\n")
                sys.stderr.flush()
        elif command == "go":
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                print("bestmove 0000")
                sys.stdout.flush()
                continue
            
            # Lower default depth to 2 or 3 temporarily so it responds instantly
            depth = 3
            if "depth" in tokens:
                try:
                    depth_idx = tokens.index("depth")
                    depth = int(tokens[depth_idx + 1])
                except (ValueError, IndexError):
                    pass
            
            try:
                book_move = get_opening_move(board)
                if book_move and book_move in legal_moves:
                    best_move = book_move
                else:
                    _, best_move = chess_tools.minimax(board, depth, float('-inf'), float('inf'), board.turn)
            except Exception:
                best_move = None

            if best_move and best_move in legal_moves:
                print(f"bestmove {best_move.uci()}")
            else:
                print(f"bestmove {legal_moves[0].uci()}")
            sys.stdout.flush()
        elif command == "quit":
            break

if __name__ == "__main__":
    with open(LOG_PATH, "w") as f:
        f.write("Engine launched successfully.\n")
    try:
        uci_loop()
    except Exception:
        with open(LOG_PATH, "a") as f:
            traceback.print_exc(file=f)
        raise