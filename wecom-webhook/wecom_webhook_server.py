#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
企业微信消息接收服务器
接收企业微信应用消息，自动在 GitHub 创建镜像同步 Issues
"""

import os
import hashlib
import json
import time
import logging
from flask import Flask, request, jsonify
import requests
from WXBizMsgCrypt3 import WXBizMsgCrypt
import xmltodict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 从环境变量读取配置
WECOM_TOKEN = os.environ.get('WECOM_TOKEN', '')
WECOM_ENCODING_AES_KEY = os.environ.get('WECOM_ENCODING_AES_KEY', '')
WECOM_CORP_ID = os.environ.get('WECOM_CORP_ID', '')
WECOM_AGENT_ID = os.environ.get('WECOM_AGENT_ID', '')
WECOM_SECRET = os.environ.get('WECOM_SECRET', '')
WECOM_API_BASE = os.environ.get('WECOM_API_BASE', 'https://qyapi.weixin.qq.com')  # 企业微信 API 地址
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
GITHUB_REPO = os.environ.get('GITHUB_REPO', '')  # 格式: owner/repo
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')  # Webhook 验证密钥
HUAWEI_SWR_REGION = os.environ.get('HUAWEI_SWR_REGION', 'cn-east-3')  # 华为云 SWR 区域
HUAWEI_SWR_NAMESPACE = os.environ.get('HUAWEI_SWR_NAMESPACE', 'ui_beam-images')  # 华为云 SWR 命名空间

# 验证必需的环境变量
required_vars = [WECOM_TOKEN, WECOM_ENCODING_AES_KEY, WECOM_CORP_ID, WECOM_AGENT_ID, WECOM_SECRET, GITHUB_TOKEN, GITHUB_REPO, WEBHOOK_SECRET]
if not all(required_vars):
    logger.error("缺少必需的环境变量！")
    logger.error(f"WECOM_TOKEN: {'已设置' if WECOM_TOKEN else '未设置'}")
    logger.error(f"WECOM_ENCODING_AES_KEY: {'已设置' if WECOM_ENCODING_AES_KEY else '未设置'}")
    logger.error(f"WECOM_CORP_ID: {'已设置' if WECOM_CORP_ID else '未设置'}")
    logger.error(f"WECOM_AGENT_ID: {'已设置' if WECOM_AGENT_ID else '未设置'}")
    logger.error(f"WECOM_SECRET: {'已设置' if WECOM_SECRET else '未设置'}")
    logger.error(f"GITHUB_TOKEN: {'已设置' if GITHUB_TOKEN else '未设置'}")
    logger.error(f"GITHUB_REPO: {'已设置' if GITHUB_REPO else '未设置'}")
    logger.error(f"WEBHOOK_SECRET: {'已设置' if WEBHOOK_SECRET else '未设置'}")

# 初始化消息加解密类
wxcpt = WXBizMsgCrypt(WECOM_TOKEN, WECOM_ENCODING_AES_KEY, WECOM_CORP_ID)

# Access Token 缓存
access_token_cache = {
    'token': None,
    'expires_at': 0
}


def get_access_token():
    """获取企业微信 Access Token"""
    try:
        # 检查缓存
        if access_token_cache['token'] and time.time() < access_token_cache['expires_at']:
            return access_token_cache['token']
        
        # 获取新 token
        url = f"{WECOM_API_BASE}/cgi-bin/gettoken"
        params = {
            'corpid': WECOM_CORP_ID,
            'corpsecret': WECOM_SECRET
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('errcode') == 0:
            token = data.get('access_token')
            expires_in = data.get('expires_in', 7200)
            
            # 缓存 token（提前 5 分钟过期）
            access_token_cache['token'] = token
            access_token_cache['expires_at'] = time.time() + expires_in - 300
            
            logger.info("✅ 成功获取 Access Token")
            return token
        else:
            logger.error(f"❌ 获取 Access Token 失败: {data.get('errmsg')}")
            return None
            
    except Exception as e:
        logger.error(f"❌ 获取 Access Token 异常: {str(e)}")
        return None


def send_wecom_message(user_id, content):
    """发送企业微信消息"""
    try:
        access_token = get_access_token()
        if not access_token:
            logger.error("❌ 无法获取 Access Token，消息发送失败")
            return False
        
        url = f"{WECOM_API_BASE}/cgi-bin/message/send?access_token={access_token}"
        
        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": int(WECOM_AGENT_ID),
            "text": {
                "content": content
            },
            "safe": 0
        }
        
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        if result.get('errcode') == 0:
            logger.info(f"✅ 成功发送企业微信消息给用户: {user_id}")
            return True
        else:
            logger.error(f"❌ 发送企业微信消息失败: {result.get('errmsg')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 发送企业微信消息异常: {str(e)}")
        return False


def verify_signature(signature, timestamp, nonce, echo_str):
    """验证企业微信签名"""
    try:
        ret, reply_echo_str = wxcpt.VerifyURL(signature, timestamp, nonce, echo_str)
        if ret == 0:
            logger.info("✅ URL 验证成功")
            return reply_echo_str.decode('utf-8')
        else:
            logger.error(f"❌ URL 验证失败，错误码: {ret}")
            return None
    except Exception as e:
        logger.error(f"❌ 验证签名异常: {str(e)}")
        return None


def decrypt_message(msg_signature, timestamp, nonce, post_data):
    """解密企业微信消息"""
    try:
        ret, xml_content = wxcpt.DecryptMsg(post_data, msg_signature, timestamp, nonce)
        if ret == 0:
            logger.info("✅ 消息解密成功")
            return xml_content.decode('utf-8')
        else:
            logger.error(f"❌ 消息解密失败，错误码: {ret}")
            return None
    except Exception as e:
        logger.error(f"❌ 解密消息异常: {str(e)}")
        return None


def parse_message(xml_content):
    """解析 XML 消息"""
    try:
        msg_dict = xmltodict.parse(xml_content)
        return msg_dict.get('xml', {})
    except Exception as e:
        logger.error(f"❌ 解析消息异常: {str(e)}")
        return None


def create_github_issue(image_name, user_id=None):
    """在 GitHub 创建 Issue，并发送企业微信通知"""
    try:
        # 清理镜像名称，去除空格
        image_name = image_name.strip()
        
        # 验证镜像名称格式
        if not image_name:
            logger.error("❌ 镜像名称为空")
            if user_id:
                send_wecom_message(user_id, "❌ 镜像同步失败：镜像名称为空")
            return False
        
        logger.info(f"准备创建 GitHub Issue: {image_name}")
        
        # GitHub API 地址
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
        
        # 请求头
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json"
        }
        
        # Issue 数据（将用户ID保存到body中，用于后续通知）
        issue_data = {
            "title": image_name,
            "labels": ["sync image"],
            "body": f"📦 来自企业微信的镜像同步请求\n\n镜像名称: `{image_name}`\n提交时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n<!-- wecom_user_id: {user_id} -->"
        }
        
        # 发送请求
        response = requests.post(api_url, headers=headers, json=issue_data, timeout=10)
        
        if response.status_code == 201:
            issue_data = response.json()
            issue_url = issue_data.get('html_url', '')
            issue_number = issue_data.get('number', '')
            logger.info(f"✅ Issue 创建成功: {issue_url}")
            
            # 发送企业微信通知
            if user_id:
                notification = f"✅ 镜像同步任务已创建\n\n" \
                             f"镜像名称: {image_name}\n" \
                             f"Issue 编号: #{issue_number}\n" \
                             f"状态: 等待同步\n\n" \
                             f"查看详情: {issue_url}"
                send_wecom_message(user_id, notification)
            
            return True
        else:
            logger.error(f"❌ Issue 创建失败: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            
            # 发送失败通知
            if user_id:
                send_wecom_message(user_id, f"❌ 镜像同步失败\n\n镜像名称: {image_name}\n原因: GitHub Issue 创建失败")
            
            return False
            
    except Exception as e:
        logger.error(f"❌ 创建 Issue 异常: {str(e)}")
        
        # 发送异常通知
        if user_id:
            send_wecom_message(user_id, f"❌ 镜像同步失败\n\n镜像名称: {image_name}\n原因: 系统异常")
        
        return False


def extract_image_name(content):
    """从消息内容中提取镜像名称"""
    # 去除空格和换行
    content = content.strip()
    
    # 支持的格式：
    # 1. library/busybox:latest
    # 2. docker.io/library/busybox:latest
    # 3. gcr.io/google-containers/pause:3.9
    
    # 简单验证：应该包含冒号（标签分隔符）
    if ':' not in content:
        logger.warning(f"⚠️ 消息内容可能不是有效的镜像名称: {content}")
    
    return content


def get_user_id_from_issue(issue_number):
    """从 Issue body 中提取用户 ID"""
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{issue_number}"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            issue_data = response.json()
            body = issue_data.get('body', '')
            
            # 从 body 中提取用户 ID
            import re
            match = re.search(r'<!-- wecom_user_id: (\S+) -->', body)
            if match:
                user_id = match.group(1)
                logger.info(f"从 Issue #{issue_number} 提取到用户 ID: {user_id}")
                return user_id
            else:
                logger.warning(f"Issue #{issue_number} 中未找到用户 ID")
                return None
        else:
            logger.error(f"获取 Issue 失败: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"提取用户 ID 异常: {str(e)}")
        return None


@app.route('/wecom/callback', methods=['GET', 'POST'])
def wecom_callback():
    """企业微信回调接口"""
    try:
        if request.method == 'GET':
            # URL 验证
            msg_signature = request.args.get('msg_signature', '')
            timestamp = request.args.get('timestamp', '')
            nonce = request.args.get('nonce', '')
            echostr = request.args.get('echostr', '')
            
            logger.info(f"收到 URL 验证请求: timestamp={timestamp}, nonce={nonce}")
            
            reply_echostr = verify_signature(msg_signature, timestamp, nonce, echostr)
            if reply_echostr:
                return reply_echostr
            else:
                return "验证失败", 403
        
        elif request.method == 'POST':
            # 接收消息
            msg_signature = request.args.get('msg_signature', '')
            timestamp = request.args.get('timestamp', '')
            nonce = request.args.get('nonce', '')
            
            logger.info(f"收到消息推送: timestamp={timestamp}, nonce={nonce}")
            
            # 解密消息
            post_data = request.data
            xml_content = decrypt_message(msg_signature, timestamp, nonce, post_data)
            
            if not xml_content:
                return "解密失败", 403
            
            # 解析消息
            msg = parse_message(xml_content)
            if not msg:
                return "解析失败", 400
            
            logger.info(f"消息内容: {json.dumps(msg, ensure_ascii=False, indent=2)}")
            
            # 获取消息类型和内容
            msg_type = msg.get('MsgType', '')
            
            if msg_type == 'text':
                # 文本消息
                content = msg.get('Content', '')
                from_user = msg.get('FromUserName', '')
                
                logger.info(f"收到文本消息 from {from_user}: {content}")
                
                # 提取镜像名称
                image_name = extract_image_name(content)
                
                # 创建 GitHub Issue 并发送企业微信通知
                success = create_github_issue(image_name, user_id=from_user)
                
                if success:
                    logger.info(f"✅ 成功处理镜像同步请求: {image_name}")
                else:
                    logger.error(f"❌ 处理镜像同步请求失败: {image_name}")
                
                return "success"
            
            elif msg_type == 'event':
                # 事件消息
                event = msg.get('Event', '')
                logger.info(f"收到事件: {event}")
                return "success"
            
            else:
                logger.warning(f"⚠️ 不支持的消息类型: {msg_type}")
                return "success"
        
    except Exception as e:
        logger.error(f"❌ 处理回调异常: {str(e)}", exc_info=True)
        return "服务器错误", 500


@app.route('/api/notify', methods=['POST'])
def notify_status():
    """
    接收 GitHub Actions 的状态通知并转发到企业微信
    请求格式：
    {
        "secret": "webhook_secret",
        "issue_number": 123,
        "status": "syncing|success|failure",
        "image_name": "docker.io/library/nginx:latest",
        "target_image": "swr.cn-east-3.myhuaweicloud.com/ui_beam-images/nginx:latest",
        "error_message": "错误信息（可选）",
        "logs_url": "日志URL（可选）"
    }
    """
    try:
        # 验证 secret
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request"}), 400
        
        secret = data.get('secret', '')
        if secret != WEBHOOK_SECRET:
            logger.warning(f"⚠️ 无效的 webhook secret")
            return jsonify({"error": "Invalid secret"}), 403
        
        issue_number = data.get('issue_number')
        status = data.get('status')
        image_name = data.get('image_name', '')
        target_image = data.get('target_image', '')
        error_message = data.get('error_message', '')
        logs_url = data.get('logs_url', '')
        
        if not issue_number or not status:
            return jsonify({"error": "Missing required fields"}), 400
        
        # 从 Issue 中获取用户 ID
        user_id = get_user_id_from_issue(issue_number)
        if not user_id:
            logger.warning(f"⚠️ 无法获取 Issue #{issue_number} 的用户 ID，跳过通知")
            return jsonify({"error": "User ID not found"}), 404
        
        # 根据状态发送不同的通知
        if status == 'syncing':
            # 同步中
            message = f"🔄 镜像正在同步中\n\n" \
                     f"镜像: {image_name}\n" \
                     f"Issue: #{issue_number}\n" \
                     f"进度: 正在处理..."
        
        elif status == 'success':
            # 同步成功
            message = f"✅ 镜像同步成功\n\n" \
                     f"镜像: {image_name}\n" \
                     f"Issue: #{issue_number}\n\n" \
                     f"📦 快捷命令：\n" \
                     f"docker pull {target_image}\n\n" \
                     f"查看详情: https://github.com/{GITHUB_REPO}/issues/{issue_number}"
        
        elif status == 'failure':
            # 同步失败
            message = f"❌ 镜像同步失败\n\n" \
                     f"镜像: {image_name}\n" \
                     f"Issue: #{issue_number}\n\n" \
                     f"失败原因: {error_message or '未知错误'}\n\n"
            
            if logs_url:
                message += f"查看日志: {logs_url}"
        
        else:
            return jsonify({"error": "Invalid status"}), 400
        
        # 发送企业微信通知
        success = send_wecom_message(user_id, message)
        
        if success:
            logger.info(f"✅ 成功发送状态通知: {status} for Issue #{issue_number}")
            return jsonify({"success": True, "message": "Notification sent"}), 200
        else:
            logger.error(f"❌ 发送状态通知失败: {status} for Issue #{issue_number}")
            return jsonify({"success": False, "message": "Failed to send notification"}), 500
    
    except Exception as e:
        logger.error(f"❌ 处理通知请求异常: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "wecom-webhook-server",
        "timestamp": time.time()
    })


@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        "service": "企业微信消息接收服务器",
        "description": "接收企业微信应用消息，自动在 GitHub 创建镜像同步 Issues",
        "endpoints": {
            "/wecom/callback": "企业微信回调接口（GET: URL验证, POST: 消息接收）",
            "/health": "健康检查接口"
        },
        "status": "running"
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 服务器启动在端口 {port}")
    logger.info(f"📋 GitHub 仓库: {GITHUB_REPO}")
    app.run(host='0.0.0.0', port=port, debug=False)
