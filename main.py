"""固定プロンプトを 2 つの LLM で実行する。"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from dual_llm_wrapper import run_dual_llm_with_judge
from llm_factory import load_dotenv

PROMPT_FILE = Path(__file__).resolve().parent / "prompt" / "ses_industry_analysis.md"
LOG_FILE = Path(__file__).resolve().parent / "logs" / "results.log"

def main() -> int:
    load_dotenv()
    prompt = PROMPT_FILE.read_text(encoding="utf-8")
    try:
        results, judged_result = run_dual_llm_with_judge(prompt)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    report = [f"\n=== {datetime.now().astimezone().isoformat()} ===\n"]
    for name, output in [*results, judged_result]:
        report.append(f"# {name}\n\n{output}\n")
    report_text = "\n".join(report)

    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as log_file:
            log_file.write(report_text)
    except OSError as error:
        print(f"結果ログの保存に失敗しました: {error}", file=sys.stderr)
        return 1

    print(report_text, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())