import asyncio
import json
import time
from typing import Any, Dict, List, Optional
from urllib import parse, request
from urllib.error import HTTPError, URLError

from ..config import settings


class WeChatMPError(Exception):
    pass


class WeChatMPService:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._token_expires_at = 0.0

    def is_enabled(self) -> bool:
        return bool(
            settings.WECHAT_MP_ENABLED
            and settings.WECHAT_MP_APP_ID
            and settings.WECHAT_MP_APP_SECRET
            and settings.WECHAT_MP_TEMPLATE_ID
            and (self.get_openids() or self.get_user_openid_map())
        )

    def get_openids(self) -> List[str]:
        return [
            openid.strip()
            for openid in settings.WECHAT_MP_TO_USER_OPENIDS.split(",")
            if openid.strip()
        ]

    def get_user_openid_map(self) -> Dict[str, List[str]]:
        mapping: Dict[str, List[str]] = {}
        for item in settings.WECHAT_MP_USER_OPENIDS.split(","):
            if ":" not in item:
                continue
            username, openids_text = item.split(":", 1)
            username = username.strip()
            openids = [openid.strip() for openid in openids_text.split("|") if openid.strip()]
            if username and openids:
                mapping[username] = openids
        return mapping

    def get_openids_for_user(self, username: Optional[str] = None) -> List[str]:
        if username:
            openids = self.get_user_openid_map().get(username)
            if openids:
                return openids
        return self.get_openids()

    async def send_alarm(
        self,
        *,
        title: str,
        content: str,
        device_name: str,
        variable_name: str,
        value: Any,
        alarm_message: str,
        username: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        openids = self.get_openids_for_user(username)
        if not self.is_enabled() or not openids:
            return []

        return await asyncio.to_thread(
            self._send_alarm_sync,
            openids,
            title,
            content,
            device_name,
            variable_name,
            value,
            alarm_message,
        )

    def _send_alarm_sync(
        self,
        openids: List[str],
        title: str,
        content: str,
        device_name: str,
        variable_name: str,
        value: Any,
        alarm_message: str,
    ) -> List[Dict[str, Any]]:
        token = self._get_access_token()
        results = []
        for openid in openids:
            payload = {
                "touser": openid,
                "template_id": settings.WECHAT_MP_TEMPLATE_ID,
                "url": settings.WECHAT_MP_TEMPLATE_URL,
                "data": {
                    "first": {"value": title},
                    "keyword1": {"value": device_name},
                    "keyword2": {"value": variable_name},
                    "keyword3": {"value": str(value)},
                    "keyword4": {"value": alarm_message},
                    "remark": {"value": content},
                },
            }
            results.append(self._post_template_message(token, payload))
        return results

    def _get_access_token(self) -> str:
        now = time.time()
        if self._access_token and now < self._token_expires_at:
            return self._access_token

        query = parse.urlencode(
            {
                "grant_type": "client_credential",
                "appid": settings.WECHAT_MP_APP_ID,
                "secret": settings.WECHAT_MP_APP_SECRET,
            }
        )
        url = f"https://api.weixin.qq.com/cgi-bin/token?{query}"
        data = self._request_json(url)
        access_token = data.get("access_token")
        if not access_token:
            raise WeChatMPError(f"WeChat access token failed: {data}")

        expires_in = int(data.get("expires_in") or 7200)
        self._access_token = access_token
        self._token_expires_at = now + max(expires_in - 300, 60)
        return access_token

    def _post_template_message(self, access_token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = parse.urlencode({"access_token": access_token})
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?{query}"
        data = self._request_json(url, payload)
        if data.get("errcode") not in (None, 0):
            raise WeChatMPError(f"WeChat template message failed: {data}")
        return data

    def _request_json(self, url: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        body = None
        headers = {}
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = request.Request(url, data=body, headers=headers, method="POST" if body else "GET")
        try:
            with request.urlopen(req, timeout=settings.WECHAT_MP_TIMEOUT_SECONDS) as response:
                response_body = response.read().decode("utf-8")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise WeChatMPError(f"WeChat request failed: {exc}") from exc

        try:
            return json.loads(response_body)
        except ValueError as exc:
            raise WeChatMPError(f"WeChat response is not JSON: {response_body}") from exc


wechat_mp_service = WeChatMPService()
