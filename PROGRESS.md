# AI VTuber (Open-LLM-VTuber) 進捗

最終更新: 2026-09-13

## 経緯

海外で話題のAI活用を日本で再現する企画の一環。過去に複数回、環境構築地獄で挫折している
プロジェクト。今回はClaude Codeが実際にBashで手を動かしてセットアップを巻き取り、
LLM単体→TTS→ASR→Live2D、の順で一段ずつ「動く状態」を確認しながら進めた。

## 今の状態（全部動作確認済み）

- **リポジトリ**: このフォルダ（`Open-LLM-VTuber`、GitHubからclone、uv管理）
- **テキスト会話**: Gemini 3.7 Flash（無料枠、`conf.yaml`にAPIキー設定済み）
- **音声合成**: VOICEVOX「冥鳴ひまり」/「ノーマル」、`speed_scale: 1.2`
- **Live2Dアバター**: デフォルトキャラ「mao_pro」、表情連動も動作
- **ASR（マイク入力）**: 動作はしている。ただしデフォルトでマイク常時ONになっており、
  周囲の雑談を拾って誤動作しやすい（次にやる作業）

## 再開手順

1. VOICEVOX ENGINEを起動（別プロセス、必須）
   ```bash
   cd /Users/kato/Public/claude_git/voicevox-engine/macos-arm64
   ./run --host 127.0.0.1 --port 50021
   ```
2. Open-LLM-VTuberサーバーを起動
   ```bash
   cd /Users/kato/Public/claude_git/ai-vtuber
   uv run run_server.py
   ```
3. ブラウザで `http://localhost:12393` を開く
4. 起動直後はマイクがONになっているので、雑音を拾いたくない場合は先にミュートボタンを押す

## 技術的な詰まりポイント（次回同じ罠を踏まないためのメモ）

- **Python 3.13だと動かない**。`requires-python = ">=3.10,<3.13"`。`uv sync`が自動で
  Python 3.10を用意してくれるので、素の`pip install`ではなく必ず`uv`を使うこと
- **Anthropic・Geminiどちらも通常はAPI課金（クレジットカード登録）が必要**。今回は
  Gemini側の無料枠モデルで進めている。Gemini API利用にはGoogle AI Proサブスクの
  クレジットは含まれない（別会計）
- `gemini-3.1-flash-live-preview`のような「-live-」系モデルは`bidiGenerateContent`
  （WebSocket専用）が必須で、Open-LLM-VTuberが使う通常の`generateContent`方式では
  動かない。配信用に本格導入するなら別途自前でWebSocket連携が必要（未着手）
- `agent_settings.basic_memory_agent.use_mcpp: True`＋`mcp_enabled_servers: ["time", "ddg-search"]`
  がデフォルト有効だが、ddg-searchのMCPサーバーが実際には起動していないため
  **応答がハングする不具合**があった。`use_mcpp: False`にして回避（今もFalseのまま）
- VOICEVOXはOpen-LLM-VTuberにネイティブ対応が無いため自作。追加/変更したファイル：
  - `src/open_llm_vtuber/tts/voicevox_tts.py`（新規）
  - `src/open_llm_vtuber/tts/tts_factory.py`（`voicevox_tts`分岐を追加）
  - `src/open_llm_vtuber/config_manager/tts.py`（`VoicevoxTTSConfig`クラスを追加）
  - `conf.yaml`の`tts_config`に`voicevox_tts`ブロックを追加
- VOICEVOX ENGINE本体はGitHub公式リリースの「エンジン本体（.7z.001）」を使用
  （「プラグインエンジン（.vvpp）」はVOICEVOXエディタアプリ用なので不可）。
  解凍に`brew install sevenzip`が必要だった

## 次にやること

1. ASRの誤検知対策（感度・閾値調整、または明示的なプッシュトゥトーク運用の検討）
2. Live2Dモデルのカスタマイズ（デフォルトの「mao_pro」から差し替えるか検討）
3. （やるなら後回し）配信用途でのGemini Live API本格対応
