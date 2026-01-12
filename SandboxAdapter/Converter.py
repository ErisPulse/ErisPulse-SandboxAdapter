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
        else:
            # 否则创建文本消息段
            message_segments = [{"type": "text", "data": {"text": message}}]
        
        base_event.update({
            "type": "message",
            "detail_type": detail_type,
            "message_id": str(uuid.uuid4()),
            "message": message_segments,
            "alt_message": message,
            "user_id": raw_event.get("user_id", ""),
        })
        
        # 添加发送者信息
        if "user_name" in raw_event:
            base_event["user_nickname"] = raw_event["user_name"]
        
        # 群聊消息
        if detail_type == "group":
            base_event["group_id"] = raw_event.get("group_id", "")
            if "group_name" in raw_event:
                base_event["group_name"] = raw_event["group_name"]
        
        return base_event
    
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
