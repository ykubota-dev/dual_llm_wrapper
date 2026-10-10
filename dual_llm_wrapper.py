"""2 つの LLM に同じプロンプトを実行する Wrapper。"""

from __future__ import annotations

import concurrent.futures
from pathlib import Path

from llm_factory import (
    LLMConnection,
    call_chat_api,
    create_azure_openai_connection,
    create_openai_connection,
)

JUDGE_PROMPT_FILE = Path(__file__).resolve().parent / "prompt" / "judge_ses_industry_analysis.md"
JUDGE_PROMPT = JUDGE_PROMPT_FILE.read_text(encoding="utf-8")


def run_dual_llm(prompt: str) -> list[tuple[str, str]]:
    """OpenAI と Azure OpenAI に同じプロンプトを並列実行する。"""
    connections = _create_connections()
    if len(connections) != 2:
        configured = ", ".join(connection.name for connection in connections) or "なし"
        raise RuntimeError(
            f"2 つの LLM 接続が必要です。利用可能な接続: {configured}"
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(call_chat_api, connection, prompt) for connection in connections]
        return [future.result() for future in futures]



def run_dual_llm_with_judge(
    prompt: str,
) -> tuple[list[tuple[str, str]], tuple[str, str]]:
    """2つのLLMを実行し、結果をOpenAIでJudgeする。"""
    results = run_dual_llm(prompt)
    judged_result = judge_results(results)
    return results, judged_result


def judge_results(results: list[tuple[str, str]]) -> tuple[str, str]:
    """2つの回答をOpenAIで比較し、優れた回答を返す。"""
    openai_connection = create_openai_connection()
    if openai_connection is None:
        raise RuntimeError("Judge用のOpenAI接続が設定されていません。")
    if len(results) != 2:
        raise RuntimeError("Judgeには2つのLLM回答が必要です。")

    (name_a, answer_a), (name_b, answer_b) = results
    prompt = JUDGE_PROMPT.format(
        name_a=name_a,
        answer_a=answer_a,
        name_b=name_b,
        answer_b=answer_b,
    )
    _, judged_answer = call_chat_api(openai_connection, prompt)
    return "Judge（OpenAI）", judged_answer


def _create_connections() -> list[LLMConnection]:
    connections = []
    for create_connection in (create_openai_connection, create_azure_openai_connection):
        connection = create_connection()
        if connection is not None:
            connections.append(connection)
    return connections