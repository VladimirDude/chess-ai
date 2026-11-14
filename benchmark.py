import chess
import chess.engine
import time
import multiprocessing
import math
import random
from chess_tools import minimax, PIECE_VALUES
def get_engine_move(board, time_limit=5.0):
    start_time = time.time()
    best_move = None
    maximizing = (board.turn == chess.WHITE)
    for depth in range(1, 10):
        if time.time() - start_time > time_limit - 0.4:
            break
        try:
            score, move = minimax(board, depth, float('-inf'), float('inf'), maximizing)
            if move is not None:
                best_move = move
        except Exception:
            break
    if not best_move and list(board.legal_moves):
        best_move = random.choice(list(board.legal_moves))
    return best_move
def play_single_game(args):
    engine_is_white, stockfish_elo = args
    board = chess.Board()
    stockfish_path = "/opt/homebrew/bin/stockfish"
    try:
        sf_engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        sf_engine.configure({"UCI_LimitStrength": True, "UCI_Elo": stockfish_elo})
    except Exception as e:
        return "error"
    result = "draw"
    while not board.is_game_over(claim_draw=True):
        is_engine_turn = (board.turn == chess.WHITE) if engine_is_white else (board.turn == chess.BLACK)
        if is_engine_turn:
            move = get_engine_move(board, time_limit=5.0)
            if move in board.legal_moves:
                board.push(move)
            else:
                break
        else:
            try:
                res = sf_engine.play(board, chess.engine.Limit(time=5.0))
                if res.move in board.legal_moves:
                    board.push(res.move)
                else:
                    break
            except Exception:
                break
    sf_engine.quit()
    outcome = board.outcome(claim_draw=True)
    if outcome is None:
        return "draw"
    winner = outcome.winner
    if winner is None:
        return "draw"
    elif (winner == chess.WHITE) == engine_is_white:
        return "win"
    else:
        return "loss"
def calculate_elo(wins, draws, losses, opponent_elo):
    total = wins + draws + losses
    if total == 0:
        return opponent_elo, 0.0
    score = (wins + 0.5 * draws) / total
    if score >= 1.0:
        score = 0.99
    elif score <= 0.0:
        score = 0.01
    elo_diff = -400.0 * math.log10((1.0 / score) - 1.0)
    estimated_elo = opponent_elo + elo_diff
    std_error = (400.0 / math.log(10)) * math.sqrt((score * (1.0 - score)) / total)
    return round(estimated_elo, 1), round(std_error, 1)
def run_match_block(num_games, stockfish_elo, concurrency):
    print(f"\n--- Running {num_games} games against Stockfish @ {stockfish_elo} Elo (Concurrency: {concurrency}) ---")
    tasks = []
    for i in range(num_games):
        engine_is_white = (i % 2 == 0)
        tasks.append((engine_is_white, stockfish_elo))
    wins, draws, losses = 0, 0, 0
    with multiprocessing.Pool(processes=concurrency) as pool:
        results = pool.imap_unordered(play_single_game, tasks)
        for idx, res in enumerate(results, 1):
            if res == "win":
                wins += 1
            elif res == "loss":
                losses += 1
            else:
                draws += 1
            print(f"[{idx}/{num_games}] Result: {res.upper()} (Current W-D-L: {wins}-{draws}-{losses})")
    return wins, draws, losses
if __name__ == "__main__":
    multiprocessing.freeze_support()
    CONCURRENCY = 12
    print("=== Python Chess Engine Elo Benchmark Pipeline ===")
    initial_elo = 1400
    w, d, l = run_match_block(num_games=12, stockfish_elo=initial_elo, concurrency=CONCURRENCY)
    total_calib = w + d + l
    score_ratio = (w + 0.5 * d) / total_calib if total_calib > 0 else 0.5
    target_elo = initial_elo
    if score_ratio > 0.70:
        target_elo = initial_elo + 200
        print(f"\nYour engine dominated calibration (Score: {score_ratio:.2f}). Adjusting gauntlet Elo UP to {target_elo}.")
    elif score_ratio < 0.30:
        target_elo = max(1320, initial_elo - 200)
        print(f"\nYour engine struggled in calibration (Score: {score_ratio:.2f}). Adjusting gauntlet Elo DOWN to {target_elo}.")
    else:
        print(f"\nCalibration score balanced ({score_ratio:.2f}). Keeping gauntlet Elo at {target_elo}.")
    gw, gd, gl = run_match_block(num_games=48, stockfish_elo=target_elo, concurrency=CONCURRENCY)
    total_w = w + gw
    total_d = d + gd
    total_l = l + gl
    final_elo, error_margin = calculate_elo(gw, gd, gl, target_elo)
    print("\n" + "="*40)
    print("       FINAL BENCHMARK RESULTS")
    print("="*40)
    print(f"Total Games Played: {total_w + total_d + total_l}")
    print(f"Wins: {total_w} | Draws: {total_d} | Losses: {total_l}")
    print(f"Estimated Engine Elo: {final_elo} ± {error_margin}")
    print("="*40)