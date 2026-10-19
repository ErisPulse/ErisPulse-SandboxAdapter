import asyncio
import html as _html
import json
import os
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List

from ErisPulse import sdk
from ErisPulse.Core import router
from ErisPulse.Core.Bases import BaseConfig
from ErisPulse.runtime.tasks import spawn_background

__version__ = "4.2.0"

# 软依赖的框架最低版本（运行时检测，仅提示不强制）
MIN_FRAMEWORK_VERSION = (2, 7, 1)


def _forward_node_text(node: Dict) -> str:
    """提取合并转发节点 content 中全部 text 段文本（段间直接连接）"""
    data = node.get("data") or {}
    return "".join(
        str(seg.get("data", {}).get("text") or "")
        for seg in (data.get("content") or [])
        if isinstance(seg, dict) and seg.get("type") == "text"
    )


def _forward_nodes_plain(nodes, separator: str = "\n") -> str:
    """合并转发节点降级纯文本：每条「昵称: 正文」"""
    lines = []
    for node in nodes if isinstance(nodes, list) else [nodes]:
        if not isinstance(node, dict):
            continue
        data = node.get("data") or {}
        nickname = str(data.get("nickname") or "").strip()
        text = _forward_node_text(node).strip()
        if nickname and text:
            lines.append(f"{nickname}: {text}")
        elif text:
            lines.append(text)
    return separator.join(lines)


def _build_forward_html(nodes, title: str = "合并聊天记录") -> str:
    """渲染合并转发折叠 HTML 卡片（<details> 折叠 + CSS 系统色，自动适配明暗主题）"""
    bubbles = []
    for node in nodes if isinstance(nodes, list) else [nodes]:
        if not isinstance(node, dict):
            continue
        data = node.get("data") or {}
        nickname = str(data.get("nickname") or "")
        text = _forward_node_text(node).strip()
        if not text:
            continue
        body = _html.escape(text).replace("\n", "<br>")
        bubbles.append(
            '<div style="margin:8px 0;padding:10px 12px;border:1px solid GrayText;border-radius:8px;'
            'background:Canvas;color:CanvasText;">'
            '<div style="font-size:12px;line-height:1.4;margin-bottom:6px;color:GrayText;">'
            f"<strong>{_html.escape(nickname)}</strong></div>"
            '<div style="font-size:14px;line-height:1.6;word-break:break-word;color:CanvasText;">' + body + "</div></div>"
        )
    if not bubbles:
        return ""
    return (
        '<div style="color:CanvasText;color-scheme:light dark;">'
        '<details style="width:100%;box-sizing:border-box;border:1px solid GrayText;border-radius:10px;'
        'background:Canvas;color:CanvasText;overflow:hidden;">'
        '<summary style="list-style:none;cursor:pointer;padding:10px 12px;background:Canvas;'
        'border-bottom:1px solid GrayText;font-size:14px;font-weight:600;color:CanvasText;">'
        f"{_html.escape(title)}</summary>"
        '<div style="padding:8px 10px;">' + "".join(bubbles) + "</div></details></div>"
    )


from fastapi import WebSocket, WebSocketDisconnect


@dataclass
class SandboxConfig(BaseConfig):
    self_id: str = field(
        default="sandbox_bot",
        metadata={"description": "沙箱机器人ID", "required": False},
    )
    enable: bool = field(
        default=True,
        metadata={"description": "是否启用", "required": False},
    )


