import chess
from openings import get_opening_move
import chess.polyglot
import time
transportation_table = {}

PASSED_PAWN_BONUS = [0, 10, 20, 35, 60, 100, 200, 0]
ISOLATED_PAWN_PENALTY = -15
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}
PHASE_WEIGHTS = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 1,
    chess.ROOK: 2,
    chess.QUEEN: 4,
    chess.KING: 0
}
TOTAL_PHASE = 24
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]
ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]
KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]
KING_ENDGAME_TABLE = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
]
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]
PIECE_TABLES = MG_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE
}
EG_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_ENDGAME_TABLE
}
def evaluate_board(board):
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    mg_score = 0
    eg_score = 0
    game_phase = 0
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            ptype = piece.piece_type
            color = piece.color
            game_phase += PHASE_WEIGHTS.get(ptype, 0)
            val = PIECE_VALUES[ptype]
            sq = square ^ 56 if color == chess.WHITE else square
            mg_table = MG_TABLES.get(ptype)
            eg_table = EG_TABLES.get(ptype)
            mg_pst = mg_table[sq] if mg_table else 0
            eg_pst = eg_table[sq] if eg_table else 0
            piece_mg = val + mg_pst
            piece_eg = val + eg_pst
            # ---------------------
            if ptype == chess.PAWN:
                file_idx = chess.square_file(square)
                rank_idx = chess.square_rank(square)
                is_passed = True
                if color == chess.WHITE:
                    for r in range(rank_idx + 1, 8):
                        for f in range(max(0, file_idx - 1), min(8, file_idx + 2)):
                            if chess.square(f, r) in black_pawns:
                                is_passed = False
                                break
                        if not is_passed:
                                break
                    if is_passed:
                        piece_mg += PASSED_PAWN_BONUS[rank_idx] 
                        piece_eg += PASSED_PAWN_BONUS[rank_idx] * 2
                else:
                    b_rank_idx = 7 - rank_idx
                    for r in range(0, rank_idx):
                        for f in range(max(0, file_idx - 1), min(8, file_idx + 2)):
                            if chess.square(f, r) in white_pawns:
                                is_passed = False
                                break
                        if not is_passed:
                            break
                    if is_passed:
                        piece_mg += PASSED_PAWN_BONUS[b_rank_idx] 
                        piece_eg += PASSED_PAWN_BONUS[b_rank_idx] * 2
                has_neighbours = False
                friendly_pawns = white_pawns if color == chess.WHITE else black_pawns
                for f in [file_idx - 1, file_idx + 1]:
                    if 0 <= f <= 7:
                        if any(chess.square_file(p) == f for p in friendly_pawns):
                            has_neighbours = True
                            break
                if not has_neighbours:
                    piece_mg += ISOLATED_PAWN_PENALTY
                    piece_eg += ISOLATED_PAWN_PENALTY
            if color == chess.WHITE:
                mg_score += piece_mg
                eg_score += piece_eg
            else:
                mg_score -= piece_mg
                eg_score -= piece_eg
    game_phase = min(game_phase, TOTAL_PHASE)
    eval_score = (mg_score * game_phase + eg_score * (TOTAL_PHASE - game_phase)) / TOTAL_PHASE
    return int(eval_score)
def get_ordered_moves(board, tt_move = None):
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return []
    if tt_move and tt_move in legal_moves:
        legal_moves.remove(tt_move)
        sorted_rest = sorted(legal_moves, key = lambda m: score_move(board, m), reverse = True)
        return [tt_move] + sorted_rest
    return sorted(legal_moves, key = lambda m: score_move(board, m), reverse = True)
def minimax(board, depth, alpha, beta, maximizing_player, ply = 0):
    original_alpha = alpha
    original_beta = beta
    board_hash = chess.polyglot.zobrist_hash(board)
    best_move_found = None
    if board.is_checkmate():
        return(-99999 + ply) if board.turn == chess.WHITE else (99999 - ply), None
    if board_hash in transportation_table:
        entry = transportation_table[board_hash]
        if entry["depth"] >= depth:
            score = entry["score"]
            bound = entry.get("bound", 0)
            best_move_found = entry.get("best_move", None)
            if bound == 0:
                return score, best_move_found
            elif bound == 1 and score >= beta:
                return score, best_move_found
            elif bound == 2 and score <= alpha:
                return score, best_move_found
    if board.is_repetition(3) or board.can_claim_fifty_moves():
        return 0, None
    if board.is_game_over():
        return evaluate_board(board), None
    if depth == 0:
        return quiescence_search(board, alpha, beta, maximizing_player), None
    if maximizing_player:
        max_eval = float('-inf')
        best_move = None
        sorted_moves = get_ordered_moves(board, best_move_found)
        for move in sorted_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, False, ply + 1)
            board.pop()
            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        if max_eval >= original_beta:
            bound = 1
        elif max_eval > original_alpha:
            bound = 0
        else:
            bound = 2
        transportation_table[board_hash] = {
            "depth": depth, 
            "score": max_eval, 
            "bound": bound,
            "best_move": best_move
        }
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        sorted_moves = get_ordered_moves(board, best_move_found)
        for move in sorted_moves:
            board.push(move)
            eval, _ = minimax(board, depth - 1, alpha, beta, True, ply + 1)
            board.pop()
            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        if min_eval <= original_alpha:
            bound = 2
        elif min_eval < original_beta:
            bound = 0
        else:
            bound = 1
        transportation_table[board_hash] = {
            "depth": depth, 
            "score": min_eval, 
            "bound": bound,
            "best_move": best_move
        }
        return min_eval, best_move
def score_move(board, move):
    if board.is_capture(move):
        target_piece = board.piece_at(move.to_square)
        victim_type = target_piece.piece_type if target_piece else chess.PAWN
        attacker_piece = board.piece_at(move.from_square)
        attacker_type = attacker_piece.piece_type if attacker_piece else chess.PAWN
        score = (PIECE_VALUES[victim_type]*10 - PIECE_VALUES[attacker_type] + 10000)
        return score
    piece = board.piece_at(move.from_square)
    if piece:
        sq_to = move.to_square ^56 if piece.color == chess.WHITE else move.to_square
        table = PIECE_TABLES.get(piece.piece_type)
        if table:
            return table[sq_to]
    return 0
def quiescence_search(board, alpha, beta, maximizing_player):
    stand_pat = evaluate_board(board)
    if maximizing_player:
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
        captures = [m for m in board.legal_moves if board.is_capture(m)]
        sorted_captures = sorted(captures, key = lambda m: score_move(board, m), reverse = True)
        for move in sorted_captures:
            board.push(move)
            score = quiescence_search(board, alpha, beta, False)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
    else:
        if stand_pat <= alpha:
            return alpha
        if stand_pat < beta:
            beta = stand_pat
        captures = [m for m in board.legal_moves if board.is_capture(m)]
        sorted_captures = sorted(captures, key = lambda m: score_move(board, m), reverse = True)
        for move in sorted_captures:
            board.push(move)
            score = quiescence_search(board, alpha, beta, True)
            board.pop()
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
        return beta