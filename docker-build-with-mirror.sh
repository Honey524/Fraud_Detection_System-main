#!/bin/bash
# Use PyPI mirror for faster/more reliable downloads in China/Asia

export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# Alternative mirrors (uncomment if needed):
# export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
# export PIP_INDEX_URL=https://pypi.douban.com/simple/

echo "Using PyPI mirror: $PIP_INDEX_URL"

# Build with mirror
cd /home/honey/Downloads/Fraud_Detection_System-main
sudo -E docker compose build
