# 镜像域名去除配置说明

## 配置项：`REMOVE_SOURCE_DOMAIN`

这个配置项控制在同步镜像到华为云 SWR 时，是否去除源镜像的域名部分。

## 配置方式

在 GitHub Repository Settings → Secrets and variables → Actions 中添加：

**Secret 名称**: `REMOVE_SOURCE_DOMAIN`  
**Secret 值**: `true` 或 `false`（或不设置）

## 效果对比

### 场景 1：`REMOVE_SOURCE_DOMAIN = true`（去除域名）

| 源镜像 | 同步到 SWR 后的路径 |
|--------|-------------------|
| `docker.io/library/busybox:latest` | `swr.cn-east-3.myhuaweicloud.com/namespace/library/busybox:latest` |
| `gcr.io/google-containers/pause:3.1` | `swr.cn-east-3.myhuaweicloud.com/namespace/google-containers/pause:3.1` |
| `quay.io/prometheus/node-exporter:v1.0.0` | `swr.cn-east-3.myhuaweicloud.com/namespace/prometheus/node-exporter:v1.0.0` |
| `k8s.gcr.io/kube-proxy:v1.28.0` | `swr.cn-east-3.myhuaweicloud.com/namespace/kube-proxy:v1.28.0` |
| `nginx:latest` | `swr.cn-east-3.myhuaweicloud.com/namespace/nginx:latest` |

**优点**：
- ✅ 路径更简洁
- ✅ 避免多层嵌套
- ✅ 节省存储空间
- ✅ 符合大多数镜像加速场景的习惯

**适用场景**：
- 公共镜像加速服务
- 镜像缓存代理
- 大多数使用场景

---

### 场景 2：`REMOVE_SOURCE_DOMAIN = false` 或不设置（保留完整路径）

| 源镜像 | 同步到 SWR 后的路径 |
|--------|-------------------|
| `docker.io/library/busybox:latest` | `swr.cn-east-3.myhuaweicloud.com/namespace/docker.io/library/busybox:latest` |
| `gcr.io/google-containers/pause:3.1` | `swr.cn-east-3.myhuaweicloud.com/namespace/gcr.io/google-containers/pause:3.1` |
| `quay.io/prometheus/node-exporter:v1.0.0` | `swr.cn-east-3.myhuaweicloud.com/namespace/quay.io/prometheus/node-exporter:v1.0.0` |
| `k8s.gcr.io/kube-proxy:v1.28.0` | `swr.cn-east-3.myhuaweicloud.com/namespace/k8s.gcr.io/kube-proxy:v1.28.0` |
| `nginx:latest` | `swr.cn-east-3.myhuaweicloud.com/namespace/nginx:latest` |

**优点**：
- ✅ 保留完整的源信息
- ✅ 可以区分不同源的同名镜像
- ✅ 便于追溯镜像来源

**适用场景**：
- 需要明确区分镜像源的场景
- 需要保留完整路径信息的企业内部使用
- 多源镜像仓库整合

---

## 如何选择？

### 推荐配置：`REMOVE_SOURCE_DOMAIN = true`

大多数情况下推荐设置为 `true`，理由：
1. **路径更简洁**：减少不必要的路径层级
2. **节省空间**：在华为云 SWR 中创建更少的仓库
3. **使用方便**：拉取镜像时路径更短
4. **兼容性好**：符合大多数镜像加速服务的习惯

### 特殊场景使用 `false`

只在以下情况考虑设置为 `false`：
- 需要在同一个命名空间下保存来自不同源的同名镜像
- 企业内部需要严格追踪镜像来源
- 有特殊的镜像管理策略要求保留完整路径

---

## 配置步骤

1. 登录 GitHub，进入你的仓库
2. 点击 `Settings` → `Secrets and variables` → `Actions`
3. 点击 `New repository secret`
4. 填写：
   - Name: `REMOVE_SOURCE_DOMAIN`
   - Value: `true`
5. 点击 `Add secret`

## 验证配置

配置完成后，创建一个测试 Issue：
1. 使用镜像同步 Issue 模板
2. 填写镜像名称，如：`docker.io/library/alpine:latest`
3. 提交 Issue
4. 观察 Actions 日志中的输出：
   - 如果看到 `✓ 已启用域名去除`，说明配置生效
   - 如果看到 `✗ 未启用域名去除`，说明使用默认配置（保留完整路径）

## 注意事项

1. **配置更改后立即生效**：修改 Secret 后，下次同步即生效
2. **不影响已同步的镜像**：只影响新同步的镜像
3. **可随时修改**：可以根据需要随时更改配置
4. **删除配置等同于 false**：如果删除这个 Secret，系统默认保留完整路径

## 示例 Actions 日志

### 启用域名去除时的日志：
```
✓ 已启用域名去除，检测到域名，去除后: library/busybox:latest
开始同步镜像:
  源镜像: docker.io/library/busybox:latest
  目标镜像: swr.cn-east-3.myhuaweicloud.com/namespace/library/busybox:latest
```

### 未启用域名去除时的日志：
```
✗ 未启用域名去除，使用完整镜像名: docker.io/library/busybox:latest
开始同步镜像:
  源镜像: docker.io/library/busybox:latest
  目标镜像: swr.cn-east-3.myhuaweicloud.com/namespace/docker.io/library/busybox:latest
```
