########################################
# 再起動時、start_button.py起動
########################################
cat <<EOF> /etc/init.d/ire2017arm
#!/bin/sh
### BEGIN INIT INFO
# Provides:         ire2017arm
# Required-Start:   $remote_fs $syslog
# Required-Stop:    $remote_fs $syslog
# Default-Start:    2 3 4 5
# Default-Stop:	    0 1 6
# Short-Description: IRE2017 demo arm launcher
### END INIT INFO

# Launch IRE2017 demo arm
/usr/bin/python /home/ubuntu/notebooks/RobotCarAI/demo/IRE2017/RobotARM/start_button.py
EOF

chmod 755 /etc/init.d/ire2017arm
update-rc.d ire2017arm defaults

# uninstall
# update-rc.d ire2017arm remove