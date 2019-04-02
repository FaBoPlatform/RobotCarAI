#!/bin/bash
########################################
# IPv4 Forwarding
########################################
# sed
# escape characters \'$.*/[]^
# 1. Write the regex between single quotes.
# 2. \ -> \\
# 3. ' -> '\''
# 4. Put a backslash before $.*/[]^ and only those characters.

#-#net.ipv4.ip_forward=1
#+net.ipv4.ip_forward=1
sudo sed -i 's/#net\.ipv4\.ip_forward=1/net.ipv4.ip_forward=1/g' /etc/sysctl.conf

# IP転送を有効にする
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"
# or
# sudo sysctl -w net.ipv4.ip_forward=1

#IP転送が有効になっているかどうか確認する
/sbin/sysctl net.ipv4.ip_forward
