#!/bin/bash
while true
do
    python app.py -p $1
    sleep 1  # 等待1秒后重启
done
