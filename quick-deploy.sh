#!/bin/bash

# 企业微信 Webhook 服务器快速部署脚本
# 支持两种部署方式：Docker 镜像部署 和 服务器直接部署

set -e

echo "🚀 企业微信 Webhook 服务器快速部署"
echo "====================================="
echo ""

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未安装 Docker Compose"
    exit 1
fi

# 选择安装目录
echo "📂 设置安装目录"
echo "默认安装目录: /opt/wecom-webhook"
echo ""
read -p "请输入安装目录（直接回车使用默认）: " CUSTOM_DIR
echo ""

if [ -z "$CUSTOM_DIR" ]; then
    BASE_DIR="/opt/wecom-webhook"
else
    BASE_DIR="$CUSTOM_DIR"
fi

echo "✅ 安装目录: $BASE_DIR"
echo ""

# 检查目录权限
PARENT_DIR=$(dirname "$BASE_DIR")
if [ ! -w "$PARENT_DIR" ] 2>/dev/null; then
    echo "⚠️  警告: $PARENT_DIR 需要管理员权限"
    echo "请使用 sudo 运行此脚本，或选择其他目录"
    echo ""
    read -p "是否使用 sudo 继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
    echo ""
    # 使用 sudo 重新运行脚本
    exec sudo bash "$0"
fi

# 选择部署方式
echo "请选择部署方式："
echo "1) Docker 镜像部署（推荐，无需下载项目代码）"
echo "2) 服务器直接部署（需要克隆项目，适合自定义代码）"
echo ""
read -p "请输入选项 (1 或 2): " -n 1 -r DEPLOY_MODE
echo ""
echo ""

if [[ "$DEPLOY_MODE" == "1" ]]; then
    # ==========================================
    # 方式一：Docker 镜像部署
    # ==========================================
    echo "📦 方式一：使用预构建 Docker 镜像部署"
    echo "========================================="
    echo ""
    
    if [ -d "$BASE_DIR" ]; then
        echo "⚠️  目录 $BASE_DIR 已存在"
        read -p "是否覆盖? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
        rm -rf "$BASE_DIR"
    fi
    
    mkdir -p "$BASE_DIR"
    cd "$BASE_DIR"
    
    echo "📥 下载配置文件..."
    
    # 下载 .env.example 和 docker-compose.yml
    if command -v curl &> /dev/null; then
        curl -sS -O https://raw.githubusercontent.com/ui-beam-9/docker-images-sync-huaweicloud-swr/main/wecom-webhook/.env.example
        curl -sS -O https://raw.githubusercontent.com/ui-beam-9/docker-images-sync-huaweicloud-swr/main/wecom-webhook/docker-compose.yml
    elif command -v wget &> /dev/null; then
        wget -q https://raw.githubusercontent.com/ui-beam-9/docker-images-sync-huaweicloud-swr/main/wecom-webhook/.env.example
        wget -q https://raw.githubusercontent.com/ui-beam-9/docker-images-sync-huaweicloud-swr/main/wecom-webhook/docker-compose.yml
    else
        echo "❌ 错误: 未安装 curl 或 wget"
        exit 1
    fi
    
    # 重命名 .env.example
    mv .env.example .env
    
    echo "✅ 配置文件下载完成！"
    echo ""
    echo "📝 下一步操作："
    echo "1. 编辑 .env 文件，填写你的配置"
    echo "   cd $BASE_DIR"
    echo "   nano .env"
    echo ""
    echo "2. 启动服务（会自动拉取预构建镜像）"
    echo "   docker-compose up -d"
    echo ""
    echo "3. 查看日志"
    echo "   docker-compose logs -f"
    echo ""
    
elif [[ "$DEPLOY_MODE" == "2" ]]; then
    # ==========================================
    # 方式二：服务器直接部署
    # ==========================================
    echo "🔧 方式二：服务器直接部署"
    echo "========================================="
    echo ""
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        echo "❌ 错误: 未安装 Git"
        exit 1
    fi
    
    if [ -d "$BASE_DIR" ]; then
        echo "⚠️  目录 $BASE_DIR 已存在"
        read -p "是否覆盖? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
        rm -rf "$BASE_DIR"
    fi
    
    echo "📥 克隆项目..."
    # 使用临时目录克隆
    TEMP_DIR=$(mktemp -d)
    git clone https://github.com/ui-beam-9/docker-images-sync-huaweicloud-swr.git "$TEMP_DIR"
    
    # 复制 wecom-webhook 目录到目标位置
    mkdir -p "$(dirname "$BASE_DIR")"
    cp -r "$TEMP_DIR/wecom-webhook" "$BASE_DIR"
    
    # 清理临时目录
    rm -rf "$TEMP_DIR"
    
    cd "$BASE_DIR"
    
    echo "📁 创建配置文件..."
    cp .env.example .env
    
    echo "✅ 项目克隆完成！"
    echo ""
    echo "📝 下一步操作："
    echo "1. 编辑 .env 文件，填写你的配置"
    echo "   cd $BASE_DIR"
    echo "   nano .env"
    echo ""
    echo "2. 如需本地构建，编辑 docker-compose.yml"
    echo "   nano docker-compose.yml"
    echo "   注释: image: swr.cn-east-3.myhuaweicloud.com/ui_beam-images/wecom-webhook-server:latest"
    echo "   取消注释: # build: ."
    echo ""
    echo "3. 启动服务"
    echo "   docker-compose up -d"
    echo ""
    echo "4. 查看日志"
    echo "   docker-compose logs -f"
    echo ""
    
else
    echo "❌ 无效的选项，请输入 1 或 2"
    exit 1
fi

echo "🎉 部署准备完成！"
echo ""
