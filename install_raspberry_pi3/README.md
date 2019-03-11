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
古いStretchにはI2Cに問題があります。2018-04-18や2018-06-27ではカーネル修正が必要になります。問題がある場合はトラブルシューティングを参照してください。<br>
Dockerで用意しているRobotCarの環境には影響ないので、別のOSの場合はDocker部分だけ参考にしてください。<br>


<a name='0'>

【目次】
* [Stretch Liteインストール](#1)
* [raspi-config](#2)
  * SSH有効化
  * SPI有効化
  * I2C有効化
  * WiFi設定
  * ホスト名変更
  * キーボードレイアウト変更
  * TimeZone変更
* [RobotCar ソースコードダウンロード](#3)
* [OS環境設定](#4)
* [RobotCar Docker環境ダウンロード](#5)
* [Dockerコンテナ作成](#6)
* [自動起動設定](#7)
* [トラブルシューティング](#tips)
  * [I2C Kernel/smbus修正]
  * [ホスト名変更]

<hr>

<a name='1'>

## Stretch Liteインストール
Raspberry Pi3の2019年3月時点での最新OSはRaspbian Stretchなので、Stretch Lite 2018-11-13をベースとしたインストール方法を記載します。<br>

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

#### WiFi設定
Raspberry Pi3をWiFiに接続します。<br>
> Network Options

項目から、WiFiの国別コードとしてJPを設定します。<br>
次に、WiFiのSSID、パスワードを入力してください。<br>
この設定は、<br>
> /etc/wpa_supplicant/wpa_supplicant.conf

ここに保存されます。

パスワードを暗号化する場合は、以下のコマンド実行で表示されるpsk=xxxxxxxxの部分でpskを書き換えてください。
```
sudo wpa_passphrase 'SSID' 'PASSWORD'
```

* 2019/03/07 追記
wpasupplicantはシステムのデフォルトセキュリティ設定を見ていません。<br>
システムの現在の設定はTLS1.2とsecurity level 2です。<br>
TLS1.2未満のネットワークに接続しないことを確信出来る場合は以下の設定を追加してください。<br>
ルータ機器が古い場合は接続出来なくなる恐れがあるため、ここは設定しないでおいてください。<br>
```
tls_disable_tlsv1_0=1
tls_disable_tlsv1_1=1
opensslciphers=DEFAULT@SECLEVEL=2
```

#### ホスト名変更
Raspberry Pi3をたくさん使っていると、どれを使っているのかわからなくなることがあるので、ホスト名を変更します。<br>
これは動作には必須ではありません。<br>

#### キーボードレイアウト変更
OSのデフォルトでは英語キーボードになっているため、日本語キーボードを使う場合はレイアウトをOADG 109Aに変更した方が使いやすくなります。<br>

#### TimeZone変更
OSのデフォルトではUTCになっているため、タイムゾーンをAsia/Tokyoに変更した方が時間がわかりやすくなります。<br>

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
OSのアップデート、bashの設定、vim設定等を行います。動作には必須ではありませんが、ログインしなおすと少し見やすくなります。<br>
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
sudo ./setup_docker-ce.sh
sudo reboot
```
dockerをインストールすると再起動が必要になります。<br>
dockerインストール直後は以下のようなエラーが表示されますが、スルーして再起動してください。
```
Errors were encountered while processing:
 docker-ce
E: Sub-process /usr/bin/dpkg returned an error code (1)
```
再起動後、dockerが利用可能かどうかを確認します。
```
sudo docker ps -a
```
まだdockerコンテナを作成していないため、dockerが利用可能であれば以下のような出力になります。
```
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
```


[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='5'>

## RobotCar Docker環境ダウンロード
[Docker Hub](https://cloud.docker.com/repository/docker/naisy/fabo-jupyter-armhf)
```
sudo docker pull naisy/fabo-jupyter-armhf
```

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='6'>

## Dockerコンテナ作成

### docker-ceの場合
--network=hostの指定が可能になり、利用するポート番号指定を簡略化できます。<br>

* Jupyterのみ起動
```
sudo docker run \
    -itd \
    --privileged \
    --network=host \
    -v /home/pi/notebooks:/notebooks \
    -e "PASSWORD=robotcar" \
naisy/fabo-jupyter-armhf /bin/bash -c "jupyter notebook --allow-root"
```

* level1_car走行用(start_button.pyを実行するコンテナを作成)
```
sudo docker run \
    -itd \
    --privileged \
    --network=host \
    -v /home/pi/notebooks:/notebooks \
    -e "PASSWORD=robotcar" \
naisy/fabo-jupyter-armhf /bin/bash -c "python /notebooks/github/RobotCarAI/level1_car/start_button.py & jupyter notebook --allow-root"
```


### docker.ioの場合(古いDockerバージョン)
--networkオプションが使えないため、利用するポート番号を指定する必要があります。<br>

* Jupyterのみ起動
```
sudo docker run \
    -itd \
    --privileged \
    -p 6006:6006 -p 8888:8888 -p 8091:8091 \
    -v /home/pi/notebooks:/notebooks \
    -e "PASSWORD=robotcar" \
naisy/fabo-jupyter-armhf /bin/bash -c "jupyter notebook --allow-root"
```

* level1_car走行用(start_button.pyを実行するコンテナを作成)
```
sudo docker run \
    -itd \
    --privileged \
    -p 6006:6006 -p 8888:8888 -p 8091:8091 \
    -v /home/pi/notebooks:/notebooks \
    -e "PASSWORD=robotcar" \
naisy/fabo-jupyter-armhf /bin/bash -c "python /notebooks/github/RobotCarAI/level1_car/start_button.py & jupyter notebook --allow-root"
```

jupyterのプロセスをkillするとdockerコンテナは終了してしまいますが、start_button.pyのプロセスをkillしても、dockerコンテナは終了しません。<br>
このため、自動起動のコンテナにログインしてコードを実行する場合は、start_button.pyのプロセスをkillするとJupyterのみ起動したコンテナと同じように利用出来ます。<br>
docker runで指定したコンテナの設定が変わる訳では無いため、コンテナを再起動するとstart_button.pyとjupyterのプロセスが起動した状態になります。<br>

[<ページTOP>](#top)　[<目次>](#0)
<hr>

<a name='7'>

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

<a name='tips'>

## トラブルシューティング

#### I2C Kernel/smbus修正
* 2019/03/07 追記
2018-11-13-raspbian-stretch-liteでは問題が解決しているのでここは不要です。<br>

Raspbian Stretch Liteの古いOSではraspi-configでI2Cを有効にしてもsmbusコード実行時にエラーが発生します。原因はKernelにあるようなので修正します。<br>

```
wget -O i2c1-bcm2708.dtbo https://drive.google.com/uc\?export=download\&id=0B_P-i4u-SLBXb3VlN0N5amVBb1k
sudo chmod 755 i2c1-bcm2708.dtbo
sudo chown root:root i2c1-bcm2708.dtbo
sudo mv i2c1-bcm2708.dtbo /boot/overlays/
sudo sh -c 'echo "dtoverlay=i2c1-bcm2708" >> /boot/config.txt'
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

#### hostname変更
`raspi-config`コマンドを使わずに設定ファイルを直接修正してホスト名を変更する場合、<br>
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

