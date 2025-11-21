
# Docker 镜像同步到华为云 SWR

🚀 自动同步 Docker 镜像到华为云容器镜像服务（SWR）

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?style=flat&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Huawei Cloud](https://img.shields.io/badge/Huawei-Cloud-FF0000?style=flat&logo=huawei&logoColor=white)](https://www.huaweicloud.com/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

---

## 📖 项目简介

本项目通过 GitHub Actions 自动将 Docker 镜像同步到华为云 SWR（Software Repository for Container），解决国内访问 Docker Hub、GCR、Quay 等国外镜像仓库速度慢或无法访问的问题。

### ✨ 主要特性

- ✅ **自动化同步**：通过 Issue 触发，全自动同步流程
- ✅ **企业微信集成**：通过企业微信应用发送镜像名称，自动创建同步任务并接收实时通知
- ✅ **自动构建镜像**：自动构建企业微信服务器 Docker 镜像并推送到 SWR
- ✅ **官方 SDK**：使用华为云官方 Python SDK，稳定可靠
- ✅ **灵活配置**：支持域名去除、区域选择等多种配置
- ✅ **状态验证**：自动设置镜像为公开并验证状态
- ✅ **详细日志**：完整的同步日志和错误提示
- ✅ **多源支持**：支持 Docker Hub、GCR、Quay 等多个镜像源

---

## 🚀 快速开始

### 1️⃣ 使用方法

1. 访问 [镜像同步 Issue 模板](../../issues/new?assignees=&labels=sync+image&projects=&template=sync-image.yml)
2. 填写要同步的镜像名称（如：`docker.io/library/nginx:latest`）
3. 提交 Issue，GitHub Actions 会自动开始同步
4. 同步完成后，Issue 会自动关闭并显示同步结果

### 2️⃣ 通过企业微信同步（推荐）

通过企业微信应用发送镜像名称，自动创建同步任务并接收实时通知。

#### 使用步骤

1. 在企业微信中打开 **镜像同步助手** 应用
2. 直接发送镜像名称，例如：
   ```
   docker.io/library/nginx:latest
   ```
3. 服务器自动创建 GitHub Issue 并触发同步
4. 收到企业微信通知消息：
   ```
   ✅ 镜像同步任务已创建
   
   镜像名称: docker.io/library/nginx:latest
   Issue 编号: #123
   状态: 等待同步
   
   查看详情: https://github.com/...
   ```

#### 部署企业微信服务器

**服务器代码位置**：`wecom-webhook/` 文件夹

**步骤 1：配置环境变量**

```bash
cd wecom-webhook
cp .env.example .env
nano .env
```

填写以下配置：

```bash
# 企业微信应用配置
WECOM_CORP_ID=your_corp_id_here           # 企业 ID
WECOM_AGENT_ID=1000002                    # 应用 ID
WECOM_SECRET=your_app_secret_here         # 应用密钥
WECOM_TOKEN=your_random_token             # 接收消息 Token（自定义，至少 32 位）
WECOM_ENCODING_AES_KEY=your_aes_key       # 加解密密钥（43 位）
WECOM_API_BASE=https://qyapi.weixin.qq.com  # 企业微信 API 地址（动态IP需反代，参考配置说明）

# GitHub 配置
GITHUB_TOKEN=ghp_xxxxx                    # GitHub Personal Access Token
GITHUB_REPO=owner/repo                    # 仓库名称（格式：owner/repo）
```

**配置说明**：

| 配置项 | 说明 | 获取方式 |
|--------|------|---------|
| `WECOM_CORP_ID` | 企业 ID | 企业微信管理后台 → 我的企业 → 企业信息 |
| `WECOM_AGENT_ID` | 应用 ID | 应用详情页面 → AgentId |
| `WECOM_SECRET` | 应用密钥 | 应用详情页面 → Secret（点击查看）|
| `WECOM_TOKEN` | 接收消息 Token | 自定义字符串，至少 32 位 |
| `WECOM_ENCODING_AES_KEY` | 加解密密钥 | 随机生成，43 位字符 |
| `WECOM_API_BASE` | 企业微信 API 地址 | 默认：`https://qyapi.weixin.qq.com`<br>动态 IP 服务器需配置反代（见下文） |
| `GITHUB_TOKEN` | GitHub Token | [GitHub Settings](https://github.com/settings/tokens)，需要 `repo` 权限 |
| `GITHUB_REPO` | 仓库名称 | 格式：`owner/repo` |

<details>
<summary>💡 企业微信 API 反代配置（视情况而定）</summary>

企业微信有**企业可信 IP** 配置，只有在可信 IP 列表中的服务器才能调用企业微信 API。

**是否需要反代取决于服务器 IP 类型：**

| 服务器 IP 类型 | 是否需要反代 | 说明 |
|--------------|------------|------|
| 🔄 动态公网 IP | ✅ **需要** | IP 会变化，无法固定添加到可信 IP 列表，必须通过反代服务器 |
| 📍 固定公网 IP | ❌ **不需要** | 直接将服务器 IP 添加到可信 IP 列表，使用官方地址即可 |
| 🏠 内网 IP / NAT | ✅ **需要** | 无固定公网 IP，必须通过反代服务器 |

**如何配置反代：**

**Nginx 反代配置：**

```nginx
location ^~ / {
    proxy_pass https://qyapi.weixin.qq.com; 
    proxy_set_header Host qyapi.weixin.qq.com; 
    proxy_set_header X-Real-IP $remote_addr; 
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; 
    proxy_set_header REMOTE-HOST $remote_addr; 
    proxy_set_header Upgrade $http_upgrade; 
    proxy_set_header Connection $http_connection; 
    proxy_set_header X-Forwarded-Proto $scheme; 
    proxy_http_version 1.1; 
    add_header X-Cache $upstream_cache_status; 
    add_header Cache-Control no-cache; 
    proxy_ssl_server_name off; 
    proxy_ssl_name $proxy_host; 
    add_header Strict-Transport-Security "max-age=31536000"; 
}
```

**配置步骤：**
1. 准备一台**具有固定公网 IP** 的服务器用作反代
2. 在该服务器上配置上述 Nginx 反代
3. 在企业微信管理后台将该反代服务器的 IP 添加到**企业可信 IP**列表
4. 将 `.env` 中的 `WECOM_API_BASE` 修改为你的反代地址（如：`https://wecom-api.yourdomain.com`）

**如果你的 Webhook 服务器有固定公网 IP：**
1. 直接将 Webhook 服务器 IP 添加到企业微信**企业可信 IP**列表
2. `.env` 中的 `WECOM_API_BASE` 使用官方地址 `https://qyapi.weixin.qq.com` 即可

</details>

**步骤 2：部署服务**

可以选择以下任意一种方式部署：

#### 🚀 快速部署

使用一键部署脚本：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ui-beam-9/docker-images-sync-huaweicloud-swr/main/quick-deploy.sh)
```

脚本功能：
- ✅ 自动检测 Docker 和 Docker Compose
- ✅ 支持自定义安装目录（默认 `/opt/wecom-webhook`）
- ✅ 自动检测权限，需要时提示使用 sudo
- ✅ 两种部署方式可选：Docker 镜像部署 或 服务器直接部署

> � 脚本源码：[quick-deploy.sh](./quick-deploy.sh)

#### 🔧 手动部署

**方式一：Docker 镜像部署（推荐）**

无需下载项目代码，只需下载配置文件：

```bash
# 1. 创建部署目录
mkdir wecom-webhook && cd wecom-webhook

# 2. 下载配置文件
curl -O https://raw.githubusercontent.com/ui-beam-9/docker-images-sync-huaweicloud-swr/main/wecom-webhook/.env.example
curl -O https://raw.githubusercontent.com/ui-beam-9/docker-images-sync-huaweicloud-swr/main/wecom-webhook/docker-compose.yml
mv .env.example .env

# 3. 编辑 .env 文件，填写你的实际配置
nano .env

# 4. 启动服务（会自动拉取预构建镜像）
docker-compose up -d

# 5. 查看日志
docker-compose logs -f
```

**方式二：服务器直接部署（自定义代码）**

适合需要修改代码的场景：

```bash
# 1. 克隆项目
git clone https://github.com/ui-beam-9/docker-images-sync-huaweicloud-swr.git
cd docker-images-sync-huaweicloud-swr/wecom-webhook

# 2. 配置环境变量
cp .env.example .env
nano .env  # 填写你的配置

# 3. 修改 docker-compose.yml 使用本地构建
nano docker-compose.yml
# 注释掉: image: swr.cn-east-3.myhuaweicloud.com/ui_beam-images/wecom-webhook-server:latest
# 取消注释: # build: .

# 4. 启动服务
docker-compose up -d

# 5. 查看日志
docker-compose logs -f
```

**步骤 3：配置企业微信应用**

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 进入 **应用管理** → 你的应用 → **接收消息**
3. 点击 **设置 API 接收**，填写：
   - **URL**: `https://your-domain.com/wecom/callback`（你的服务器公网地址）
   - **Token**: 与 `.env` 中的 `WECOM_TOKEN` 相同
   - **EncodingAESKey**: 与 `.env` 中的 `WECOM_ENCODING_AES_KEY` 相同
4. 点击 **保存**，看到 ✅ 验证成功即可

**注意**：
- Webhook 服务器需要部署在有公网访问的服务器上
- 如果服务器是动态公网 IP，需要配置反代服务（参考上方配置说明）
- 如果服务器是固定公网 IP，直接将 IP 添加到企业微信可信 IP 列表即可

### 3️⃣ 查询已同步镜像

访问 [已同步镜像查询](https://404.ui-beam.com/404.html) 查看已经同步过的镜像列表。

---

## ⚙️ 配置说明

### 必需的 GitHub Secrets

在 `Settings` → `Secrets and variables` → `Actions` 中配置以下 Secrets：

#### 1. 华为云访问凭证

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `HUAWEI_CLOUD_ACCESS_KEY` | 华为云 Access Key (AK) | [华为云访问凭证](https://console.huaweicloud.com/iam#/mine/accessKey) |
| `HUAWEI_CLOUD_SECRET_KEY` | 华为云 Secret Key (SK) | [华为云访问凭证](https://console.huaweicloud.com/iam#/mine/accessKey) |

#### 2. 华为云 SWR 配置

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `HUAWEI_SWR_REGION` | 华为云 SWR 区域代码 | `cn-east-3` |
| `HUAWEI_SWR_NAMESPACE` | 华为云 SWR 组织名称 | `your-organization` |

**⚠️ 注意**：
- `HUAWEI_SWR_REGION` 只需填写区域代码（如 `cn-east-3`），不要填写完整域名
- 组织名称需要在 [华为云 SWR 控制台](https://console.huaweicloud.com/swr/?region=cn-east-3#/swr/dashboard) 预先创建
- 该链接默认打开华东-上海一区域，如需切换区域，请在页面顶部自行选择

#### 3. Docker 登录凭证

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `HUAWEI_SWR_DOCKER_USERNAME` | 华为云 SWR Docker 登录用户名 | `cn-east-3@YOUR_AK` |
| `HUAWEI_SWR_DOCKER_PASSWORD` | 华为云 SWR Docker 登录密码 | `从 SWR 控制台获取` |

**获取 Docker 登录密码**：
1. 登录 [华为云 SWR 控制台](https://console.huaweicloud.com/swr/?region=cn-east-3#/swr/dashboard)
2. 总览 → 右上角登录指令
3. 查看并复制登录密码，建议使用长期有效登录指令

### 可选的 GitHub Secrets

#### 4. 镜像域名去除选项

| Secret 名称 | 可选值 | 默认值 | 说明 |
|------------|--------|--------|------|
| `REMOVE_SOURCE_DOMAIN` | `true` / `false` | `false` | 是否去除源镜像的域名部分 |

---

## 🔧 域名去除配置详解

### 什么是域名去除？

控制在同步镜像时，是否保留源镜像的域名部分。

### 效果对比

#### 场景 1：`REMOVE_SOURCE_DOMAIN = true` （推荐）

去除域名，路径更简洁：

| 源镜像 | 同步后的 SWR 路径 |
|--------|------------------|
| `docker.io/library/busybox:latest` | `swr.cn-east-3.myhuaweicloud.com/namespace/library/busybox:latest` |
| `gcr.io/google-containers/pause:3.1` | `swr.cn-east-3.myhuaweicloud.com/namespace/google-containers/pause:3.1` |
| `quay.io/prometheus/node-exporter:v1.0.0` | `swr.cn-east-3.myhuaweicloud.com/namespace/prometheus/node-exporter:v1.0.0` |

**优点**：
- ✅ 路径简洁，易于使用
- ✅ 节省 SWR 存储空间
- ✅ 符合镜像加速服务习惯

#### 场景 2：`REMOVE_SOURCE_DOMAIN = false` 或不设置

保留完整路径：

| 源镜像 | 同步后的 SWR 路径 |
|--------|------------------|
| `docker.io/library/busybox:latest` | `swr.cn-east-3.myhuaweicloud.com/namespace/docker.io/library/busybox:latest` |
| `gcr.io/google-containers/pause:3.1` | `swr.cn-east-3.myhuaweicloud.com/namespace/gcr.io/google-containers/pause:3.1` |

**优点**：
- ✅ 保留完整源信息
- ✅ 便于追溯镜像来源
- ✅ 可区分不同源的同名镜像

### 推荐配置

大多数情况下推荐设置 `REMOVE_SOURCE_DOMAIN = true`：
- 路径更简洁
- 节省存储空间
- 使用更方便

---

## 📋 华为云 SWR 区域对照表

| 区域代码 | 区域名称 | 完整域名 |
|---------|---------|---------|
| `cn-north-4` | 华北-北京四 | swr.cn-north-4.myhuaweicloud.com |
| `cn-north-1` | 华北-北京一 | swr.cn-north-1.myhuaweicloud.com |
| `cn-east-3` | 华东-上海一 | swr.cn-east-3.myhuaweicloud.com |
| `cn-east-2` | 华东-上海二 | swr.cn-east-2.myhuaweicloud.com |
| `cn-south-1` | 华南-广州 | swr.cn-south-1.myhuaweicloud.com |

---

## 🔄 同步流程

```
提交 Issue
    ↓
验证镜像名称格式
    ↓
登录华为云 SWR
    ↓
使用 Skopeo 同步镜像
    ↓
设置镜像仓库为公开
    ↓
验证仓库公开状态
    ↓
更新 Issue 并关闭
```

---

## 💡 使用示例

### 同步 Docker Hub 镜像

在 Issue 中填写：
```
docker.io/library/nginx:latest
```

同步后可通过以下方式拉取（假设 `REMOVE_SOURCE_DOMAIN = true`）：
```bash
docker pull swr.cn-east-3.myhuaweicloud.com/your-namespace/library/nginx:latest
```

### 同步 Google Container Registry 镜像

在 Issue 中填写：
```
gcr.io/google-containers/pause:3.9
```

同步后拉取：
```bash
docker pull swr.cn-east-3.myhuaweicloud.com/your-namespace/google-containers/pause:3.9
```

### 同步 Quay.io 镜像

在 Issue 中填写：
```
quay.io/prometheus/node-exporter:v1.7.0
```

同步后拉取：
```bash
docker pull swr.cn-east-3.myhuaweicloud.com/your-namespace/prometheus/node-exporter:v1.7.0
```

---

## 🛠️ 技术架构

### 核心组件

- **GitHub Actions**: 自动化工作流引擎
- **企业微信 Webhook 服务器**: 接收企业微信消息，自动创建 GitHub Issues
- **Skopeo**: 镜像复制工具，无需本地存储
- **华为云 Python SDK**: 官方 SDK，用于设置和验证镜像权限
- **华为云 SWR**: 目标镜像仓库

### 工作流程

```
┌──────────────────────────┐
│     用户在企业微信        │
│   发送镜像名称消息        │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   Webhook 服务器          │
│  （你的服务器，公网地址）  │
│  - 接收并解密消息         │
│  - 提取镜像名称           │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│    调用 GitHub API       │
│    创建 Issue            │
└────────────┬─────────────┘
             │
       ┌─────┴─────┐
       │           │
       ▼           ▼
┌─────────────┐  ┌──────────────────────┐
│GitHub Actions│  │  调用企业微信 API     │
│  自动同步    │  │ （反代地址）          │
│             │  │  发送通知消息         │
│  - 登录 SWR │  └──────────┬───────────┘
│  - 同步镜像 │             │
│  - 设为公开 │             ▼
└──────┬──────┘  ┌──────────────────────┐
       │         │   用户收到通知消息    │
       │         │                      │
       ▼         │  ✅ 镜像同步任务已创建 │
┌─────────────┐  │  镜像: nginx:latest  │
│  华为云 SWR  │  │  Issue: #123         │
│  存储镜像    │  │  状态: 等待同步       │
└─────────────┘  └──────────────────────┘
```

**说明**：
- **Webhook 服务器**：需要部署在公网可访问的服务器上
- **企业微信 API**：固定 IP 直接加入可信列表，动态 IP 需通过反代访问
- **消息通知**：Issue 创建后立即发送，用户实时收到反馈

### 依赖包

项目自动安装以下 Python 依赖：
- `huaweicloudsdkcore`: 华为云 SDK 核心库
- `huaweicloudsdkswr`: 华为云容器镜像服务 SDK

### GitHub Actions 工作流

项目包含两个自动化工作流：

#### 1. 镜像同步工作流（`target-image-sync.yml`）
- **触发条件**: 创建带有 `sync image` 标签的 Issue
- **功能**:
  - 使用 Skopeo 同步 Docker 镜像到华为云 SWR
  - 自动设置镜像仓库为公开
  - 验证镜像仓库状态
  - 同步完成后自动关闭 Issue

#### 2. Docker 镜像构建工作流（`build-docker-image.yml`）
- **触发条件**: 
  - 推送代码到 `main`/`master` 分支（`wecom-webhook/` 目录有变化）
  - 每天北京时间 0:00 和 12:00 定时构建
  - 手动触发
- **功能**:
  - 自动构建企业微信服务器 Docker 镜像
  - 推送镜像到华为云 SWR（`latest` 标签）
  - 自动设置镜像仓库为公开
  - 使用 GitHub Actions 缓存加速构建

**使用预构建镜像**：
```bash
docker pull swr.cn-east-3.myhuaweicloud.com/ui_beam-images/wecom-webhook-server:latest
```

### 技术优势

1. **安全可靠**: 使用华为云官方 SDK，减少安全风险
2. **稳定高效**: Skopeo 直接复制，无需本地存储
3. **完善日志**: 详细的执行日志和错误提示
4. **易于维护**: 代码结构清晰，注释完整
5. **灵活扩展**: 支持多种配置选项

---

## 📝 配置步骤

### 第一步：创建华为云 SWR 组织

1. 登录 [华为云 SWR 控制台](https://console.huaweicloud.com/swr/?region=cn-east-3#/swr/dashboard)
   - 该链接默认打开华东-上海一区域，如需修改，请在页面顶部切换区域
2. 点击左侧菜单 **组织管理**
3. 点击 **创建组织**，输入组织名称并创建

### 第二步：获取访问凭证

1. 访问 [华为云访问凭证](https://console.huaweicloud.com/iam#/mine/accessKey)
2. 创建或查看 Access Key (AK) 和 Secret Key (SK)
3. 在 [SWR 控制台](https://console.huaweicloud.com/swr/?region=cn-east-3#/swr/dashboard) 获取 Docker 登录密码

### 第三步：配置 GitHub Secrets

1. 进入你的 GitHub 仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 依次添加所有必需的 Secrets

### 第四步：测试同步

1. 创建测试 Issue，填写镜像名称（如：`alpine:latest`）
2. 提交 Issue，观察 Actions 执行日志
3. 验证镜像是否成功同步到 SWR

---

## ⚠️ 注意事项

1. **AK/SK 安全**: 请妥善保管访问密钥，不要提交到代码仓库
2. **区域一致性**: 确保所有配置中的区域代码保持一致
3. **组织名称**: 必须在 [华为云 SWR 控制台](https://console.huaweicloud.com/swr/?region=cn-east-3#/swr/dashboard) 预先创建组织
4. **权限要求**: AK/SK 需要有 SWR 的读写权限
5. **配额限制**: 注意华为云 SWR 的存储配额和流量限制
6. **镜像大小**: 大镜像同步需要更长时间，请耐心等待

---

## 🔍 故障排查

### Issue 同步失败

1. 检查 Actions 执行日志，查看具体错误信息
2. 确认所有 Secrets 配置正确
3. 验证镜像名称格式是否正确
4. 确认华为云账户状态和 SWR 配额

### 镜像无法拉取

1. 确认镜像已成功同步到 SWR
2. 检查仓库是否设置为公开
3. 验证拉取命令中的域名和路径是否正确

### 仓库设置公开失败

1. 检查 AK/SK 是否有 SWR 权限
2. 确认组织名称是否存在
3. 查看 Python 脚本执行日志

### 企业微信消息接收问题

1. 检查 Webhook 服务器是否正常运行：`curl http://localhost:8080/health`
2. 确认企业微信应用配置是否正确（`WECOM_CORP_ID`, `WECOM_AGENT_ID`, `WECOM_SECRET`）
3. 检查企业微信 API 反代是否可用
4. 查看服务器日志：`cd wecom-webhook && docker-compose logs -f`
5. 验证 Access Token 获取是否成功
6. 确认 GitHub Token 权限正确

---

## 📚 相关资源

### 官方文档
- [华为云 SWR 官方文档](https://support.huaweicloud.com/swr/index.html)
- [华为云 Python SDK](https://github.com/huaweicloud/huaweicloud-sdk-python-v3)
- [企业微信开发文档](https://developer.work.weixin.qq.com/document/)
- [Skopeo 官方文档](https://github.com/containers/skopeo)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目基于原项目 [docker-registry-mirrors](https://github.com/kubesre/docker-registry-mirrors) 修改。

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！**

Made with ❤️ by the community

</div>