class SandboxAdapter(sdk.BaseAdapter):
    _platform = "sandbox"
    ConfigClass = SandboxConfig

    # ==================== Api DSL（最小集） ====================

    class Api(sdk.BaseAdapter.Api):
        """Sandbox 标准 API 动作实现（最小集）"""

        async def get_self_info(self) -> dict:
            ad = self._adapter
            return ad.make_response(
                data={"user_id": str(getattr(ad.config, "self_id", "")), "user_name": "sandbox"}
            )

        async def get_status(self) -> dict:
            ad = self._adapter
            bots = [{
                "self": {"platform": ad.platform, "user_id": str(getattr(ad.config, "self_id", ""))},
                "online": ad._running,
            }]
            return ad.make_response(data={"good": bots[0]["online"], "bots": bots})

        async def get_version(self) -> dict:
            from . import __version__

            return self._adapter.make_response(
                data={"impl": "ErisPulse-SandboxAdapter", "version": __version__, "onebot_version": "12"}
            )

        async def get_supported_actions(self) -> dict:
            actions = {"get_self_info", "get_status", "get_version", "get_supported_actions"}
            return self._adapter.make_response(data=sorted(actions))

    class Send(sdk.BaseAdapter.Send):
        def Text(self, text: str):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="text",
                    content=text,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Image(self, file: str, summary: str = None):
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
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Face(self, face_id: int):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="face",
                    content=str(face_id),
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Recall(self, message_id: str):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="recall",
                    content=f"撤回消息 {message_id}",
                )
            )
            self._reset_modifiers()
            return task

        def Raw_ob12(self, message, **kwargs):
            # node 段解析：纯 node 列表自动路由合并转发；混合列表降级为纯文本
            if isinstance(message, dict) and message.get("type") == "node":
                message = [message]
            if isinstance(message, list) and message and all(
                isinstance(seg, dict) and seg.get("type") == "node" for seg in message
            ):
                return asyncio.create_task(
                    self._do_send_merge_forward([seg for seg in message])
                )
            if isinstance(message, list):
                message = [
                    {"type": "text", "data": {"text": _forward_nodes_plain(seg)}}
                    if isinstance(seg, dict) and seg.get("type") == "node"
                    else seg
                    for seg in message
                ]

            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="raw_ob12",
                    content=message,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Json(self, json_data: str):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="json",
                    content=json_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Xml(self, xml_data: str):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="xml",
                    content=xml_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Music(self, platform: str, id: str, title: str = None):
            music_data = {
                "type": "custom",
                "url": f"https://music.163.com/song/media/outer/url?id={id}.mp3",
                "audio": f"https://music.163.com/song/media/outer/url?id={id}.mp3",
                "title": title or f"音乐 {id}",
                "image": "https://webstatic.mihoyo.com/upload/static-resource/2022/02/23/6c7839055a7b6e3d8d8d8d8d8d8d8d_6966302954083748595.png",
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
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Record(self, file: str, magic: bool = False):
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
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Voice(self, file: str):
            return self.Record(file)

        def Video(self, file: str):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="video",
                    content=file,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Html(self, html_data: str):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="html",
                    content=html_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def MergeForward(self, nodes, title: str = "合并聊天记录"):
            """发送合并转发消息（渲染为折叠 HTML 卡片，html 通道发出）

            :param nodes: go-cqhttp 扩展的 OneBot v11 合并转发节点数组（或单节点 dict）
            :param title: 折叠卡标题
            :return: asyncio.Task
            """
            if isinstance(nodes, dict):
                nodes = [nodes]
            return asyncio.create_task(
                self._do_send_merge_forward(
                    [n for n in nodes if isinstance(n, dict)], title
                )
            )

        async def _do_send_merge_forward(self, nodes, title: str = "合并聊天记录"):
            html = _build_forward_html(nodes, title)
            if not html:
                return self._adapter.make_error(
                    retcode=10006, message="MergeForward: 节点无有效文本内容"
                )
            result = await self._adapter.call_api(
                endpoint="send_msg",
                target_type=self._target_type,
                target_id=self._target_id,
                message_type="html",
                content=html,
                at_user_ids=self._at_user_ids,
                at_all=self._at_all,
                reply_message_id=self._reply_message_id,
            )
            self._reset_modifiers()
            return result

        def Markdown(self, markdown_data: str):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="markdown",
                    content=markdown_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Dice(self):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="dice",
                    content="",
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Rps(self):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="rps",
                    content="",
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Location(
            self, lat: float, lon: float, title: str = None, content: str = None
        ):
            location_data = {
                "lat": lat,
                "lon": lon,
                "title": title or "",
                "content": content or "",
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
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Poke(self, user_id: str, type: str = "poke"):
            poke_data = {"user_id": user_id, "type": type}
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="poke",
                    content=poke_data,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def Share(self, url: str, title: str, content: str = None, image: str = None):
            share_data = {
                "url": url,
                "title": title,
                "content": content or title,
                "image": image or "",
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
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def File(self, file: str):
            task = asyncio.create_task(
                self._adapter.call_api(
                    endpoint="send_msg",
                    target_type=self._target_type,
                    target_id=self._target_id,
                    message_type="file",
                    content=file,
                    at_user_ids=self._at_user_ids,
                    at_all=self._at_all,
                    reply_message_id=self._reply_message_id,
                )
            )
            self._reset_modifiers()
            return task

        def _reset_modifiers(self):
            self._at_user_ids = []
            self._reply_message_id = None
            self._at_all = False

    def __init__(self, sdk):
        super().__init__(sdk)
        self.storage = sdk.storage

        self.self_id = self.config.self_id

        self.user_messages: Dict[str, List[Dict]] = {}
        self.groups: Dict[str, Dict] = {}
        self.group_messages: Dict[str, List[Dict]] = {}
        self._web_connections: List[WebSocket] = []

        self.convert = self._setup_converter()
        self._load_persisted_data()

    def _setup_converter(self):
        from .Converter import SandboxConverter

        converter = SandboxConverter(self.self_id)
        return converter.convert

    def _load_persisted_data(self):
        try:
            persisted_messages = self.storage.get("sandbox:user_messages", {})
            if persisted_messages:
                self.user_messages = self._clean_for_serialization(persisted_messages)
                total_messages = sum(len(msgs) for msgs in self.user_messages.values())
                self.logger.info(
                    f"从存储加载了 {total_messages} 条消息，共 {len(self.user_messages)} 个用户"
                )
        except Exception as e:
            self.logger.warning(f"加载用户消息数据失败: {e}")

        try:
            persisted_groups = self.storage.get("sandbox:groups", {})
            if persisted_groups:
                self.groups = self._clean_for_serialization(persisted_groups)
                self.logger.info(f"从存储加载了 {len(self.groups)} 个群组")
        except Exception as e:
            self.logger.warning(f"加载群组数据失败: {e}")

        try:
            persisted_group_messages = self.storage.get("sandbox:group_messages", {})
            if persisted_group_messages:
                self.group_messages = self._clean_for_serialization(
                    persisted_group_messages
                )
                total_group_msgs = sum(
                    len(msgs) for msgs in self.group_messages.values()
                )
                self.logger.info(
                    f"从存储加载了 {total_group_msgs} 条群组消息，共 {len(self.group_messages)} 个群组"
                )
        except Exception as e:
            self.logger.warning(f"加载群组消息数据失败: {e}")

    def _clean_for_serialization(self, data):
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, bytes):
            try:
                return data.decode("utf-8")
            except UnicodeDecodeError:
                import base64

                try:
                    return base64.b64encode(data).decode("utf-8")
                except Exception:
                    return ""
        elif isinstance(data, dict):
            return {
                key: self._clean_for_serialization(value) for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._clean_for_serialization(item) for item in data]
        else:
            return str(data)

    def _save_persisted_data(self):
        try:
            messages_to_save = {}
            for user_id, msgs in self.user_messages.items():
                messages_to_save[user_id] = msgs[-1000:] if len(msgs) > 1000 else msgs

            messages_to_save = self._clean_for_serialization(messages_to_save)
            self.storage.set("sandbox:user_messages", messages_to_save)

            total_messages = sum(len(msgs) for msgs in messages_to_save.values())
            self.logger.debug(f"保存了 {total_messages} 条消息")

            groups_to_save = self._clean_for_serialization(self.groups)
            self.storage.set("sandbox:groups", groups_to_save)

            group_messages_to_save = {}
            for group_id, msgs in self.group_messages.items():
                group_messages_to_save[group_id] = (
                    msgs[-1000:] if len(msgs) > 1000 else msgs
                )
            group_messages_to_save = self._clean_for_serialization(
                group_messages_to_save
            )
            self.storage.set("sandbox:group_messages", group_messages_to_save)
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            import traceback

            self.logger.error(f"详细错误: {traceback.format_exc()}")

    async def call_api(self, endpoint: str, **params):
        if endpoint == "get_commands":
            return await self._handle_get_commands()

        elif endpoint == "send_msg":
            target_type = params.get("target_type", "user")
            target_id = params.get("target_id", "")
            message_type = params.get("message_type", "text")
            content = params.get("content", "")

            at_user_ids = params.get("at_user_ids", [])
            at_all = params.get("at_all", False)
            reply_message_id = params.get("reply_message_id", None)

            message_segments = self._build_message_segments(
                message_type, content, at_user_ids, at_all, reply_message_id
            )

            chat_type = "group" if target_type == "group" else "private"

            message = {
                "type": "message",
                "message_type": chat_type,
                "user_id": self.self_id,
                "user_name": "机器人",
                "target_id": target_id,
                "message": content,
                "message_type_detail": message_type,
                "message_segments": message_segments,
                "timestamp": int(time.time()),
            }

            if chat_type == "group":
                message["group_id"] = target_id
                group_info = self.groups.get(target_id, {})
                message["group_name"] = group_info.get("group_name", "")

            message = self._clean_for_serialization(message)

            if chat_type == "group":
                if target_id not in self.group_messages:
                    self.group_messages[target_id] = []
                self.group_messages[target_id].append(message)
            else:
                if target_id not in self.user_messages:
                    self.user_messages[target_id] = []
                self.user_messages[target_id].append(message)

            self._save_persisted_data()

            await self._broadcast_to_web(
                {
                    "type": "message",
                    "data": message,
                }
            )

            if chat_type == "group":
                msg_index = len(self.group_messages.get(target_id, []))
            else:
                msg_index = len(self.user_messages.get(target_id, []))

            return self.make_response(
                data={"message_id": str(msg_index)},
                message_id=str(msg_index),
            )

        return self.make_error(retcode=10002, message="未知的API端点")

    def _build_message_segments(
        self, message_type, content, at_user_ids, at_all, reply_message_id
    ):
        message_segments = []

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
        elif message_type == "file":
            message_segments = [{"type": "file", "data": {"file": content}}]
        elif message_type == "dice":
            dice_value = random.randint(1, 6)
            message_segments = [{"type": "dice", "data": {"result": str(dice_value)}}]
        elif message_type == "rps":
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

        final_segments = []

        if reply_message_id:
            final_segments.append(
                {
                    "type": "reply",
                    "data": {"message_id": reply_message_id},
                }
            )
            final_segments.append(
                {
                    "type": "text",
                    "data": {"text": " "},
                }
            )

        if at_all:
            final_segments.append(
                {
                    "type": "mention_all",
                    "data": {},
                }
            )
            final_segments.append(
                {
                    "type": "text",
                    "data": {"text": " "},
                }
            )

        for user_id in at_user_ids:
            final_segments.append(
                {
                    "type": "mention",
                    "data": {"user_id": user_id},
                }
            )
            final_segments.append(
                {
                    "type": "text",
                    "data": {"text": " "},
                }
            )

        final_segments.extend(message_segments)

        return final_segments

    async def _broadcast_to_web(self, data: Dict):
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
        self._web_connections.append(websocket)
        self.logger.info("网页客户端已连接")

        await self.emit_meta(
            "connect", self.self_id, user_name="SandboxBot", nickname="沙箱机器人"
        )

        initial_data = {
            "type": "init",
            "data": {
                "self_id": self.self_id,
            },
        }
        cleaned_data = self._clean_for_serialization(initial_data)
        await websocket.send_text(json.dumps(cleaned_data, ensure_ascii=False))

        heartbeat_task = spawn_background(self._heartbeat_loop()) if spawn_background is not None else asyncio.create_task(self._heartbeat_loop())

        try:
            while True:
                data = await websocket.receive_text()
                self.logger.debug(f"[Sandbox] 收到WebSocket消息: {data[:200]}")
                asyncio.create_task(self._handle_web_message_safe(data))
                self.logger.debug("[Sandbox] 已创建消息处理任务")
        except WebSocketDisconnect:
            self.logger.info("网页客户端断开连接")
        except Exception as e:
            self.logger.error(f"WebSocket 处理异常: {e}")
            import traceback

            self.logger.error(f"详细错误: {traceback.format_exc()}")
        finally:
            heartbeat_task.cancel()
            if websocket in self._web_connections:
                self._web_connections.remove(websocket)
            await self.emit_meta("disconnect", self.self_id)

    async def _heartbeat_loop(self):
        try:
            while True:
                await asyncio.sleep(30)
                await self.emit_meta("heartbeat", self.self_id)
        except asyncio.CancelledError:
            pass

    async def _handle_web_message_safe(self, raw_msg: str):
        try:
            await self._handle_web_message(raw_msg)
        except Exception as e:
            self.logger.error(f"[Sandbox] 后台消息处理任务异常: {e}")
            import traceback

            self.logger.error(f"详细错误: {traceback.format_exc()}")

    async def _handle_web_message(self, raw_msg: str):
        try:
            data = json.loads(raw_msg)
            msg_type = data.get("type")
            self.logger.info(f"[Sandbox] 处理消息类型: {msg_type}")

            if msg_type == "send_message":
                await self._handle_send_message(data.get("data", {}))
            elif msg_type == "load_messages":
                await self._handle_load_messages(data.get("data", {}))
            elif msg_type == "call_api":
                await self._handle_call_api(data.get("data", {}))
            elif msg_type == "create_group":
                await self._handle_create_group(data.get("data", {}))
            elif msg_type == "manage_group":
                await self._handle_manage_group(data.get("data", {}))

            self.logger.info(f"[Sandbox] 消息类型 {msg_type} 处理完成")
        except json.JSONDecodeError:
            self.logger.error(f"JSON 解析失败: {raw_msg}")
        except Exception as e:
            self.logger.error(f"处理网页消息异常: {e}")
            import traceback

            self.logger.error(f"详细错误: {traceback.format_exc()}")

    async def _handle_send_message(self, message_data: Dict):
        user_id = message_data.get("user_id", "")
        user_name = message_data.get("user_name", "")
        message_type = message_data.get("message_type", "private")

        self.logger.info(
            f"[Sandbox] _handle_send_message 开始, user={user_name}({user_id}), type={message_type}"
        )

        raw_event = {
            "type": "message",
            "message_type": message_type,
            "user_id": user_id,
            "user_name": user_name,
            "message": message_data.get("message", ""),
            "message_type_detail": message_data.get("message_type_detail", "text"),
            "message_segments": message_data.get("message_segments", []),
            "target_id": self.self_id,
            "timestamp": int(time.time()),
        }

        if message_type == "group":
            group_id = message_data.get("group_id", "")
            group_name = message_data.get("group_name", "")
            raw_event["group_id"] = group_id
            raw_event["group_name"] = group_name
            raw_event["target_id"] = group_id

            if group_id not in self.group_messages:
                self.group_messages[group_id] = []
            self.group_messages[group_id].append(raw_event)
        else:
            if user_id not in self.user_messages:
                self.user_messages[user_id] = []
            self.user_messages[user_id].append(raw_event)

        self._save_persisted_data()

        onebot_event = self.convert(raw_event)

        if onebot_event:
            self.logger.info(
                f"[Sandbox] 开始 emit 事件到模块系统: {message_data.get('message', '')[:50]}"
            )
            try:
                await asyncio.wait_for(
                    self.sdk.adapter.emit(onebot_event), timeout=30.0
                )
                self.logger.info(f"[Sandbox] emit 完成")
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                self.logger.error(f"[Sandbox] emit 异常: {e}", exc_info=True)
        else:
            self.logger.warning(f"[Sandbox] convert 返回 None, 跳过 emit")

    async def _handle_load_messages(self, load_data: Dict):
        contact_id = load_data.get("contact_id", "")
        contact_type = load_data.get("contact_type", "private")

        if contact_type == "group":
            messages = self.group_messages.get(contact_id, [])
        else:
            messages = self.user_messages.get(contact_id, [])

        await self._broadcast_to_web(
            {
                "type": "messages_loaded",
                "data": {
                    "contact_id": contact_id,
                    "contact_type": contact_type,
                    "messages": messages,
                },
            }
        )

    async def _handle_get_commands(self):
        try:
            from ErisPulse.Core.Event import command as command_handler

            commands_dict = command_handler.get_visible_commands()

            commands_list = []
            for cmd_name, cmd_info in commands_dict.items():
                cmd_data = {
                    "name": cmd_name,
                    "help": cmd_info.get("help", ""),
                    "usage": cmd_info.get("usage", ""),
                    "group": cmd_info.get("group", ""),
                    "hidden": cmd_info.get("hidden", False),
                }

                aliases = [
                    alias
                    for alias, main_name in command_handler.aliases.items()
                    if main_name == cmd_name
                ]
                if aliases:
                    cmd_data["aliases"] = aliases

                commands_list.append(cmd_data)

            # prefix 可能是字符串或列表，统一返回主前缀和全部前缀
            raw_prefix = command_handler.prefix
            if isinstance(raw_prefix, list):
                all_prefixes = [str(p) for p in raw_prefix] if raw_prefix else ["/"]
                main_prefix = all_prefixes[0]
            else:
                all_prefixes = [str(raw_prefix)]
                main_prefix = str(raw_prefix)

            return self.make_response(
                data={
                    "prefix": main_prefix,
                    "prefixes": all_prefixes,
                    "commands": commands_list,
                    "total": len(commands_list),
                },
                message=f"获取了 {len(commands_list)} 个命令",
            )
        except ImportError:
            self.logger.warning("命令处理器模块未找到")
            return self.make_response(
                data={
                    "prefix": "/",
                    "commands": [],
                    "total": 0,
                },
                message="命令系统未启用",
            )
        except Exception as e:
            self.logger.error(f"获取命令列表失败: {e}")
            return self.make_error(
                retcode=-1,
                message=f"获取命令列表失败: {str(e)}",
            )

    async def _handle_call_api(self, api_data: Dict):
        endpoint = api_data.get("endpoint", "")

        if not endpoint:
            await self._broadcast_to_web(
                {
                    "type": "api_response",
                    "data": self.make_error(retcode=-1, message="缺少 endpoint 参数"),
                }
            )
            return

        try:
            result = await self.call_api(
                endpoint, **{k: v for k, v in api_data.items() if k != "endpoint"}
            )

            await self._broadcast_to_web(
                {
                    "type": "api_response",
                    "data": result,
                }
            )
        except Exception as e:
            self.logger.error(f"API 调用失败: {e}")
            await self._broadcast_to_web(
                {
                    "type": "api_response",
                    "data": self.make_error(
                        retcode=-1, message=f"API 调用失败: {str(e)}"
                    ),
                }
            )

    async def _handle_create_group(self, group_data: Dict):
        group_name = group_data.get("group_name", "未命名群组")
        members = group_data.get("members", [])

        group_id = f"g_{int(time.time())}_{uuid.uuid4().hex[:6]}"

        group_info = {
            "group_id": group_id,
            "group_name": group_name,
            "members": members,
            "created_at": int(time.time()),
        }

        self.groups[group_id] = group_info
        self._save_persisted_data()

        self.logger.info(
            f"[Sandbox] 创建群组: {group_name} ({group_id}), 成员: {members}"
        )

        await self._broadcast_to_web(
            {
                "type": "group_created",
                "data": group_info,
            }
        )

    async def _handle_manage_group(self, manage_data: Dict):
        action = manage_data.get("action", "")
        group_id = manage_data.get("group_id", "")
        user_id = manage_data.get("user_id", "")
        user_name = manage_data.get("user_name", "")

        if group_id not in self.groups:
            await self._broadcast_to_web(
                {
                    "type": "error",
                    "data": {"message": f"群组不存在: {group_id}"},
                }
            )
            return

        group_info = self.groups[group_id]

        if action == "add_member":
            if user_id not in group_info["members"]:
                group_info["members"].append(user_id)
                self._save_persisted_data()

                notice_event = {
                    "type": "notice",
                    "notice_type": "group_member_increase",
                    "group_id": group_id,
                    "group_name": group_info["group_name"],
                    "user_id": user_id,
                    "user_name": user_name,
                    "operator_id": self.self_id,
                }
                onebot_event = self.convert(notice_event)
                if onebot_event:
                    await self.sdk.adapter.emit(onebot_event)

                self.logger.info(
                    f"[Sandbox] 用户 {user_name}({user_id}) 加入群组 {group_info['group_name']}({group_id})"
                )

        elif action == "remove_member":
            if user_id in group_info["members"]:
                group_info["members"].remove(user_id)
                self._save_persisted_data()

                notice_event = {
                    "type": "notice",
                    "notice_type": "group_member_decrease",
                    "group_id": group_id,
                    "group_name": group_info["group_name"],
                    "user_id": user_id,
                    "user_name": user_name,
                    "operator_id": self.self_id,
                }
                onebot_event = self.convert(notice_event)
                if onebot_event:
                    await self.sdk.adapter.emit(onebot_event)

                self.logger.info(
                    f"[Sandbox] 用户 {user_name}({user_id}) 离开群组 {group_info['group_name']}({group_id})"
                )

        await self._broadcast_to_web(
            {
                "type": "group_updated",
                "data": self.groups[group_id],
            }
        )

    async def register_routes(self):
        router.register_websocket(
            "sandbox",
            "/ws",
            self._web_ws_handler,
        )

        async def serve_index():
            html_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
            try:
                with open(html_file, "r", encoding="utf-8") as f:
                    html_content = f.read()
                from fastapi.responses import HTMLResponse

                return HTMLResponse(content=html_content, status_code=200)
            except Exception as e:
                self.logger.error(f"读取 HTML 文件失败: {e}")
                from fastapi.responses import HTMLResponse

                return HTMLResponse(
                    content=f"<h1>Error</h1><p>{str(e)}</p>", status_code=500
                )

        router.register_http_route(
            "sandbox",
            "/",
            serve_index,
            methods=["GET"],
        )

        self.logger.info("沙箱适配器路由已注册")

    def _is_dashboard_available(self):
        try:
            return "Dashboard" in self.sdk.module._loaded_modules
        except Exception:
            return False

    def _try_register_dashboard_view(self):
        if not self._is_dashboard_available():
            return False
        try:
            dashboard = self.sdk.Dashboard
            dashboard.register_view(
                id="Sandbox",
                title="沙箱",
                title_en="Sandbox",
                icon_svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>',
                iframe_url="/sandbox/",
                group="group_tools",
            )
            self.logger.info("已注册 Dashboard 沙箱视窗")
            return True
        except Exception as e:
            self.logger.warning(f"Dashboard 视窗注册失败: {e}")
            return False

    def _setup_dashboard_view_registration(self):
        if self._try_register_dashboard_view():
            return

        async def _on_module_load(data):
            if (
                isinstance(data, dict)
                and data.get("module_name") == "Dashboard"
                and data.get("success")
            ):
                self._try_register_dashboard_view()
                self.sdk.lifecycle.unregister("module.load", _on_module_load)

        async def _on_init_complete(data):
            self._try_register_dashboard_view()
            self.sdk.lifecycle.unregister("core.init.complete", _on_init_complete)

        self.sdk.lifecycle.register("module.load", _on_module_load)
        self.sdk.lifecycle.register("core.init.complete", _on_init_complete)

    def _unregister_dashboard_view(self):
        if not self._is_dashboard_available():
            return
        try:
            self.sdk.Dashboard.unregister_view("Sandbox")
        except Exception:
            pass

    async def start(self):
        self.logger.info("正在启动沙箱适配器...")

        await self.register_routes()
        self._setup_dashboard_view_registration()

        server_config = self.sdk.config.getConfig("ErisPulse.server", {})
        host = server_config.get("host", "0.0.0.0")
        port = server_config.get("port", 8000)

        self.logger.info("沙箱适配器启动完成")
        self.logger.info(
            f"访问地址: http://{'localhost' if host == '0.0.0.0' else host}:{port}/sandbox/"
        )

    async def shutdown(self):
        self.logger.info("正在关闭沙箱适配器...")

        self._unregister_dashboard_view()

        router.unregister_websocket("sandbox", "/ws")
        router.unregister_http_route("sandbox", "/")

        for ws in self._web_connections:
            try:
                await ws.close()
            except Exception as e:
                self.logger.warning(f"关闭 WebSocket 连接失败: {e}")

        self._web_connections.clear()
        self.logger.info("沙箱适配器已关闭")
