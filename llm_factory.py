"""LLM の接続情報と OpenAI 互換 API 呼び出しを管理する。"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class LLMConnection:
    name: str
    url: str
    api_key: str
    model: str


def load_dotenv(path: Path = Path(".env")) -> None:
    """未設定の環境変数だけ .env から読み込む。"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"\''))


def create_openai_connection() -> LLMConnection | None:
    """OpenAI 用の接続を生成する。設定がなければ None を返す。"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return LLMConnection(
        name="OpenAI",
        url="https://api.openai.com/v1/chat/completions",
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    )


def create_azure_openai_connection() -> LLMConnection | None:
    """Azure OpenAI 用の接続を生成する。設定がなければ None を返す。"""
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    if not api_key or not endpoint or not deployment:
        return None
    return LLMConnection(
        name="Azure OpenAI",
        url=endpoint.rstrip("/") + "/chat/completions",
        api_key=api_key,
        model=deployment,
    )


def call_chat_api(connection: LLMConnection, prompt: str) -> tuple[str, str]:
    """指定された接続で OpenAI 互換の Chat Completions API を呼び出す。"""
    payload = {
        "model": connection.model,
        "messages": [
            {"role": "system", "content": "専門家として、根拠と具体例を示して回答してください。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
    }
    request = Request(
        connection.url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {connection.api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
        return connection.name, result["choices"][0]["message"]["content"]
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as error:
        return connection.name, f"実行に失敗しました: {error}"