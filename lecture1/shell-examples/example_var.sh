#! /bin/bash

set -v

MY_VAR="my value"

echo ${MY_VAR} # print out the value of MY_VAR
echo "$HOME/$MY_VAR" # print out the value of $HOME/$MY_VAR
echo '$HOME/$MY_VAR' # print out exactly $HOME/MY_VAR

echo *.txt # echo the names of all files ending in .txt in this directory



