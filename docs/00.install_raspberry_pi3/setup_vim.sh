#!/bin/bash
########################################
# vim install
########################################
sudo apt-get update
sudo apt-get install -y vim

########################################
# .vimrc
########################################

####################
# pi user
####################
cat <<EOF>> /home/pi/.vimrc
set clipboard=unnamed
EOF
chown pi:pi /home/pi/.vimrc

####################
# root user
####################
cat <<EOF>> /root/.vimrc
set clipboard=unnamed
EOF
