# coding: utf-8

import os
import sys
import json
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkswr.v2.region.swr_region import SwrRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkswr.v2 import *

if __name__ == "__main__":
    # Get credentials and configuration from environment variables
    ak = os.environ.get("HUAWEI_CLOUD_ACCESS_KEY")
    sk = os.environ.get("HUAWEI_CLOUD_SECRET_KEY")
    region = os.environ.get("HUAWEI_SWR_REGION")
    namespace = os.environ.get("HUAWEI_SWR_NAMESPACE")
    repository = os.environ.get("REPOSITORY")

    # Validate required environment variables
    if not all([ak, sk, region, namespace, repository]):
        print("错误: 缺少必需的环境变量")
        print(f"HUAWEI_CLOUD_ACCESS_KEY: {'已设置' if ak else '未设置'}")
        print(f"HUAWEI_CLOUD_SECRET_KEY: {'已设置' if sk else '未设置'}")
        print(f"HUAWEI_SWR_REGION: {'已设置' if region else '未设置'}")
        print(f"HUAWEI_SWR_NAMESPACE: {'已设置' if namespace else '未设置'}")
        print(f"REPOSITORY: {'已设置' if repository else '未设置'}")
        sys.exit(1)

    credentials = BasicCredentials(ak, sk)

    client = SwrClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(SwrRegion.value_of(region)) \
        .build()

    # 华为云 SWR API 要求：仓库名称中的斜杠需要替换为 $
    # 例如：library/busybox -> library$busybox
    repository_encoded = repository.replace('/', '$')
    
    if repository != repository_encoded:
        print(f"仓库名称转换: {repository} -> {repository_encoded}")

    try:
        request = ShowRepositoryRequest()
        request.namespace = namespace
        request.repository = repository_encoded
        response = client.show_repository(request)
        
        # Check if repository is public
        is_public = response.is_public if hasattr(response, 'is_public') else False
        
        if is_public:
            print(f"验证成功: 仓库 {namespace}/{repository} 已设置为公开")
            print(f"仓库详情: {response}")
            sys.exit(0)
        else:
            print(f"验证失败: 仓库 {namespace}/{repository} 不是公开的")
            print(f"仓库详情: {response}")
            sys.exit(1)
    except exceptions.ClientRequestException as e:
        print(f"错误: 获取仓库信息失败")
        print(f"状态码: {e.status_code}")
        print(f"请求ID: {e.request_id}")
        print(f"错误码: {e.error_code}")
        print(f"错误信息: {e.error_msg}")
        sys.exit(1)