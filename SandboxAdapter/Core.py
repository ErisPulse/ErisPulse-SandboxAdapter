import asyncio
import json
import os
import time
from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
from ErisPulse import sdk
from ErisPulse.Core import router

class SandboxAdapter(sdk.BaseAdapter):
    """
    沙箱适配器，提供网页界面用于调试和模拟消息
    """
    
    class Send(sdk.BaseAdapter.Send):
        """消息发送DSL实现"""
        
        def __init__(self, adapter, target_type=None, target_id=None, account_id=None):
            super().__init__(adapter, target_type, target_id, account_id)
            self._at_user_ids = []
            self._reply_message_id = None
            self._at_all = False
        
        def Text(self, text: str):
            """发送文本消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="text",
                    content=text,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Image(self, file: str, summary: str = None):
            """发送图片消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="image",
                    content=file,
                    summary=summary,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Face(self, face_id: int):
            """发送表情消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="face",
                    content=str(face_id),
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def At(self, user_id: str):
            """@用户（可多次调用，链式修饰方法）"""
            self._at_user_ids.append(user_id)
            return self
        
        def AtAll(self):
            """@全体成员（链式修饰方法）"""
            self._at_all = True
            return self
        
        def Reply(self, message_id: str):
            """回复消息（链式修饰方法）"""
            self._reply_message_id = message_id
            return self
        
        def Recall(self, message_id: str):
            """撤回消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="recall",
                    content=f"撤回消息 {message_id}"
                )
            )
            self._reset_modifiers()
            return task
        
        def Raw_ob12(self, message):
            """发送原始 OneBot12 格式的消息段"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="raw_ob12",
                    content=message,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Json(self, json_data: str):
            """发送JSON消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="json",
                    content=json_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Xml(self, xml_data: str):
            """发送XML消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="xml",
                    content=xml_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Music(self, platform: str, id: str, title: str = None):
            """发送音乐分享消息"""
            music_data = {
                "type": "custom",
                "url": f"https://music.163.com/song/media/outer/url?id={id}.mp3",
                "audio": f"https://music.163.com/song/media/outer/url?id={id}.mp3",
                "title": title or f"音乐 {id}",
                "image": "https://webstatic.mihoyo.com/upload/static-resource/2022/02/23/6c7839055a7b6e3d8d8d8d8d8d8d8d_6966302954083748595.png"
            }
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="music",
                    content=music_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Record(self, file: str, magic: bool = False):
            """发送语音消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="record",
                    content=file,
                    magic=magic,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Voice(self, file: str):
            """发送语音消息（Record的别名）"""
            return self.Record(file)
        
        def Video(self, file: str):
            """发送视频消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="video",
                    content=file,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Html(self, html_data: str):
            """发送HTML消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="html",
                    content=html_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Markdown(self, markdown_data: str):
            """发送Markdown消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="markdown",
                    content=markdown_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Dice(self):
            """发送骰子消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="dice",
                    content="",
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Rps(self):
            """发送猜拳消息"""
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="rps",
                    content="",
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Location(self, lat: float, lon: float, title: str = None, content: str = None):
            """发送位置消息"""
            location_data = {
                "lat": lat,
                "lon": lon,
                "title": title or "",
                "content": content or ""
            }
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="location",
                    content=location_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Poke(self, user_id: str, type: str = "poke"):
            """发送戳一戳消息"""
            poke_data = {
                "user_id": user_id,
                "type": type
            }
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="poke",
                    content=poke_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def Share(self, url: str, title: str, content: str = None, image: str = None):
            """发送链接分享消息"""
            share_data = {
                "url": url,
                "title": title,
                "content": content or title,
                "image": image or ""
            }
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="share",
                    content=share_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id
                )
            )
            self._reset_modifiers()
            return task
        
        def _reset_modifiers(self):
            """重置链式修饰器状态"""
            self._at_user_ids = []
            self._reply_message_id = None
            self._at_all = False
    
    def __init__(self, sdk):
        super().__init__()
        self.sdk = sdk
        self.logger = sdk.logger
        self.adapter = self.sdk.adapter
        
        # 配置
        self.config = self._get_config()
        self.self_id = self.config.get("self_id", "sandbox_bot")
        
        # 存储系统
        self.storage = sdk.storage
        
        # 消息存储（按用户ID分组）
        # 结构: {user_id: [message1, message2, ...]}
        self.user_messages: Dict[str, List[Dict]] = {}
        
        # WebSocket 连接
        self._web_connections: List[WebSocket] = []
        
        # 初始化转换器
        self.convert = self._setup_converter()
        
        # 加载持久化数据
        self._load_persisted_data()
    
    def _setup_converter(self):
        from .Converter import SandboxConverter
        converter = SandboxConverter(self.self_id)
        return converter.convert
    
    def _get_config(self):
        """加载配置"""
        config = self.sdk.config.getConfig("SandboxAdapter", {})
        
        if not config:
            default_config = {
                "self_id": "sandbox_bot",
                "enable": True
            }
            self.sdk.config.setConfig("SandboxAdapter", default_config)
            return default_config
        
        return config
    
    def _load_persisted_data(self):
        """从持久化存储加载数据"""
        try:
            persisted_messages = self.storage.get("sandbox:user_messages", {})
            if persisted_messages:
                self.user_messages = self._clean_for_serialization(persisted_messages)
                total_messages = sum(len(msgs) for msgs in self.user_messages.values())
                self.logger.info(f"从存储加载了 {total_messages} 条消息，共 {len(self.user_messages)} 个用户")
        except Exception as e:
            self.logger.warning(f"加载数据失败: {e}")
    
    def _clean_for_serialization(self, data):
        """清理数据，确保所有字段都是JSON可序列化的"""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, bytes):
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                import base64
                try:
                    return base64.b64encode(data).decode('utf-8')
                except Exception:
                    return ''
        elif isinstance(data, dict):
            return {key: self._clean_for_serialization(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._clean_for_serialization(item) for item in data]
        else:
            return str(data)
    
    def _save_persisted_data(self):
        """保存数据到持久化存储"""
        try:
            # 保存用户消息（每个用户最多保留1000条）
            messages_to_save = {}
            for user_id, msgs in self.user_messages.items():
                messages_to_save[user_id] = msgs[-1000:] if len(msgs) > 1000 else msgs
            
            messages_to_save = self._clean_for_serialization(messages_to_save)
            self.storage.set("sandbox:user_messages", messages_to_save)
            
            total_messages = sum(len(msgs) for msgs in messages_to_save.values())
            self.logger.debug(f"保存了 {total_messages} 条消息")
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            import traceback
            self.logger.error(f"详细错误: {traceback.format_exc()}")
    
    async def call_api(self, endpoint: str, **params):
        """调用沙箱API"""
        
        if endpoint == "get_commands":
            # 获取命令列表
            return await self._handle_get_commands()
        
        elif endpoint == "send_msg":
            # 处理发送消息（Bot发送给用户）
            target_type = params.get("target_type", "user")
            target_id = params.get("target_id", "")
            message_type = params.get("message_type", "text")
            content = params.get("content", "")
            
            # 获取链式修饰器参数
            at_user_ids = params.get("at_user_ids", [])
            at_all = params.get("at_all", False)
            reply_message_id = params.get("reply_message_id", None)
            
            # 构建消息段数组（OneBot12 格式）
            message_segments = self._build_message_segments(
                message_type, content, at_user_ids, at_all, reply_message_id
            )
            
            # 构建消息
            message = {
                "type": "message",
                "message_type": "private",
                "user_id": self.self_id,  # Bot的ID
                "user_name": "机器人",
                "target_id": target_id,  # 目标用户ID
                "message": content,
                "message_type_detail": message_type,
                "message_segments": message_segments,
                "timestamp": int(time.time())
            }
            
            # 清理并保存消息
            message = self._clean_for_serialization(message)
            
            # 保存到目标用户的消息列表
            if target_id not in self.user_messages:
                self.user_messages[target_id] = []
            self.user_messages[target_id].append(message)
            
            # 持久化数据
            self._save_persisted_data()
            
            # 通过 WebSocket 发送到网页
            await self._broadcast_to_web({
                "type": "message",
                "data": message
            })
            
            return {
                "status": "ok",
                "retcode": 0,
                "data": {"message_id": str(len(self.user_messages.get(target_id, [])))},
                "message_id": str(len(self.user_messages.get(target_id, []))),
                "message": "消息发送成功",
                "self": {"user_id": self.self_id}
            }
        
        return {
            "status": "failed",
            "retcode": -1,
            "data": None,
            "message": "未知的API端点",
            "self": {"user_id": self.self_id}
        }
    
    def _build_message_segments(self, message_type, content, at_user_ids, at_all, reply_message_id):
        """构建消息段数组"""
        message_segments = []
        
        # 根据消息类型构建消息段
        if message_type == "text":
            message_segments = [{"type": "text", "data": {"text": content}}]
        elif message_type == "image":
            message_segments = [{"type": "image", "data": {"file": content}}]
        elif message_type == "face":
            message_segments = [{"type": "face", "data": {"id": content}}]
        elif message_type == "record":
            message_segments = [{"type": "record", "data": {"file": content}}]
        elif message_type == "video":
            message_segments = [{"type": "video", "data": {"file": content}}]
        elif message_type == "dice":
            import random
            dice_value = random.randint(1, 6)
            message_segments = [{"type": "dice", "data": {"result": str(dice_value)}}]
        elif message_type == "rps":
            import random
            rps_types = ["石头", "剪刀", "布"]
            rps_value = random.choice(rps_types)
            message_segments = [{"type": "rps", "data": {"result": rps_value}}]
        elif message_type == "location":
            if isinstance(content, dict):
                message_segments = [{"type": "location", "data": content}]
            else:
                message_segments = [{"type": "text", "data": {"text": str(content)}}]
        elif message_type == "poke":
            if isinstance(content, dict):
                message_segments = [{"type": "poke", "data": content}]
            else:
                message_segments = [{"type": "text", "data": {"text": str(content)}}]
        elif message_type == "share":
            if isinstance(content, dict):
                message_segments = [{"type": "share", "data": content}]
            else:
                message_segments = [{"type": "text", "data": {"text": str(content)}}]
        elif message_type == "music":
            if isinstance(content, dict):
                message_segments = [{"type": "music", "data": content}]
            else:
                message_segments = [{"type": "text", "data": {"text": str(content)}}]
        elif message_type == "html":
            message_segments = [{"type": "html", "data": {"data": content}}]
        elif message_type == "markdown":
            message_segments = [{"type": "markdown", "data": {"data": content}}]
        elif message_type == "json":
            message_segments = [{"type": "json", "data": {"data": content}}]
        elif message_type == "xml":
            message_segments = [{"type": "xml", "data": {"data": content}}]
        else:
            message_segments = [{"type": "text", "data": {"text": str(content)}}]
        
        # 在消息段前插入链式修饰器（@、@全体、回复）
        final_segments = []
        
        if reply_message_id:
            final_segments.append({
                "type": "reply",
                "data": {"message_id": reply_message_id}
            })
            final_segments.append({
                "type": "text",
                "data": {"text": " "}
            })
        
        if at_all:
            final_segments.append({
                "type": "mention_all",
                "data": {}
            })
            final_segments.append({
                "type": "text",
                "data": {"text": " "}
            })
        
        for user_id in at_user_ids:
            final_segments.append({
                "type": "mention",
                "data": {"user_id": user_id}
            })
            final_segments.append({
                "type": "text",
                "data": {"text": " "}
            })
        
        final_segments.extend(message_segments)
        
        return final_segments
    
    async def _broadcast_to_web(self, data: Dict):
        """向所有连接的网页客户端广播消息"""
        if not self._web_connections:
            return
        
        cleaned_data = self._clean_for_serialization(data)
        message = json.dumps(cleaned_data, ensure_ascii=False)
        disconnected = []
        
        for ws in self._web_connections:
            try:
                await ws.send_text(message)
            except Exception as e:
                self.logger.warning(f"向网页发送消息失败: {e}")
                disconnected.append(ws)
        
        for ws in disconnected:
            if ws in self._web_connections:
                self._web_connections.remove(ws)
    
    async def _web_ws_handler(self, websocket: WebSocket):
        """WebSocket 处理器"""
        self._web_connections.append(websocket)
        self.logger.info("网页客户端已连接")
        
        # 发送初始数据
        initial_data = {
            "type": "init",
            "data": {
                "self_id": self.self_id
            }
        }
        cleaned_data = self._clean_for_serialization(initial_data)
        await websocket.send_text(json.dumps(cleaned_data, ensure_ascii=False))
        
        try:
            while True:
                data = await websocket.receive_text()
                await self._handle_web_message(data)
        except WebSocketDisconnect:
            self.logger.info("网页客户端断开连接")
        except Exception as e:
            self.logger.error(f"WebSocket 处理异常: {e}")
        finally:
            if websocket in self._web_connections:
                self._web_connections.remove(websocket)
    
    async def _handle_web_message(self, raw_msg: str):
        """处理来自网页的消息"""
        try:
            data = json.loads(raw_msg)
            msg_type = data.get("type")
            
            if msg_type == "send_message":
                # 网页发送消息（用户发送给Bot）
                await self._handle_send_message(data.get("data", {}))
            
            elif msg_type == "load_messages":
                # 按需加载消息
                await self._handle_load_messages(data.get("data", {}))
            
            elif msg_type == "call_api":
                # 调用 API
                await self._handle_call_api(data.get("data", {}))
            
        except json.JSONDecodeError:
            self.logger.error(f"JSON 解析失败: {raw_msg}")
        except Exception as e:
            self.logger.error(f"处理网页消息异常: {e}")
    
    async def _handle_send_message(self, message_data: Dict):
        """处理网页发送的消息"""
        user_id = message_data.get("user_id", "")
        user_name = message_data.get("user_name", "")
        
        # 构建原始事件
        raw_event = {
            "type": "message",
            "message_type": "private",
            "user_id": user_id,
            "user_name": user_name,
            "message": message_data.get("message", ""),
            "message_type_detail": message_data.get("message_type_detail", "text"),
            "message_segments": message_data.get("message_segments", []),
            "target_id": self.self_id,  # 发送给Bot
            "timestamp": int(time.time())
        }
        
        # 保存到用户的消息列表
        if user_id not in self.user_messages:
            self.user_messages[user_id] = []
        self.user_messages[user_id].append(raw_event)
        
        # 持久化数据
        self._save_persisted_data()
        
        # 转换为 OneBot12 事件并发送给模块
        onebot_event = self.convert(raw_event)
        
        if onebot_event:
            self.logger.info(f"收到网页消息: {message_data.get('message', '')} (用户: {user_name})")
            await self.adapter.emit(onebot_event)
    
    async def _handle_load_messages(self, load_data: Dict):
        """处理加载消息请求"""
        contact_id = load_data.get("contact_id", "")
        contact_type = load_data.get("contact_type", "private")
        
        # 获取该用户的消息
        messages = self.user_messages.get(contact_id, [])
        
        # 发送过滤后的消息
        await self._broadcast_to_web({
            "type": "messages_loaded",
            "data": {
                "contact_id": contact_id,
                "contact_type": contact_type,
                "messages": messages
            }
        })
    
    async def _handle_get_commands(self):
        """获取命令列表"""
        try:
            # 导入命令处理器
            from ErisPulse.Core.Event import command as command_handler
            
            # 获取所有可见命令
            commands_dict = command_handler.get_visible_commands()
            
            # 构建命令列表
            commands_list = []
            for cmd_name, cmd_info in commands_dict.items():
                cmd_data = {
                    "name": cmd_name,
                    "help": cmd_info.get("help", ""),
                    "usage": cmd_info.get("usage", ""),
                    "group": cmd_info.get("group", ""),
                    "hidden": cmd_info.get("hidden", False)
                }
                
                # 获取别名
                aliases = [alias for alias, main_name in command_handler.aliases.items() 
                          if main_name == cmd_name]
                if aliases:
                    cmd_data["aliases"] = aliases
                
                commands_list.append(cmd_data)
            
            # 获取命令前缀
            prefix = command_handler.prefix
            
            return {
                "status": "ok",
                "retcode": 0,
                "data": {
                    "prefix": prefix,
                    "commands": commands_list,
                    "total": len(commands_list)
                },
                "message": f"获取了 {len(commands_list)} 个命令"
            }
        except ImportError:
            self.logger.warning("命令处理器模块未找到")
            return {
                "status": "ok",
                "retcode": 0,
                "data": {
                    "prefix": "/",
                    "commands": [],
                    "total": 0
                },
                "message": "命令系统未启用"
            }
        except Exception as e:
            self.logger.error(f"获取命令列表失败: {e}")
            return {
                "status": "failed",
                "retcode": -1,
                "data": {
                    "prefix": "/",
                    "commands": [],
                    "total": 0
                },
                "message": f"获取命令列表失败: {str(e)}"
            }
    
    async def _handle_call_api(self, api_data: Dict):
        """处理来自网页的 API 调用请求"""
        endpoint = api_data.get("endpoint", "")
        
        if not endpoint:
            await self._broadcast_to_web({
                "type": "api_response",
                "data": {
                    "status": "failed",
                    "retcode": -1,
                    "message": "缺少 endpoint 参数"
                }
            })
            return
        
        try:
            # 调用 API
            result = await self.call_api(endpoint, **{k: v for k, v in api_data.items() if k != "endpoint"})
            
            # 广播 API 响应
            await self._broadcast_to_web({
                "type": "api_response",
                "data": result
            })
        except Exception as e:
            self.logger.error(f"API 调用失败: {e}")
            await self._broadcast_to_web({
                "type": "api_response",
                "data": {
                    "status": "failed",
                    "retcode": -1,
                    "message": f"API 调用失败: {str(e)}"
                }
            })
    
    async def register_routes(self):
        """注册路由"""
        # 注册 WebSocket 路由
        router.register_websocket(
            "sandbox",
            "/ws",
            self._web_ws_handler
        )
        
        # 注册静态文件路由
        async def serve_index():
            html_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                from fastapi.responses import HTMLResponse
                return HTMLResponse(content=html_content, status_code=200)
            except Exception as e:
                self.logger.error(f"读取 HTML 文件失败: {e}")
                from fastapi.responses import HTMLResponse
                return HTMLResponse(content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)
        
        router.register_http_route(
            "sandbox",
            "/",
            serve_index,
            methods=["GET"]
        )
        
        self.logger.info("沙箱适配器路由已注册")
    
    async def start(self):
        """启动适配器"""
        self.logger.info("正在启动沙箱适配器...")
        
        # 注册路由
        await self.register_routes()
        
        # 从配置读取服务器地址
        server_config = self.sdk.config.getConfig("ErisPulse.server", {})
        host = server_config.get("host", "0.0.0.0")
        port = server_config.get("port", 8000)
        
        self.logger.info("沙箱适配器启动完成")
        self.logger.info(f"访问地址: http://{'localhost' if host == '0.0.0.0' else host}:{port}/sandbox/")
    
    async def shutdown(self):
        """关闭适配器"""
        self.logger.info("正在关闭沙箱适配器...")
        
        # 取消注册路由
        router.unregister_websocket("sandbox", "/ws")
        router.unregister_http_route("sandbox", "/")
        
        # 关闭所有 WebSocket 连接
        for ws in self._web_connections:
            try:
                await ws.close()
            except Exception as e:
                self.logger.warning(f"关闭 WebSocket 连接失败: {e}")
        
        self._web_connections.clear()
        self.logger.info("沙箱适配器已关闭")