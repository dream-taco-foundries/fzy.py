#!/usr/bin/env python3

import os, select, sys, termios, tty, re
from pfzy_algo import score, positions

NUM_ITEMS = 10

def getch():
    fd = sys.stdin.fileno()
    orig = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)  # or tty.setraw(fd) if you prefer raw mode's behavior.
        return os.read(fd, 0x100)
    except KeyboardInterrupt:
        tty_cleanup_for_exit()
        sys.exit(1)
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, orig)

def read_pipe_input():
    """
    Read input from a pipe if available (non-blocking).
    Returns None if no piped input is present.
    """
    # Check if there's input available on stdin without blocking
    return sys.stdin.read().strip()

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def tty_clearline():   eprint("\033[K", end="")
def tty_setcol(col=0): eprint(f"\033[{col+1}G", end="", flush=True)
def tty_invert():      eprint("\033[7m", end="")
def tty_setdefault():  eprint("\033[0m", end="")
def tty_clear_to_top(col=0):
    eprint(f"\033[{NUM_ITEMS}A", end="") # move up
    tty_setcol(col)
def tty_cleanup_for_exit():
    tty_setcol(0)
    for i in range(NUM_ITEMS):
        eprint()
        tty_clearline()
    eprint(f"\033[{NUM_ITEMS}A", end="", flush=True)

def update_matches():
    global matches
    pattern = '.*'.join(re.escape(c) for c in user_buf)
    regex = re.compile(pattern, re.IGNORECASE)
    matches = [s for s in pipe_lines if regex.search(s)]
    matches.sort(key=lambda s: -score(user_buf, s))

def print_match(line, invert=False):
    if invert: tty_invert()
    pos = positions(user_buf, line)
    for i, c in enumerate(line):
        if i in pos: eprint("\033[33m", end="") # yellow fg
        else:        eprint("\033[39m", end="") # default fg
        eprint(c, end="")
    tty_setdefault()

def draw_menu():
    tty_setcol(0)
    eprint(f"> {user_buf}", end="")
    tty_clearline()
    for i, line in enumerate(matches[:NUM_ITEMS]):
        eprint()
        tty_clearline()
        print_match(line, invert=(i == selected))
    for i in range(max(NUM_ITEMS-len(matches), 0)):
        eprint()
        tty_clearline()
        tty_setdefault()
        eprint("...", end="") # pad if not enough matches
    tty_clear_to_top()
    eprint(f"> {user_buf}", end="", flush=True)

pipe_lines = read_pipe_input().splitlines()
if len(pipe_lines) == 0:
    sys.exit(1)
elif len(pipe_lines) == 1:
    print(pipe_lines[0])
    sys.exit(0)

# Switch over to interactive input again
sys.stdin = open('/dev/tty', 'r')

user_buf = ""
matches = pipe_lines
selected = 0
while True:
    draw_menu()
    c = getch()
    if 0x20 <= int.from_bytes(c, "little") <= 0x7e:
        user_buf += chr(c[0])
    elif c[0] == 0x7f: # handle backspace
        user_buf = user_buf[:-1]
    elif c[0] in [ord('\n'), ord('\r')]:
        tty_cleanup_for_exit()
        print(matches[selected])
        break
    elif len(c) > 1:
        if c[1] == ord("["):
            if c[2] == ord("A"):   selected = max(selected-1, 0)
            elif c[2] == ord("B"): selected = min(selected+1, NUM_ITEMS-1)
    update_matches()
