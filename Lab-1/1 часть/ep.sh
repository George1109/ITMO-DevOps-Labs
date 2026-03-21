#!/bin/bash
if [ $# -eq 0 ]; then
sh -c "/usr/games/fortune | /usr/games/cowsay"
else
/usr/games/cowsay "$@"
fi