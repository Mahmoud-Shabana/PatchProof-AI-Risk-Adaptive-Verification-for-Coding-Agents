from __future__ import annotations
import json
import os
import time
import urllib.request


class OpenAICompatibleProvider:
    def __init__(self):
        self.url = os.environ.get("PATCHPROOF_API_URL", "").strip()
        self.key = os.environ.get("PATCHPROOF_API_KEY", "").strip()
        self.model = os.environ.get("PATCHPROOF_MODEL", "").strip()
        self.last_usage = {}
        self.usage_totals = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        if not self.url or not self.model:
            raise RuntimeError("Set PATCHPROOF_API_URL and PATCHPROOF_MODEL.")

    def _record_usage(self, usage):
        self.last_usage = usage or {}
        for key in self.usage_totals:
            try:
                self.usage_totals[key] += int(self.last_usage.get(key, 0) or 0)
            except (TypeError, ValueError):
                pass

    def _post(self, payload):
        body = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        last_error = None
        for attempt in range(3):
            try:
                req = urllib.request.Request(self.url, data=body, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=300) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                self._record_usage(data.get("usage"))
                return data
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(2 ** attempt)
        raise RuntimeError(f"Model request failed after retries: {last_error}")

    def complete_tool(self, system, messages, tools):
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}] + messages,
            "temperature": 0,
            "tools": tools,
            "tool_choice": "auto",
        }
        data = self._post(payload)
        return data["choices"][0]["message"]

    def force_function(self, system, user, function_name, description, parameters):
        tool = {
            "type": "function",
            "function": {"name": function_name, "description": description, "parameters": parameters},
        }
        base_messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        forced = {"type": "function", "function": {"name": function_name}}
        for attempt in range(2):
            payload = {
                "model": self.model,
                "messages": base_messages,
                "temperature": 0,
                "tools": [tool],
                "tool_choice": forced,
            }
            data = self._post(payload)
            message = data["choices"][0]["message"]
            calls = message.get("tool_calls") or []
            if calls:
                fn = calls[0].get("function") or {}
                if fn.get("name") == function_name:
                    raw = fn.get("arguments") or "{}"
                    args = raw if isinstance(raw, dict) else json.loads(raw)
                    return args, message, self.last_usage
                text_content = f"[wrong function called: {fn.get('name')}]"
            else:
                text_content = message.get("content") or ""
            if attempt == 0:
                base_messages = base_messages + [
                    {"role": "assistant", "content": text_content},
                    {"role": "user", "content": f"You must now call the `{function_name}` function with the information you just provided. Do not write prose — call the function directly."},
                ]
        raise RuntimeError(f"Model did not call {function_name} after 2 attempts. Last content={text_content!r}")
