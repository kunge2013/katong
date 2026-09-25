#!/bin/bash
# 创建 conda 环境并安装依赖

echo "Creating conda environment: cinegacha"
conda env create -f environment.yml

echo "Activating environment..."
echo "Run: conda activate cinegacha"
