########################################
# LabelImg インストール
########################################
mkdir ~/github
cd ~/github
git clone https://github.com/tzutalin/labelImg

cd labelImg
sudo apt-get install -y pyqt4-dev-tools
sudo apt-get install -y python-pip
sudo pip install --upgrade pip
sudo pip install lxml
make qt4py2
./labelImg.py

