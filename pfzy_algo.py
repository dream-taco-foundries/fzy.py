#!/usr/bin/env python3

# Copy of https://github.com/jhawthorn/fzy.js

from typing import List, Optional
import math

# Scoring constants
SCORE_MIN = -math.inf
SCORE_MAX = math.inf

SCORE_GAP_LEADING = -0.005
SCORE_GAP_TRAILING = -0.005
SCORE_GAP_INNER = -0.01
SCORE_MATCH_CONSECUTIVE = 1.0
SCORE_MATCH_SLASH = 0.9
SCORE_MATCH_WORD = 0.8
SCORE_MATCH_CAPITAL = 0.7
SCORE_MATCH_DOT = 0.6

def precompute_bonus(haystack: str) -> List[float]:
    """Compute match bonuses for each position in the haystack string."""
    match_bonus = [0.0] * len(haystack)
    last_char = '/'

    for i, char in enumerate(haystack):
        if last_char == '/':
            match_bonus[i] = SCORE_MATCH_SLASH
        elif last_char in '-_ ':
            match_bonus[i] = SCORE_MATCH_WORD
        elif last_char == '.':
            match_bonus[i] = SCORE_MATCH_DOT
        elif last_char.islower() and char.isupper():
            match_bonus[i] = SCORE_MATCH_CAPITAL
        else:
            match_bonus[i] = 0
        last_char = char

    return match_bonus

def compute(needle: str, haystack: str) -> tuple[List[List[float]], List[List[float]]]:
    """Compute dynamic programming matrices for fuzzy string matching."""
    n, m = len(needle), len(haystack)
    needle_lower = needle.lower()
    haystack_lower = haystack.lower()
    match_bonus = precompute_bonus(haystack)

    D = [[SCORE_MIN] * m for _ in range(n)]
    M = [[SCORE_MIN] * m for _ in range(n)]

    for i in range(n):
        prev_score = SCORE_MIN
        gap_score = SCORE_GAP_TRAILING if i == n - 1 else SCORE_GAP_INNER

        for j in range(m):
            if needle_lower[i] == haystack_lower[j]:
                score = SCORE_MIN
                if i == 0:
                    score = j * SCORE_GAP_LEADING + match_bonus[j]
                elif j > 0:
                    score = max(
                        M[i-1][j-1] + match_bonus[j],
                        D[i-1][j-1] + SCORE_MATCH_CONSECUTIVE
                    )
                D[i][j] = score
                prev_score = M[i][j] = max(score, prev_score + gap_score)
            else:
                D[i][j] = SCORE_MIN
                prev_score = M[i][j] = prev_score + gap_score

    return D, M

def score(needle: str, haystack: str) -> float:
    """Calculate the fuzzy match score between needle and haystack."""
    n, m = len(needle), len(haystack)

    if n == 0 or m == 0:
        return SCORE_MIN
    if n == m:
        return SCORE_MAX
    if m > 1024:
        return SCORE_MIN

    D, M = compute(needle, haystack)
    return M[n-1][m-1]

def positions(needle: str, haystack: str) -> List[int]:
    """Find the positions of optimal matching characters."""
    n, m = len(needle), len(haystack)
    positions = [0] * n

    if n == 0 or m == 0:
        return positions
    if n == m:
        return list(range(n))
    if m > 1024:
        return positions

    D, M = compute(needle, haystack)

    match_required = False
    i, j = n - 1, m - 1

    while i >= 0:
        while j >= 0:
            if (D[i][j] != SCORE_MIN and
                (match_required or D[i][j] == M[i][j])):
                match_required = (i > 0 and j > 0 and
                                M[i][j] == D[i-1][j-1] + SCORE_MATCH_CONSECUTIVE)
                positions[i] = j
                j -= 1
                break
            j -= 1
        i -= 1

    return positions

def has_match(needle: str, haystack: str) -> bool:
    """Check if all characters in needle appear in order in haystack."""
    needle, haystack = needle.lower(), haystack.lower()
    j = 0

    for char in needle:
        j = haystack.find(char, j) + 1
        if not j:
            return False
    return True
