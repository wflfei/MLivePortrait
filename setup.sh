#!/bin/bash

# 由于runpod容器无法使用systemctl，改用loop_start.sh启动

# 获取当前目录
CURRENT_DIR=$(pwd)

# 获取conda路径
CONDA_PATH="/workspace/miniconda/bin/conda"
if [ -z "$CONDA_PATH" ]; then
    echo "Error: Conda not found in PATH. Please make sure Conda is installed and in your PATH."
    exit 1
fi
CONDA_BIN_DIR=$(dirname "$CONDA_PATH")

# 获取当前用户和组
CURRENT_USER=$(whoami)
CURRENT_GROUP=$(id -gn)

# 获取当前激活的Conda环境名称
CONDA_ENV=$("$CONDA_PATH" info --envs | grep '*' | awk '{print $1}')

# 创建启动脚本
cat > "$CURRENT_DIR/startup.sh" << EOL
#!/bin/bash
source $CONDA_BIN_DIR/activate $CONDA_ENV
python $CURRENT_DIR/app.py
EOL

chmod +x "$CURRENT_DIR/startup.sh"

# 创建service文件
SERVICE_NAME="FaceWonder"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

if [ -e $SERVICE_FILE ]; then
    echo "FaceWonder.service file exists, deleting now!"
    systemctl disable FaceWonder.service
    rm -f $SERVICE_FILE
fi

tee "$SERVICE_FILE" > /dev/null << EOL
[Unit]
Description=$SERVICE_NAME Python Service
After=network.target

[Service]
ExecStart=$CURRENT_DIR/startup.sh
Restart=always
User=$CURRENT_USER
Group=$CURRENT_GROUP
Environment=PATH=$CONDA_BIN_DIR:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
WorkingDirectory=$CURRENT_DIR

[Install]
WantedBy=multi-user.target
EOL

echo "Service file created at $SERVICE_FILE"

# 重新加载systemd配置
systemctl daemon-reload

# 启用服务
systemctl enable "$SERVICE_NAME"

echo "Service $SERVICE_NAME has been created and enabled."
echo "You can start it with: sudo systemctl start $SERVICE_NAME"
echo "You can check its status with: sudo systemctl status $SERVICE_NAME"
