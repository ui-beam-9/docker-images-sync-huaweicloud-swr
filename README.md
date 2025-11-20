
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

### 2️⃣ 查询已同步镜像

访问 [已同步镜像查询](https://404.ui-beam.com/404.html) 查看已经同步过的镜像列表。

---

## ⚙️ 配置说明

### 必需的 GitHub Secrets

在 `Settings` → `Secrets and variables` → `Actions` 中配置以下 Secrets：

#### 1. 华为云访问凭证

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `HUAWEI_CLOUD_ACCESS_KEY` | 华为云 Access Key (AK) | 华为云控制台 → 我的凭证 → 访问密钥 |
| `HUAWEI_CLOUD_SECRET_KEY` | 华为云 Secret Key (SK) | 华为云控制台 → 我的凭证 → 访问密钥 |

#### 2. 华为云 SWR 配置

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `HUAWEI_SWR_REGION` | 华为云 SWR 区域代码 | `cn-east-3` |
| `HUAWEI_SWR_NAMESPACE` | 华为云 SWR 命名空间 | `your-namespace` |

**⚠️ 注意**：
- `HUAWEI_SWR_REGION` 只需填写区域代码（如 `cn-east-3`），不要填写完整域名
- 命名空间需要在华为云 SWR 控制台预先创建

#### 3. Docker 登录凭证

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `HUAWEI_SWR_DOCKER_USERNAME` | 华为云 SWR Docker 登录用户名 | `cn-east-3@YOUR_AK` |
| `HUAWEI_SWR_DOCKER_PASSWORD` | 华为云 SWR Docker 登录密码 | `从 SWR 控制台获取` |

**获取 Docker 登录密码**：
1. 登录华为云 SWR 控制台
2. 右上角用户名 → 我的凭证 → 容器镜像服务登录指令
3. 查看并复制登录密码

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
- **Skopeo**: 镜像复制工具，无需本地存储
- **华为云 Python SDK**: 官方 SDK，用于设置和验证镜像权限
- **华为云 SWR**: 目标镜像仓库

### 依赖包

项目自动安装以下 Python 依赖：
- `huaweicloudsdkcore`: 华为云 SDK 核心库
- `huaweicloudsdkswr`: 华为云容器镜像服务 SDK

### 技术优势

1. **安全可靠**: 使用华为云官方 SDK，减少安全风险
2. **稳定高效**: Skopeo 直接复制，无需本地存储
3. **完善日志**: 详细的执行日志和错误提示
4. **易于维护**: 代码结构清晰，注释完整
5. **灵活扩展**: 支持多种配置选项

---

## 📝 配置步骤

### 第一步：创建华为云 SWR 命名空间

1. 登录 [华为云控制台](https://console.huaweicloud.com/)
2. 进入容器镜像服务（SWR）
3. 创建组织（命名空间）

### 第二步：获取访问凭证

1. 访问 **我的凭证** → **访问密钥**
2. 创建或查看 Access Key (AK) 和 Secret Key (SK)
3. 在 SWR 控制台获取 Docker 登录密码

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
3. **命名空间**: 必须在华为云 SWR 控制台预先创建命名空间
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
2. 确认命名空间是否存在
3. 查看 Python 脚本执行日志

---

## 📚 相关资源

- [华为云 SWR 官方文档](https://support.huaweicloud.com/swr/index.html)
- [华为云 Python SDK](https://github.com/huaweicloud/huaweicloud-sdk-python-v3)
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
