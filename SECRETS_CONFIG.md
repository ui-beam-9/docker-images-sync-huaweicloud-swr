# GitHub Secrets 配置说明

本项目需要在 GitHub Repository Settings 中配置以下 Secrets：

## 必需的 Secrets

### 1. 华为云访问凭证
- **`HUAWEI_CLOUD_ACCESS_KEY`**: 华为云 Access Key (AK)
- **`HUAWEI_CLOUD_SECRET_KEY`**: 华为云 Secret Key (SK)

获取方式：登录华为云控制台 → 我的凭证 → 访问密钥

### 2. 华为云 SWR 配置
- **`HUAWEI_SWR_REGION`**: 华为云 SWR 区域代码
  - 示例值：`cn-east-3`（华东-上海一）
  - 其他可选值：`cn-north-4`（华北-北京四）、`cn-south-1`（华南-广州）等
  - ⚠️ 注意：只需填写区域代码，不要填写完整域名

- **`HUAWEI_SWR_NAMESPACE`**: 华为云 SWR 命名空间
  - 示例值：`ui_beam-images`
  - 需要在华为云 SWR 控制台预先创建

### 3. Docker 登录凭证
- **`HUAWEI_SWR_DOCKER_USERNAME`**: 华为云 SWR Docker 登录用户名
  - 格式：`<区域名称>@<AK>`
  - 示例：`cn-east-3@ABCDEFGHIJKLMNOPQRST`

- **`HUAWEI_SWR_DOCKER_PASSWORD`**: 华为云 SWR Docker 登录密码
  - 这是通过华为云 SWR 控制台生成的登录密码（与 SK 不同）
  - 获取方式：登录华为云 SWR 控制台 → 右上角用户名 → 我的凭证 → 容器镜像服务登录指令

## 配置步骤

1. 进入 GitHub Repository
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 依次添加上述所有 Secrets

## 区域对照表

| 区域代码 | 区域名称 | 完整域名 |
|---------|---------|---------|
| cn-north-4 | 华北-北京四 | swr.cn-north-4.myhuaweicloud.com |
| cn-north-1 | 华北-北京一 | swr.cn-north-1.myhuaweicloud.com |
| cn-east-3 | 华东-上海一 | swr.cn-east-3.myhuaweicloud.com |
| cn-east-2 | 华东-上海二 | swr.cn-east-2.myhuaweicloud.com |
| cn-south-1 | 华南-广州 | swr.cn-south-1.myhuaweicloud.com |

## 注意事项

1. **AK/SK 安全**：请妥善保管，不要泄露到代码仓库中
2. **区域一致性**：确保 `HUAWEI_SWR_REGION` 和 Docker 登录用户名中的区域代码一致
3. **命名空间**：命名空间必须在华为云 SWR 控制台预先创建
4. **权限要求**：AK/SK 需要有 SWR 的读写权限

## 测试配置

配置完成后，可以通过创建一个 Issue 来测试镜像同步功能：
1. 使用 [镜像同步 Issue 模板](../../issues/new?assignees=&labels=sync+image&projects=&template=sync-image.yml)
2. 填写要同步的镜像名称（如：`docker.io/library/nginx:latest`）
3. 提交 Issue 后，GitHub Actions 会自动执行同步流程
