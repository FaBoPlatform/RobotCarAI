########################################
# 起動時に自動実行する
########################################
# CPU版、SPIあり、I2Cあり(ケルベロス用はこれを使う)
docker run -itd --device /dev/spidev0.0:/dev/spidev0.0 --device /dev/i2c-1:/dev/i2c-1 -v /home/pi/notebooks:/notebooks -e "PASSWORD=gclue" -p 6006:6006 -p 8888:8888 naisy/fabo-jupyter-armhf /bin/bash -c "python /notebooks/github/RobotCarAI/demo/IRE2017/RobotCAR/start_button.py & jupyter notebook --allow-root --NotebookApp.iopub_data_rate_limit=10000000"


vi /etc/rc.local
docker start b11453216a0a # change for your container-id
