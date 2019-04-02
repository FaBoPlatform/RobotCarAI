#!/bin/bash

sudo localedef -i en_US -f UTF-8 en_US.UTF-8

########################################
# .bashrc (pi/root両方)
########################################
# sed
# escape characters \'$.*/[]^
# 1. Write the regex between single quotes.
# 2. \ -> \\
# 3. ' -> '\''
# 4. Put a backslash before $.*/[]^ and only those characters.

####################
# pi user
####################
#-    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w \$\[\033[00m\] '
#+    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\[\033[01;32m\]\h\[\033[00;00m\]:\[\033[01;35m\]\w\[\033[00m\]\$ '

#-    alias ls='ls --color=auto'
#+    alias ls='ls -asiF --color=auto'
sed -i 's/PS1='\''\${debian_chroot:+(\$debian_chroot)}\\\[\\033\[01;32m\\\]\\u@\\h\\\[\\033\[00m\\\]:\\\[\\033\[01;34m\\\]\\w \\\$\\\[\\033\[00m\\\] '\''/PS1='\''\${debian_chroot:+(\$debian_chroot)}\\\[\\033\[01;32m\\\]\\u@\\\[\\033\[01;32m\\\]\\h\\\[\\033\[00;00m\\\]:\\\[\\033\[01;35m\\\]\\w\\\[\\033\[00m\\\]\\\$ '\''/g' /home/pi/.bashrc
sed -i 's/alias ls='\''ls --color=auto'\''/alias ls='\''ls -asiF --color=auto'\''/g' /home/pi/.bashrc

cat <<EOF>> /home/pi/.bashrc

export LANG="en_US.UTF-8"
export LC_ALL=$LANG
EOF

####################
# root user
####################
cat <<EOF>> /root/.bashrc

PS1='${debian_chroot:+($debian_chroot)}\[\033[01;37m\]\u@\[\033[01;32m\]\h\[\033[00;00m\]:\[\033[01;35m\]\w\[\033[00m\]\$ '
alias ls='ls -asiF --color=auto'

export LANG="en_US.UTF-8"
export LC_ALL=$LANG
EOF
