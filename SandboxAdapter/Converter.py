import time
import uuid
from typing import Dict, Optional

class SandboxConverter:
    """沙箱事件转换器，将虚拟消息转换为 OneBot12 标准事件"""
    
    def __init__(self, self_id: str):
        self.self_id = self_id
    
    def convert(self, raw_event: Dict) -> Optional[Dict]:
        """
        将沙箱事件转换为 OneBot12 格式
        
        :param raw_event: 原始沙箱事件数据
        :return: 转换后的 OneBot12 事件
        """
        if not isinstance(raw_event, dict):
            raise ValueError("事件数据必须是字典类型")
        
        event_type = raw_event.get("type")
        if not event_type:
            return None
        
        # 基础事件结构
        onebot_event = {
            "id": str(uuid.uuid4()),
            "time": int(time.time()),
            "platform": "sandbox",
            "self": {
                "platform": "sandbox",
                "user_id": self.self_id
            },
            "sandbox_raw": raw_event
        }
        
        # 根据事件类型分发处理
        handler = getattr(self, f"_handle_{event_type}", None)
        if handler:
            event_converted = handler(raw_event, onebot_event)
            from ErisPulse.Core import logger
            logger.debug(f"沙盒事件: {event_converted}")
            return event_converted
        
        return None
    
    def _handle_message(self, raw_event: Dict, base_event: Dict) -> Dict:
        """处理消息事件"""
        message_type = raw_event.get("message_type", "private")
        detail_type = "private" if message_type == "private" else "group"

        # 解析消息内容
        message = raw_event.get("message", "")

        # 优先使用消息段数组（如果存在）
        if "message_segments" in raw_event:
            message_segments = raw_event.get("message_segments", [])
            # 确保消息段是可序列化的
            message_segments = self._clean_message_segments(message_segments)
        else:
            # 否则创建文本消息段
            message_segments = [{"type": "text", "data": {"text": str(message)}}]

        base_event.update({
            "type": "message",
            "detail_type": detail_type,
            "message_id": str(uuid.uuid4()),
            "message": message_segments,
            "alt_message": str(message),
            "user_id": str(raw_event.get("user_id", "")),
        })

        # 添加发送者信息
        if "user_name" in raw_event:
            base_event["user_nickname"] = str(raw_event["user_name"])

        # 群聊消息
        if detail_type == "group":
            base_event["group_id"] = str(raw_event.get("group_id", ""))
            if "group_name" in raw_event:
                base_event["group_name"] = str(raw_event["group_name"])

        return base_event

    def _clean_message_segments(self, segments):
        """清理消息段，确保所有数据都是可序列化的"""
        if not isinstance(segments, list):
            return []

        cleaned_segments = []
        for segment in segments:
            if not isinstance(segment, dict):
                continue

            segment_type = segment.get("type", "text")
            segment_data = segment.get("data", {})

            # 确保data是字典类型
            if not isinstance(segment_data, dict):
                segment_data = {}

            # 清理数据中的所有值
            cleaned_data = {}
            for key, value in segment_data.items():
                if isinstance(value, bytes):
                    # 媒体文件字段需要转换为base64
                    if segment_type in ['image', 'video', 'record'] and key == 'file':
                        import base64
                        try:
                            cleaned_data[key] = base64.b64encode(value).decode('utf-8')
                        except Exception:
                            cleaned_data[key] = ''
                    else:
                        # 其他bytes字段尝试解码为UTF-8
                        try:
                            cleaned_data[key] = value.decode('utf-8')
                        except Exception:
                            cleaned_data[key] = ''
                elif isinstance(value, (str, int, float, bool, type(None))):
                    cleaned_data[key] = value
                else:
                    # 对于其他类型，转换为字符串
                    cleaned_data[key] = str(value)

            cleaned_segments.append({
                "type": str(segment_type),
                "data": cleaned_data
            })

        return cleaned_segments
    
    def _handle_notice(self, raw_event: Dict, base_event: Dict) -> Dict:
        """处理通知事件"""
        notice_type = raw_event.get("notice_type", "notify")
        
        base_event.update({
            "type": "notice",
            "detail_type": notice_type,
        })
        
        if notice_type == "group_member_increase":
            base_event.update({
                "group_id": raw_event.get("group_id", ""),
                "user_id": raw_event.get("user_id", ""),
                "operator_id": raw_event.get("operator_id", ""),
            })
        elif notice_type == "group_member_decrease":
            base_event.update({
                "group_id": raw_event.get("group_id", ""),
                "user_id": raw_event.get("user_id", ""),
                "operator_id": raw_event.get("operator_id", ""),
            })
        elif notice_type == "friend_increase":
            base_event.update({
                "user_id": raw_event.get("user_id", ""),
            })
        
        return base_event
