#!/bin/bash
########################################
# dircolors
########################################
cp setup_dircolors_stretch.txt /home/pi/.dircolors
chown pi:pi /home/pi/.dircolors
chmod 600 /home/pi/.dircolors

sudo cp setup_dircolors_stretch.txt /root/.dircolors
sudo chmod 600 /root/.dircolors
