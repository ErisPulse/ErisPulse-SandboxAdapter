import asyncio
from ErisPulse import sdk

async def main():
    # 初始化 SDK
    await sdk.init()
    
    # 启动适配器
    await sdk.adapter.startup()
    
    print("沙箱适配器已启动")
    
    # 监听消息事件
    @sdk.adapter.on("message")
    async def message_handler(data):
        if data["platform"] == "sandbox":
            print(f"收到沙箱消息: {data['alt_message']}")
            
            # 获取消息类型和发送者信息
            user_id = data.get("user_id", "")
            user_name = data.get("user_nickname", "")
            message = data.get("alt_message", "")
            
            print(f"发送者: {user_name} ({user_id})")
            print(f"消息内容: {message}")
            
            # 回复消息
            platform = data["platform"]
            adapter_instance = getattr(sdk.adapter, platform)
            
            # 简单的回复逻辑
            if "你好" in message:
                if data.get("detail_type") == "group":
                    group_id = data.get("group_id", "")
                    await adapter_instance.Send.To("group", group_id).Text(f"你好，{user_name}！")
                else:
                    await adapter_instance.Send.To("user", user_id).Text(f"你好，{user_name}！")
            elif "时间" in message:
                from datetime import datetime
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if data.get("detail_type") == "group":
                    group_id = data.get("group_id", "")
                    await adapter_instance.Send.To("group", group_id).Text(f"当前时间: {current_time}")
                else:
                    await adapter_instance.Send.To("user", user_id).Text(f"当前时间: {current_time}")
            else:
                if data.get("detail_type") == "group":
                    group_id = data.get("group_id", "")
                    await adapter_instance.Send.To("group", group_id).Text(f"我收到了你的消息: {message}")
                else:
                    await adapter_instance.Send.To("user", user_id).Text(f"我收到了你的消息: {message}")
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭...")
        await sdk.adapter.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
