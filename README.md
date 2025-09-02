### 项目说明
本项目用于更新阿里云OSS上自定义域名的 HTTPS 证书，通过官方 Python SDK 实现。为自动化应用提供解决方案。



### 使用说明

使用前，记得安装依赖：

```bash
pip install -r requirements.txt
```

然后，将 `config.example.json` 复制为 `config.json`，并填写相应的配置信息。
```bash
cp config.example.json config.json
```

对于其中的 `alibaba_cloud_access_key_id` 和 `alibaba_cloud_access_key_secret`：
- 需要在阿里云控制台中，创建一个 RAM 用户，并为其授权。
  - 按照最小权限原则，只需要给予该用户 OSS 以及 **SSL 证书**相关权限即可。注意证书是上传到 SSL 证书服务的，因此这个权限也要有。
  - 你可以使用系统的权限模版，例如 `AliyunOSSFullAccess` 和 `AliyunYundunCertFullAccess`，如果你想要进一步扩展安全性，可以自定义权限。这里是我对 OSS 权限的配置：
    ```json
    {
      "Version": "1",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": "oss:*",
          "Resource": "acs:oss:*:*:你的bucket名称"
        },
        {
          "Effect": "Deny",
          "Action": [
            "oss:DeleteBucket",
            "oss:DeleteObject",
            "oss:PutBucketAcl",
            "oss:PutObjectAcl"
          ],
          "Resource": "acs:oss:*:*:你的bucket名称"
        }
      ]
    }
    ```
- 然后，你需要为 RAM 用户创建一对 `AccessKeyID` 和 `AccessKeySecret`，填入配置文件中。
- 一些具体内容可以参考下方阿里官方文档



随后，在完成这些配置后，可以手动运行脚本进行测试。

如果没有问题，通常，你可以配合 acme.sh 等工具，实现自动更新证书，例如：

```bash
acme.sh --install-cert -d example.com \ 
--key-file        /path/to/privkey.pem \  
--fullchain-file  /path/to/fullchain.pem \ 
--reloadcmd      "bash /path/to/aliyun_update.sh"
```

这样，可以实现一个全自动化流程。




### 阿里官方文档参考

- [如何为OSS Python SDK配置访问凭证](https://help.aliyun.com/zh/oss/developer-reference/python-configuration-access-credentials)
  - 本次使用了“最小化授权的RAM用户的AK”，[RAM 用户管理](https://ram.console.aliyun.com/users)
- [Python绑定自定义域名](https://help.aliyun.com/zh/oss/developer-reference/map-custom-domain-names-4)
- [PutCname接口参考文档](https://help.aliyun.com/zh/oss/developer-reference/putcname)
- [OSS地域和访问域名](https://help.aliyun.com/zh/oss/user-guide/regions-and-endpoints)



### 敏感信息说明

项目包含敏感信息，如阿里云的 `AccessKeyID` 和 `AccessKeySecret`，这些信息不应该被提交到代码仓库中，因此在`.gitignore`文件中添加了相应文件。


### 相近项目推荐

- [AliyunOSS_CertUpdate：通过 GitHub Actions 自动申请并更新证书](https://github.com/luodeb/AliyunOSS_CertUpdate/)
