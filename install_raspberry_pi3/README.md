<a name='top'>

【タイトル】
# Raspberry Pi3のインストール方法
<hr>

【必要なもの】
* Raspberry Pi3
* 32 GB SDCARD
* HDMIモニタ
* USBキーボード

<hr>

【はじめに】<br>
Stretch特有の問題回避などがあるので、他のOS(Jessie 2017等)ではOS周りの設定方法が異なります。<br>
Dockerで用意しているRobotCarの環境には影響ないので、別のOSの場合はDocker部分だけ参考にしてください。<br>


<a name='0'>

【目次】
* [Stretch Liteインストール](#1)
* [raspi-config](#2)
  * SSH有効化
  * SPI有効化
  * I2C有効化
  * WiFi設定
* [RobotCar ソースコードダウンロード](#3)
* [OS環境設定](#4)
* [I2C Kernel/smbus修正](#5)
* [hostname変更](#6)
* [Dockerインストール](#7)
* [RobotCar Docker環境ダウンロード](#8)
* [Dockerコンテナ作成](#9)
* [自動起動設定](#10)

<hr>

<a name='1'>

## Stretch Liteインストール
Raspberry Pi3の2018年4月時点での最新OSはRaspbian Stretchなので、Stretch Lite 2018-04-18をベースとしたインストール方法を記載します。<br>

Raspbianの[リリースノート](http://downloads.raspberrypi.org/raspbian/release_notes.txt)でOS更新情報を確認してください。<br>
多くの変更があるバージョンはWiFi、I2C、SPI等の設定方法が変わっている可能性があります。最新のOSをベースに使う時はそれに合わせて設定してください。<br>
ベースOSのI2C、SPI有効化が正常に行えれば、Dockerで用意しているRobotCar環境は動作するかと思います。<br>

デスクトップ機能は不要なので、容量の少ないRASPBIAN STRETCH LITEをダウンロードします。<br>
ダウンロードURL:[https://www.raspberrypi.org/downloads/raspbian/](https://www.raspberrypi.org/downloads/raspbian/)<br>

ダウンロードしたイメージファイルをSDCARDに書き込みます。Windows PCならWin32DiskImagerで書き込む事が出来ます。<br>
RobotCarの環境に必要な容量が多いのでSDCARDは32GB以上を使うようにしてください。

Raspberry Piのデフォルトログインユーザは、<br>
> user: pi<br>
> password: raspberry<br>

になります。

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='2'>

## raspi-config
ここではSSH/SPI/I2C/WiFiを有効にします。<br>
rootユーザでraspi-configを実行し、各設定を行います。
```
sudo raspi-config
```

#### SSH有効化
Raspberry Pi3にネットワーク経由でログインするために必須となるSSHデーモンを有効化します。<br>
> Interfacing Options

項目にあるSSHを有効化します。


#### SPI有効化
RobotCarのボタン動作のためにSPIを有効化します。<br>
> Interfacing Options

項目にあるSPIを有効化します。


#### I2C有効化
RobotCarの距離センサー動作のためにI2Cを有効化します。<br>
> Interfacing Options

項目にあるI2Cを有効化します。<br>

Raspbian Stretch Liteにはkernelに問題があり、I2Cが正常に利用出来ません。このため、後ほどKernelを修正します。


#### WiFi設定
Raspberry Pi3をWiFiに接続します。<br>
> Network Options

項目から、WiFiの国別コードとしてJPを設定します。<br>
次に、WiFiのSSID、パスワードを入力してください。<br>
この設定は、<br>
> /etc/wpa_supplicant/wpa_supplicant.conf

ここに保存されます。


[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='3'>

## RobotCar ソースコードダウンロード
```
sudo apt-get update
sudo apt-get dist-upgrade -y
sudo apt-get update
sudo apt-get install -y git
mkdir -p /home/pi/notebooks/github/
cd /home/pi/notebooks/github
git clone https://github.com/FaBoPlatform/RobotCarAI
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='4'>

## OS環境設定
OSのアップデート、bashの設定、vim設定等を行います。動作には必須ではありませんが、少し見やすくなります。<br>
```
cd /home/pi/notebooks/github/RobotCarAI/install_raspberry_pi3
# 改行コードがCRLF(DOS)になっている事があるので、LF(UNIX)に変更する
find ./ -type f | xargs -n1 sed -i "s/\r//g"
chmod 755 *.sh
sudo ./setup_update.sh
sudo ./setup_dircolors.sh
sudo ./setup_bash.sh
sudo ./setup_vim.sh
sudo ./setup_ip_forward.sh
sudo ./setup_package.sh
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='5'>

## I2C Kernel/smbus修正
Raspbian Stretch Liteはraspi-configでI2Cを有効にしてもsmbusコード実行時にエラーが発生します。原因はKernelにあるようなので修正します。<br>

```
wget -O i2c1-bcm2708.dtbo https://drive.google.com/uc\?export=download\&id=0B_P-i4u-SLBXb3VlN0N5amVBb1k
sudo chmod 755 i2c1-bcm2708.dtbo
sudo chown root:root i2c1-bcm2708.dtbo
sudo mv i2c1-bcm2708.dtbo /boot/overlays/
sudo echo "dtoverlay=i2c1-bcm2708" >> /boot/config.txt
sudo reboot
# リブート後、Raspberry Pi3に再ログインしてから継続
sudo sh -c '/bin/echo Y > /sys/module/i2c_bcm2708/parameters/combined'
sudo reboot
```

参考： <br>
* [https://github.com/raspberrypi/firmware/issues/867](https://github.com/raspberrypi/firmware/issues/867)
* [https://www.raspberrypi.org/forums/viewtopic.php?t=192958](https://www.raspberrypi.org/forums/viewtopic.php?t=192958)
* [https://github.com/raspberrypi/firmware/issues/828](https://github.com/raspberrypi/firmware/issues/828)

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='6'>

## hostname変更
Raspberry Pi3をたくさん使っていると、どれを使っているのかわからなくなることがあるので、ホスト名を変更します。<br>
これは動作には必須ではありません。<br>

/etc/hostnameを書き換えます。
```
sudo vi /etc/hostname
```
>RobotCar  

/etc/hostsを書き換えます。
```
sudo vi /etc/hosts
```
>127.0.0.1	localhost  
>::1		localhost ip6-localhost ip6-loopback  
>ff02::1		ip6-allnodes  
>ff02::2		ip6-allrouters  
>  
>127.0.1.1	RobotCar  

再起動します。
```
sudo reboot
```

再ログイン後、ホスト名を確認します。
```
hostnamectl 
```
>    Static hostname: RobotCar  
>         Icon name: computer  
>        Machine ID: 86e73d2e6bbb41bf89537d5bcf63f676  
>           Boot ID: 598d925b7ba3449dbc0c614cfb761b37  
>  Operating System: Raspbian GNU/Linux 9 (stretch)  
>            Kernel: Linux 4.14.30-v7+  
>      Architecture: arm  


[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='7'>

## Dockerインストール
```
sudo apt-get install -y docker.io
sudo reboot
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='8'>

## RobotCar Docker環境ダウンロード
```
sudo docker pull naisy/fabo-jupyter-armhf
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='9'>

## Dockerコンテナ作成
* CPU版、SPIあり、I2Cあり(level1はこれを使う)
```
sudo docker run -itd --device /dev/spidev0.0:/dev/spidev0.0 --device /dev/i2c-1:/dev/i2c-1 -v /home/pi/notebooks:/notebooks -e "PASSWORD=gclue" -p 6006:6006 -p 8888:8888 naisy/fabo-jupyter-armhf /bin/bash -c "jupyter notebook --allow-root --NotebookApp.iopub_data_rate_limit=10000000"
```

* CPU版、SPIあり、I2Cあり、level1_demo走行用(start_button.pyを実行するコンテナを作成)
```
sudo docker run -itd --device /dev/spidev0.0:/dev/spidev0.0 --device /dev/i2c-1:/dev/i2c-1 -v /home/pi/notebooks:/notebooks -e "PASSWORD=gclue" -p 6006:6006 -p 8888:8888 naisy/fabo-jupyter-armhf /bin/bash -c "python /notebooks/github/RobotCarAI/level1_demo/start_button.py & jupyter notebook --allow-root --NotebookApp.iopub_data_rate_limit=10000000"
```

* CPU版、開発用、SPIあり、USBカメラ付き、I2Cあり、TCP通信ポートあり(level2,3はこれを使う)
```
sudo docker run -itd --device /dev/video0:/dev/video0 --device /dev/spidev0.0:/dev/spidev0.0 --device /dev/i2c-1:/dev/i2c-1 -v /home/pi/notebooks:/notebooks -e "PASSWORD=gclue" -p 6006:6006 -p 8888:8888 -p 8091:8091 naisy/fabo-jupyter-armhf /bin/bash -c "jupyter notebook --allow-root --NotebookApp.iopub_data_rate_limit=10000000"
```


[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='10'>

## 自動起動設定
Raspberry Pi3が起動したら、RobotCarを自動起動するように設定します。<br>
/etc/rc.localを編集し、docker start container_idを追加します。<br>
Dockerコンテナのうち、start_button.pyを実行しているコンテナを指定することでRobotCarが自動起動になります。<br>

```
sudo vi /etc/rc.local
```
>...  
> docker start 16f3bd352ebd
> 
> exit 0


[<ページTOP>](#top)　[<目次>](#0)

