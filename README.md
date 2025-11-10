# pfzy

This is a direct port of jhawthorn's [fzy](https://github.com/jhawthorn/fzy)/[fzy.js](https://github.com/jhawthorn/fzy.js) tool to python, because I needed a CLI fuzzy finder written in python.

All credit goes to the jhawthorn for the fzy implementation. I just slapped on a minimal python frontend to mimic the original C tool.

# Installation

Symlink the python script to a convenient name, e.g. `fzy` or `pfzy` and use it like the original.
```
sudo ln -s ~/pfzy/pfzy.py /usr/local/bin/pfzy
```

# Usage

Pipe commands to pfzy so you can fuzzily select items.
```
# Fuzzily select a file in the current directory to edit with vim
vim $(ls -1 | pfzy)
```

Check out the [fzf examples page](https://github.com/junegunn/fzf/wiki/Examples) for more ideas about how to use fzy/fzf.

I recommend pairing this python fzy implementation with [https://github.com/duong-db/fzf-simple-completion](https://github.com/duong-db/fzf-simple-completion) to get a simple bash completion system going. You can replace the fzf invocations with pfzy, while also getting rid of the fzf-specific command-line arguments.
