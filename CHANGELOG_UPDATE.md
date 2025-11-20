# 项目更新说明

## 更新日期
2024-11-20

## 主要变更

### 1. 替换 API 调用方式
- ❌ 旧方式：使用自定义 API 端点（`APIURL`）通过 HTTP 请求设置镜像公开状态
- ✅ 新方式：使用华为云官方 SDK（`huaweicloudsdkswr`）直接调用华为云 SWR API

### 2. 环境变量重命名
以下环境变量已重命名，更加明确和规范：

| 旧变量名 | 新变量名 | 说明 |
|---------|---------|------|
| `DOCKER_USERNAME` | `HUAWEI_SWR_DOCKER_USERNAME` | 华为云 SWR Docker 登录用户名 |
| `DOCKER_PASSWORD` | `HUAWEI_SWR_DOCKER_PASSWORD` | 华为云 SWR Docker 登录密码 |
| `REGISTRY` | `HUAWEI_SWR_REGION` | 华为云 SWR 区域（仅区域代码） |
| `NAMESPACE` | `HUAWEI_SWR_NAMESPACE` | 华为云 SWR 命名空间 |

新增环境变量：
- `HUAWEI_CLOUD_ACCESS_KEY`: 华为云 Access Key
- `HUAWEI_CLOUD_SECRET_KEY`: 华为云 Secret Key

### 3. Registry 地址处理优化
- **旧方式**：`REGISTRY` 存储完整地址（如：`swr.cn-east-3.myhuaweicloud.com`）
- **新方式**：`HUAWEI_SWR_REGION` 仅存储区域代码（如：`cn-east-3`），在 workflow 中自动组合完整地址
  - 格式：`swr.${HUAWEI_SWR_REGION}.myhuaweicloud.com`

### 4. Python 脚本优化

#### UpdateRepo-Public.py
- 从环境变量读取所有配置参数
- 添加参数验证和错误处理
- 支持从 GitHub Actions 动态传入仓库名称

#### ShowRepository.py
- 从环境变量读取所有配置参数
- 添加仓库公开状态验证逻辑
- 提供清晰的验证成功/失败输出

### 5. GitHub Actions Workflow 改进

#### 新增步骤
1. **Setup Python**: 安装 Python 3.x 环境
2. **Install Huawei Cloud SDK**: 安装华为云 SDK 依赖
3. **Set Repository to Public**: 使用 Python 脚本设置仓库为公开
4. **Verify Repository is Public**: 验证仓库是否成功设置为公开

#### 优化点
- 移除对自定义 API 的依赖
- 使用官方 SDK，更加稳定可靠
- 添加详细的日志输出
- 自动提取仓库名称（去除域名前缀）

## 迁移指南

### 如果你正在使用旧版本
1. 删除以下旧的 Secrets：
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `REGISTRY`
   - `APIURL`（不再需要）

2. 添加新的 Secrets（参考 `SECRETS_CONFIG.md`）：
   - `HUAWEI_CLOUD_ACCESS_KEY`
   - `HUAWEI_CLOUD_SECRET_KEY`
   - `HUAWEI_SWR_REGION`（只填区域代码）
   - `HUAWEI_SWR_NAMESPACE`
   - `HUAWEI_SWR_DOCKER_USERNAME`
   - `HUAWEI_SWR_DOCKER_PASSWORD`

3. 拉取最新代码

### 新项目配置
直接按照 `SECRETS_CONFIG.md` 文档配置所需的 Secrets 即可。

## 技术优势

1. **更加安全**：使用官方 SDK，减少中间环节，降低安全风险
2. **更加稳定**：不依赖自定义 API 服务，减少单点故障
3. **更加可靠**：华为云官方 SDK 有完善的错误处理和重试机制
4. **更好维护**：代码结构更清晰，易于理解和维护
5. **更强扩展**：可以轻松使用更多华为云 SWR API 功能

## 依赖包

项目新增以下 Python 依赖（在 workflow 中自动安装）：
- `huaweicloudsdkcore`: 华为云 SDK 核心库
- `huaweicloudsdkswr`: 华为云容器镜像服务 SDK

## 测试建议

1. 配置好所有必需的 Secrets
2. 创建一个测试 Issue 同步小镜像（如：`alpine:latest`）
3. 观察 Actions 运行日志，确认各步骤正常执行
4. 验证镜像是否成功同步并设置为公开

## 相关文档

- [Secrets 配置说明](./SECRETS_CONFIG.md)
- [华为云 SWR 文档](https://support.huaweicloud.com/swr/index.html)
- [华为云 Python SDK](https://github.com/huaweicloud/huaweicloud-sdk-python-v3)
