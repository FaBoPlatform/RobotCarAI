########################################
# インストールスクリプト実行
########################################
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

$SCRIPT_DIR/install_balancap_ssd-tensorflow.sh
$SCRIPT_DIR/setup_bugfix.sh
$SCRIPT_DIR/copy_to.sh
$SCRIPT_DIR/patch_to.sh
