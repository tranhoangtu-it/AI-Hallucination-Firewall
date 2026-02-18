🇺🇸 [English](README.md) | 🇻🇳 [Tiếng Việt](README.vi.md) | 🇯🇵 **[日本語](README.ja.md)** | 🇰🇷 [한국어](README.ko.md)

---

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/tranhoangtu-it/AI-Hallucination-Firewall/releases)
[![Tests](https://img.shields.io/badge/tests-210%20passed-brightgreen.svg)](#開発)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](#development)
[![GitHub Pages](https://img.shields.io/badge/docs-live-blue.svg)](https://tranhoangtu-it.github.io/AI-Hallucination-Firewall/)

<p align="center">
  <img src="img/ai-hallucination-firewall.png" alt="AI Hallucination Firewall" width="600"/>
</p>

<p align="center">
  <strong>🌐 <a href="https://tranhoangtu-it.github.io/AI-Hallucination-Firewall/">ランディングページを見る</a></strong>
</p>

# AI Hallucination Firewall

AIが生成したコードをコードベースに入る前に検証する検証プロキシ。**「AI出力の型チェッカー」**として機能 — Python、JavaScript、TypeScript で幻覚関数、非推奨の使用法、無効なパターン、間違った署名、存在しないパッケージを検出。

## 機能

- 🌳 **AST構文検証** — tree-sitter パーサーが Python、JavaScript、TypeScript の不正なコードを実行前に検出
- 📦 **インポート検証** — PyPI と npm レジストリでパッケージを検証、エイリアス解決対応（`import pandas as pd` → `pd.DataFrame()`）
- 🔍 **署名チェック** — Jedi + inspect が関数パラメータ、必須引数、キーワード引数を実際の API で検証
- 📄 **LLM出力パーサー** — マークダウンレスポンスからコードブロックを抽出し、各ブロックを独立して検証
- 🪝 **Pre-commit統合** — Python と JavaScript/TypeScript の自動 Git フック
- 🔌 **VS Code拡張機能** — リアルタイムインライン診断。保存時または変更時のトリガー設定可能
- ⚡ **並列レジストリチェック** — semaphoreベースのスロットリングを使用したPyPI/npm非同期並行ルックアップ
- 📊 **SARIFエクスポート** — `--format sarif`でGitHub Code Scanning統合
- 🚦 **CI品質ゲート** — lint/type-check/testマトリックス付きGitHub Actionsワークフロー（Python 3.11-3.13、80%カバレッジ）
- 🔒 **厳格なCIポリシー** — `--ci`フラグでネットワークエラー時の失敗と警告しきい値を強制
- 📈 **観測性メトリクス** — `/metrics`エンドポイントでレイテンシ、キャッシュヒット率、エラーカウントを公開

## 仕組み

```
Code Input → AST Parsing → Import Check → Signature Validation → Report
     │           │              │                │                  │
tree-sitter    PyPI/npm        Jedi         Rich/JSON/SARIF
 (syntax)   (async parallel) (correctness)
```

**4層検証パイプライン:**
1. **構文** — tree-sitter AST 解析が不正なコードを検出
2. **インポート** — PyPI & npm レジストリでパッケージ存在を検証
3. **署名** — 実際の API 署名で関数呼び出しを検証
4. **非推奨** — 非推奨パターンを置換提案でフラグ（将来）

## インストール

Python 3.11+ が必要です。

```bash
# クローンしてインストール
git clone https://github.com/tranhoangtu-it/AI-Hallucination-Firewall.git
cd AI-Hallucination-Firewall
pip install -e ".[dev]"
```

## クイックスタート

```bash
# ファイルを検証
firewall check app.py

# LLM マークダウンレスポンスを検証
firewall parse response.md

# CI/CD 用の JSON 出力
firewall check --format json app.py

# GitHub Code Scanning用のSARIF出力
firewall check --format sarif app.py

# 厳格なCIモード（ネットワークエラー時失敗、警告しきい値適用）
firewall check --ci app.py

# API サーバーを起動
firewall serve
```

## 使い方

### CLIコマンド

```bash
# 単一ファイルをチェック
firewall check mycode.py

# 複数ファイルをチェック
firewall check src/*.py

# stdin からパイプ
cat generated_code.py | firewall check --stdin -l python

# CIモード（ネットワークエラー時失敗、警告しきい値適用）
firewall check --ci src/*.py

# GitHub Code Scanning用のSARIF出力
firewall check --format sarif --output results.sarif src/
```

### Pre-commitフック

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/tranhoangtu-it/AI-Hallucination-Firewall
    rev: v0.1.0
    hooks:
      - id: firewall-check
      - id: firewall-check-js
```

### VS Code拡張機能

1. `vscode-extension/` に移動し、`npm install && npm run compile` を実行
2. VS Code でインストール: `Extensions: Install from VSIX`
3. `hallucinationFirewall.triggerMode` を設定: `onSave`（デフォルト）または `onChange`

### APIサーバー

```bash
# サーバーを起動
firewall serve --host 0.0.0.0 --port 8000

# API で検証
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"code": "import fakelib", "language": "python"}'

# 観測性メトリクスを表示
curl http://localhost:8000/metrics
```

### 設定

プロジェクトルートに `.firewall.toml` を作成:

```toml
[firewall]
languages = ["python", "javascript"]
severity_threshold = "warning"
cache_ttl_seconds = 3600
output_format = "terminal"

[firewall.registries]
pypi_enabled = true
npm_enabled = true
timeout_seconds = 10
```

## 開発

```bash
# dev dependencies をインストール
pip install -e ".[dev]"

# テストを実行
pytest

# カバレッジ付きで実行
pytest --cov

# Lint
ruff check src/

# 型チェック
mypy src/
```

## プロジェクト構造

```
src/hallucination_firewall/
├── cli.py                     # Click CLI
├── server.py                  # FastAPI サーバー
├── pipeline/                  # 検証レイヤー
├── parsers/                   # LLM 出力パーサー
├── registries/                # PyPI/npm クライアント（非同期並列）
└── reporters/                 # 出力フォーマット（JSON/SARIF）
    └── sarif_reporter.py      # SARIFフォーマットレポーター

vscode-extension/              # VS Code 拡張機能
.pre-commit-hooks.yaml         # Pre-commit 定義
.github/workflows/             # CI品質ゲート
```

## 対象者

- ✅ AI コードアシスタント（Copilot、Claude、ChatGPT）を使用する開発者
- ✅ CI/CD パイプラインで LLM 生成コードを統合するチーム
- ✅ AI 出力にコード品質基準を適用するプロジェクト
- ✅ 実行前にコードを検証したい全ての人

## ライセンス

MIT ライセンス — 詳細は [LICENSE](LICENSE) を参照。
