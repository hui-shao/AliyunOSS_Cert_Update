#!/bin/bash

# 调用 Python 脚本
python3 /path/to/main.py

# 检查 Python 脚本的执行状态
if [ $? -eq 0 ]; then
    echo "证书已更新: $(date)" >> /var/log/log_aliyun_update.txt
else
    echo "证书更新失败: $(date)" >> /var/log/log_aliyun_update.txt
fi
