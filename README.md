# dual_llm_wrapper

指定したプロンプトを OpenAI と Azure OpenAI の 2 つの LLM に送信する Python ラッパーです。

## 実行方法

`.env` またはシェルの環境変数に API キーを設定してから実行します。既存の `.env` はそのまま利用できます。

```bash
python main.py
```

実行時は [prompt/ses_industry_analysis.md](prompt/ses_industry_analysis.md) を読み込みます。OpenAI 側のモデルは `OPENAI_MODEL` で変更できます。2 つの LLM の結果を表示した後、OpenAI が Judge として比較し、より優れた回答を表示します。全結果は `logs/results.log` に追記されます。
