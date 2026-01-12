# ErisPulse 沙箱适配器

ErisPulse 的沙箱适配器，提供网页界面用于调试和模拟消息，
可以帮助您在不接入实际机器人平台的情况下进行开发和测试。

## 安装

```bash
pip install ErisPulse-SandboxAdapter
# 或者 epsdk install sandbox
```

## 配置

在 `config.toml` 中添加以下配置：

```toml
[SandboxAdapter]
self_id = "sandbox_bot"
enable = true
```

## 开发
沙箱适配器可以模拟一个完整的标准适配器，可以辅助开发和调试，使用时请确保你进行了多适配器的适配
在获取到事件event后可以获取platform属性进行平台判断，具体实现请查看ErisPulse的官方文档

## 使用

1. 启动适配器后，访问 `http://localhost:8000/sandbox/`（端口号根据你的配置）
2. 在网页中添加虚拟好友或群聊
3. 选择一个聊天，发送消息
4. 适配器会自动将消息转换为 OneBot12 标准事件并发送给模块

## 网页界面功能
![ErisPulse-SandboxAdapter](.github/image.png)
