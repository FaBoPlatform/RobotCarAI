#!/bin/bash

########################################
# Docker Install
########################################
#apt-cache search docker
#で見つかるdocker.ioは古くて、オプションに--network=hostを利用出来ないため、新しいdocker-ceをインストールします。

curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
apt-key fingerprint 0EBFCD88
echo "deb [arch=armhf] https://download.docker.com/linux/debian \
     $(lsb_release -cs) stable" | \
     tee /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install docker-ce
