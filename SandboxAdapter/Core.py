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
        
        def Text(self, text: str):
            """发送文本消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="text",
                    content=text
                )
            )
        
        def Image(self, file: str, summary: str = None):
            """发送图片消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="image",
                    content=file,
                    summary=summary
                )
            )
        
        def Face(self, face_id: int):
            """发送表情消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="face",
                    content=str(face_id)
                )
            )
        
        def At(self, user_id: str):
            """发送@消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="at",
                    content=user_id
                )
            )
        
        def AtAll(self):
            """发送@全体成员消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="mention_all",
                    content=""
                )
            )
        
        def Reply(self, message_id: str):
            """发送回复消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="reply",
                    content=message_id
                )
            )
        
        def Json(self, json_data: str):
            """发送JSON消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="json",
                    content=json_data
                )
            )
        
        def Xml(self, xml_data: str):
            """发送XML消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="xml",
                    content=xml_data
                )
            )
        
        def Music(self, platform: str, id: str, title: str = None):
            """发送音乐分享消息"""
            music_data = {
                "type": "custom",
                "url": f"https://music.163.com/song/media/outer/url?id={id}.mp3",
                "audio": f"https://music.163.com/song/media/outer/url?id={id}.mp3",
                "title": title or f"音乐 {id}",
                "image": "https://webstatic.mihoyo.com/upload/static-resource/2022/02/23/6c7839055a7b6e3d8d8d8d8d8d8d8d8d_6966302954083748595.png"
            }
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="music",
                    content=music_data
                )
            )
        
        def Record(self, file: str, magic: bool = False):
            """发送语音消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="record",
                    content=file,
                    magic=magic
                )
            )
        
        def Video(self, file: str):
            """发送视频消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="video",
                    content=file
                )
            )
        
        def Html(self, html_data: str):
            """发送HTML消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="html",
                    content=html_data
                )
            )
        
        def Markdown(self, markdown_data: str):
            """发送Markdown消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="markdown",
                    content=markdown_data
                )
            )
        
        def Dice(self):
            """发送骰子消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="dice",
                    content=""
                )
            )
        
        def Rps(self):
            """发送猜拳消息"""
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="rps",
                    content=""
                )
            )
        
        def Location(self, lat: float, lon: float, title: str = None, content: str = None):
            """发送位置消息"""
            location_data = {
                "lat": lat,
                "lon": lon,
                "title": title or "",
                "content": content or ""
            }
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="location",
                    content=location_data
                )
            )
        
        def Poke(self, user_id: str, type: str = "poke"):
            """发送戳一戳消息"""
            poke_data = {
                "user_id": user_id,
                "type": type
            }
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="poke",
                    content=poke_data
                )
            )
        
        def Share(self, url: str, title: str, content: str = None, image: str = None):
            """发送链接分享消息"""
            share_data = {
                "url": url,
                "title": title,
                "content": content or title,
                "image": image or ""
            }
            return asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="share",
                    content=share_data
                )
            )
    
    def __init__(self, sdk):
        super().__init__()
        self.sdk = sdk
        self.logger = sdk.logger
        self.adapter = self.sdk.adapter
        
        # 配置
        self.config = self._get_config()
        self.self_id = self.config.get("self_id", "sandbox_bot")
        
        # 存储系统（用于数据持久化）
        self.storage = sdk.storage
        
        # 虚拟用户和群组存储
        self.friends: Dict[str, Dict] = {}  # user_id -> {name, avatar, ...}
        self.groups: Dict[str, Dict] = {}   # group_id -> {name, members: [], ...}
        self.messages: List[Dict] = []       # 消息记录
        
        # WebSocket 连接（网页端）
        self._web_connections: List[WebSocket] = []
        
        # 初始化转换器
        self.convert = self._setup_converter()
        
        # 从持久化存储加载数据
        self._load_persisted_data()
        
        # 如果没有数据，加载默认数据
        self._init_default_data()
    
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
            # 加载好友数据
            persisted_friends = self.storage.get("sandbox:friends", {})
            if persisted_friends:
                self.friends.update(persisted_friends)
                self.logger.info(f"从存储加载了 {len(self.friends)} 个好友")
            
            # 加载群组数据
            persisted_groups = self.storage.get("sandbox:groups", {})
            if persisted_groups:
                self.groups.update(persisted_groups)
                self.logger.info(f"从存储加载了 {len(self.groups)} 个群组")
            
            # 加载消息数据
            persisted_messages = self.storage.get("sandbox:messages", [])
            if persisted_messages:
                # 清理加载的消息数据
                cleaned_messages = self._clean_for_serialization(persisted_messages)
                self.messages.extend(cleaned_messages)
                self.logger.info(f"从存储加载了 {len(cleaned_messages)} 条消息")
        except Exception as e:
            self.logger.warning(f"加载数据失败: {e}")
    
    def _clean_for_serialization(self, data):
        """清理数据，确保所有字段都是JSON可序列化的"""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, bytes):
            # 尝试解码bytes为UTF-8字符串
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                # 如果是二进制数据（图片、视频等），转换为base64
                import base64
                try:
                    return base64.b64encode(data).decode('utf-8')
                except Exception:
                    return ''
        elif isinstance(data, dict):
            # 特殊处理消息段：检测媒体类型并转换base64
            if 'type' in data and 'data' in data:
                segment_type = data['type']
                segment_data = data['data']
                if segment_type in ['image', 'video', 'record']:
                    # 图片/视频/语音消息段
                    if 'file' in segment_data and isinstance(segment_data['file'], bytes):
                        import base64
                        try:
                            segment_data['file'] = base64.b64encode(segment_data['file']).decode('utf-8')
                        except Exception:
                            segment_data['file'] = ''
            return {key: self._clean_for_serialization(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._clean_for_serialization(item) for item in data]
        else:
            # 对于其他类型，转换为字符串
            return str(data)

    def _save_persisted_data(self):
        """保存数据到持久化存储"""
        try:
            # 保存好友数据
            self.storage.set("sandbox:friends", self._clean_for_serialization(self.friends))

            # 保存群组数据
            self.storage.set("sandbox:groups", self._clean_for_serialization(self.groups))

            # 保存消息数据（只保存最近 1000 条）
            messages_to_save = self.messages[-1000:] if len(self.messages) > 1000 else self.messages
            # 清理消息数据，确保可以序列化
            messages_to_save = self._clean_for_serialization(messages_to_save)
            self.storage.set("sandbox:messages", messages_to_save)

            self.logger.info(f"保存了 {len(messages_to_save)} 条消息")
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            import traceback
            self.logger.error(f"详细错误: {traceback.format_exc()}")
    
    def _init_default_data(self):
        """初始化默认数据"""
        # 只有在没有持久化数据时才添加默认数据
        if not self.friends:
            # 添加默认好友
            self.friends["eris"] = {
                "id": "eris",
                "name": "Eris Greyrat (艾莉丝·格雷拉特)",
                "avatar": ""
            }
            self.friends["roxy"] = {
                "id": "roxy",
                "name": "Roxy Migurdia (洛琪希·米格路迪亚)",
                "avatar": ""
            }
            # 保存默认好友
            self._save_persisted_data()
        
        if not self.groups:
            # 添加默认群组
            self.groups["grayrat_house"] = {
                "id": "grayrat_house",
                "name": "格雷拉特家",
                "members": ["eris", "roxy", "ruphyne"]
            }
            # 保存默认群组
            self._save_persisted_data()
    
    async def call_api(self, endpoint: str, **params):
        """调用沙箱API"""

        if endpoint == "send_msg":
            # 处理发送消息
            target_type = params.get("target_type", "user")
            target_id = params.get("target_id", "")
            message_type = params.get("message_type", "text")
            content = params.get("content", "")
            
            # 构建消息段数组（OneBot12 格式）
            message_segments = []
            
            # 根据消息类型构建消息段
            if message_type == "text":
                message_segments = [{"type": "text", "data": {"text": content}}]
                display_text = content
            elif message_type == "image":
                message_segments = [{"type": "image", "data": {"file": content}}]
                display_text = f"[图片: {content}]"
            elif message_type == "face":
                message_segments = [{"type": "face", "data": {"id": content}}]
                display_text = f"[表情: {content}]"
            elif message_type == "at":
                message_segments = [
                    {"type": "mention", "data": {"user_id": content}},
                    {"type": "text", "data": {"text": " "}}
                ]
                display_text = f"@{content} "
            elif message_type == "mention_all":
                message_segments = [
                    {"type": "mention_all", "data": {}},
                    {"type": "text", "data": {"text": " "}}
                ]
                display_text = "@全体成员 "
            elif message_type == "reply":
                message_segments = [
                    {"type": "reply", "data": {"message_id": content}},
                    {"type": "text", "data": {"text": " "}}
                ]
                display_text = f"[回复: {content}] "
            elif message_type == "json":
                message_segments = [{"type": "json", "data": {"data": content}}]
                display_text = "[JSON消息]"
            elif message_type == "xml":
                message_segments = [{"type": "xml", "data": {"data": content}}]
                display_text = "[XML消息]"
            elif message_type == "html":
                message_segments = [{"type": "html", "data": {"data": content}}]
                display_text = "[HTML消息]"
            elif message_type == "markdown":
                message_segments = [{"type": "markdown", "data": {"data": content}}]
                display_text = "[Markdown消息]"
            elif message_type == "record":
                message_segments = [{"type": "record", "data": {"file": content}}]
                display_text = f"[语音: {content}]"
            elif message_type == "video":
                message_segments = [{"type": "video", "data": {"file": content}}]
                display_text = f"[视频: {content}]"
            elif message_type == "dice":
                import random
                dice_value = random.randint(1, 6)
                message_segments = [{"type": "dice", "data": {"result": str(dice_value)}}]
                display_text = f"🎲 {dice_value}"
            elif message_type == "rps":
                import random
                rps_types = ["石头", "剪刀", "布"]
                rps_value = random.choice(rps_types)
                message_segments = [{"type": "rps", "data": {"result": rps_value}}]
                display_text = f"✊ {rps_value}"
            elif message_type == "location":
                if isinstance(content, dict):
                    lat = content.get("lat", 0)
                    lon = content.get("lon", 0)
                    title = content.get("title", "位置")
                    location_data = {
                        "lat": lat,
                        "lon": lon,
                        "title": title
                    }
                    message_segments = [{"type": "location", "data": location_data}]
                    display_text = f"[位置: {title}]"
                else:
                    message_segments = [{"type": "text", "data": {"text": str(content)}}]
                    display_text = str(content)
            elif message_type == "poke":
                if isinstance(content, dict):
                    user_id = content.get("user_id", "")
                    message_segments = [{"type": "poke", "data": content}]
                    display_text = f"[戳一戳: {user_id}]"
                else:
                    message_segments = [{"type": "text", "data": {"text": str(content)}}]
                    display_text = str(content)
            elif message_type == "share":
                if isinstance(content, dict):
                    url = content.get("url", "")
                    title = content.get("title", "链接分享")
                    share_data = {
                        "url": url,
                        "title": title,
                        "content": content.get("content", title),
                        "image": content.get("image", "")
                    }
                    message_segments = [{"type": "share", "data": share_data}]
                    display_text = f"[分享: {title}]"
                else:
                    message_segments = [{"type": "text", "data": {"text": str(content)}}]
                    display_text = str(content)
            elif message_type == "music":
                if isinstance(content, dict):
                    music_data = content
                    title = music_data.get("title", "未知音乐")
                    message_segments = [{"type": "music", "data": music_data}]
                    display_text = f"[音乐分享: {title}]"
                else:
                    message_segments = [{"type": "text", "data": {"text": str(content)}}]
                    display_text = str(content)
            else:
                # 默认文本消息
                message_segments = [{"type": "text", "data": {"text": content}}]
                display_text = content

            # 构建消息
            message = {
                "type": "message",
                "message_type": "private" if target_type == "user" else "group",
                "user_id": self.self_id,
                "user_name": "机器人",
                "message": display_text,
                "message_type_detail": message_type,
                "message_segments": message_segments,
                "timestamp": int(time.time())
            }

            # 记录目标信息（私聊需要知道发给谁）
            if target_type == "user":
                # 私聊消息，记录目标用户ID
                message["target_id"] = target_id
            else:
                # 群聊消息
                message["group_id"] = target_id
                message["group_name"] = self.groups.get(target_id, {}).get("name", "")

            # 清理消息数据，确保可以序列化
            message = self._clean_for_serialization(message)

            # 保存消息记录
            self.messages.append(message)

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
                "data": {"message_id": str(len(self.messages))},
                "message": "消息发送成功",
                "self": {"user_id": self.self_id}
            }

        elif endpoint == "clear_all_data":
            # 清空所有数据（包括好友、群组和消息）
            self.friends.clear()
            self.groups.clear()
            self.messages.clear()
            
            # 持久化数据
            self._save_persisted_data()
            
            return {
                "status": "ok",
                "retcode": 0,
                "data": None,
                "message": "所有数据已清空",
                "self": {"user_id": self.self_id}
            }
        
        return {
            "status": "failed",
            "retcode": -1,
            "data": None,
            "message": "未知的API端点",
            "self": {"user_id": self.self_id}
        }
    
    async def _broadcast_to_web(self, data: Dict):
        """向所有连接的网页客户端广播消息"""
        if not self._web_connections:
            return

        # 清理数据，确保可以序列化
        cleaned_data = self._clean_for_serialization(data)

        message = json.dumps(cleaned_data, ensure_ascii=False)
        disconnected = []

        for ws in self._web_connections:
            try:
                await ws.send_text(message)
            except Exception as e:
                self.logger.warning(f"向网页发送消息失败: {e}")
                disconnected.append(ws)

        # 清理断开的连接
        for ws in disconnected:
            if ws in self._web_connections:
                self._web_connections.remove(ws)
    
    async def _web_ws_handler(self, websocket: WebSocket):
        """WebSocket 处理器"""
        self._web_connections.append(websocket)
        self.logger.info("网页客户端已连接")

        # 发送初始数据（清理后再发送，不包含所有消息，只发送联系人和self_id）
        initial_data = {
            "type": "init",
            "data": {
                "friends": list(self.friends.values()),
                "groups": list(self.groups.values()),
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
                # 网页发送消息，转换为 OneBot12 事件
                await self._handle_send_message(data.get("data", {}))
            
            elif msg_type == "add_friend":
                # 添加好友
                await self._handle_add_friend(data.get("data", {}))
            
            elif msg_type == "add_group":
                # 添加群组
                await self._handle_add_group(data.get("data", {}))
            
            elif msg_type == "delete_friend":
                # 删除好友
                await self._handle_delete_friend(data.get("data", {}))
            
            elif msg_type == "delete_group":
                # 删除群组
                await self._handle_delete_group(data.get("data", {}))
            
            elif msg_type == "clear_messages":
                # 清空消息记录
                self.messages.clear()

                # 持久化数据
                self._save_persisted_data()

                await self._broadcast_to_web({"type": "messages_cleared"})

            elif msg_type == "load_messages":
                # 按需加载消息
                contact_data = data.get("data", {})
                contact_id = contact_data.get("contact_id", "")
                contact_type = contact_data.get("contact_type", "private")  # private 或 group

                # 过滤对应聊天的消息
                filtered_messages = []
                for msg in self.messages:
                    if contact_type == "private":
                        # 私聊消息：只显示私聊消息
                        if msg.get("message_type") != "private":
                            continue

                        # 判断消息是否属于当前聊天
                        is_from_contact = msg.get("user_id") == contact_id  # 联系人发送的消息
                        is_from_bot = msg.get("user_id") == self.self_id  # 机器人发送的消息

                        if is_from_contact:
                            # 联系人发送的消息，显示在这个联系人的聊天中
                            filtered_messages.append(msg)
                        elif is_from_bot:
                            # 机器人发送的消息，需要判断是发给谁的
                            target_id = msg.get("target_id") or msg.get("group_id")
                            if target_id == contact_id:
                                filtered_messages.append(msg)
                    else:
                        # 群聊：只显示该群组的消息
                        if msg.get("group_id") == contact_id:
                            filtered_messages.append(msg)

                # 发送过滤后的消息
                await self._broadcast_to_web({
                    "type": "messages_loaded",
                    "data": {
                        "contact_id": contact_id,
                        "contact_type": contact_type,
                        "messages": filtered_messages
                    }
                })

        except json.JSONDecodeError:
            self.logger.error(f"JSON 解析失败: {raw_msg}")
        except Exception as e:
            self.logger.error(f"处理网页消息异常: {e}")
    
    async def _handle_send_message(self, message_data: Dict):
        """处理网页发送的消息"""
        message_type = message_data.get("message_type", "private")
        
        raw_event = {
            "type": "message",
            "message_type": message_type,
            "user_id": message_data.get("user_id", ""),
            "user_name": message_data.get("user_name", ""),
            "message": message_data.get("message", ""),
            "timestamp": int(time.time())
        }
        
        # 添加消息段和消息类型详细信息
        if "message_type_detail" in message_data:
            raw_event["message_type_detail"] = message_data["message_type_detail"]
        
        if "message_segments" in message_data:
            raw_event["message_segments"] = message_data["message_segments"]
        
        if message_type == "group":
            raw_event["group_id"] = message_data.get("group_id", "")
            raw_event["group_name"] = message_data.get("group_name", "")
        
        # 保存消息记录（用于新连接的初始化）
        self.messages.append(raw_event)
        
        # 持久化数据
        self._save_persisted_data()
        
        # 注意：不广播到网页，因为前端已经通过乐观更新显示了
        # 只需要转换为 OneBot12 事件并发送给模块
        
        # 转换为 OneBot12 事件并发送给模块
        onebot_event = self.convert(raw_event)
        
        if onebot_event:
            self.logger.info(f"收到网页消息: {message_data.get('message', '')} (类型: {message_data.get('message_type_detail', 'text')})")
            await self.adapter.emit(onebot_event)
    
    async def _handle_add_friend(self, friend_data: Dict):
        """添加好友"""
        friend_id = friend_data.get("id", f"user{len(self.friends) + 1}")
        self.friends[friend_id] = {
            "id": friend_id,
            "name": friend_data.get("name", f"用户{len(self.friends) + 1}"),
            "avatar": ""
        }
        
        # 持久化数据
        self._save_persisted_data()
        
        await self._broadcast_to_web({
            "type": "friend_added",
            "data": self.friends[friend_id]
        })
        
        # 发送好友添加通知事件
        raw_event = {
            "type": "notice",
            "notice_type": "friend_increase",
            "user_id": friend_id
        }
        onebot_event = self.convert(raw_event)
        if onebot_event:
            await self.adapter.emit(onebot_event)
    
    async def _handle_add_group(self, group_data: Dict):
        """添加群组"""
        group_id = group_data.get("id", f"group{len(self.groups) + 1}")
        self.groups[group_id] = {
            "id": group_id,
            "name": group_data.get("name", f"测试群{len(self.groups) + 1}"),
            "members": group_data.get("members", [])
        }
        
        # 持久化数据
        self._save_persisted_data()
        
        await self._broadcast_to_web({
            "type": "group_added",
            "data": self.groups[group_id]
        })
    
    async def _handle_delete_friend(self, friend_data: Dict):
        """删除好友"""
        friend_id = friend_data.get("id")
        if friend_id in self.friends:
            del self.friends[friend_id]
            
            # 持久化数据
            self._save_persisted_data()
            
            await self._broadcast_to_web({
                "type": "friend_deleted",
                "data": {"id": friend_id}
            })
    
    async def _handle_delete_group(self, group_data: Dict):
        """删除群组"""
        group_id = group_data.get("id")
        if group_id in self.groups:
            del self.groups[group_id]
            
            # 持久化数据
            self._save_persisted_data()
            
            await self._broadcast_to_web({
                "type": "group_deleted",
                "data": {"id": group_id}
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
            # 读取 HTML 文件
            html_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                # 直接返回 HTML 字符串，FastAPI 会自动设置 Content-Type
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
        
        # 关闭所有 WebSocket 连接
        for ws in self._web_connections:
            try:
                await ws.close()
            except Exception as e:
                self.logger.warning(f"关闭 WebSocket 连接失败: {e}")
        
        self._web_connections.clear()
        self.logger.info("沙箱适配器已关闭")