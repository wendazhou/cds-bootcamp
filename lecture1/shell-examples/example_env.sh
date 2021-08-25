#! /bin/bash

set -v # print command being executed


# Not exported, variable not inherited by program
MY_VAR=10
python print_env.py
echo Still works in shell: $MY_VAR


# exported, variable inherited by program
export MY_VAR
python print_env.py
unset MY_VAR

# can also specify environment variable during command
MY_VAR=10 python print_env.py




