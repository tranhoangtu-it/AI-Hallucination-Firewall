🇺🇸 [English](README.md) | 🇻🇳 **[Tiếng Việt](README.vi.md)** | 🇯🇵 [日本語](README.ja.md) | 🇰🇷 [한국어](README.ko.md)

---

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/tranhoangtu-it/AI-Hallucination-Firewall/releases)
[![Tests](https://img.shields.io/badge/tests-210%20passed-brightgreen.svg)](#phát-triển)
[![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen.svg)](#development)
[![GitHub Pages](https://img.shields.io/badge/docs-live-blue.svg)](https://tranhoangtu-it.github.io/AI-Hallucination-Firewall/)

<p align="center">
  <img src="img/ai-hallucination-firewall.png" alt="AI Hallucination Firewall" width="600"/>
</p>

<p align="center">
  <strong>🌐 <a href="https://tranhoangtu-it.github.io/AI-Hallucination-Firewall/">Xem Trang Chủ</a></strong>
</p>

# AI Hallucination Firewall

Một proxy xác thực code do AI tạo trước khi đưa vào dự án của bạn. Hoạt động như **"bộ kiểm tra kiểu cho đầu ra AI"** — phát hiện hàm ảo, cách sử dụng lỗi thời, mẫu không hợp lệ, chữ ký sai và package không tồn tại.

## Tính Năng

- 🌳 **Xác thực cú pháp AST** — phân tích tree-sitter phát hiện code lỗi trong Python, JavaScript, TypeScript
- 📦 **Xác minh Import/Package** — xác thực package với PyPI và npm registries, hỗ trợ alias (`import pandas as pd` → `pd.DataFrame()`)
- 🔍 **Xác thực Chữ ký Hàm** — Jedi + inspect xác thực tham số, tham số bắt buộc và keyword arguments
- 📄 **Trình phân tích Đầu ra LLM** — trích xuất và xác thực code blocks từ markdown
- 🪝 **Tích hợp Pre-commit** — Git hooks tự động cho Python và JavaScript/TypeScript
- 🔌 **Extension VS Code** — chẩn đoán inline thời gian thực với chế độ trigger cấu hình được
- ⚡ **Kiểm tra Registry song song** — tra cứu PyPI/npm bất đồng bộ đồng thời với semaphore throttling
- 📊 **Xuất SARIF** — tích hợp GitHub Code Scanning với `--format sarif`
- 🚦 **CI Quality Gate** — GitHub Actions workflow với lint/type-check/test matrix (Python 3.11-3.13, 80% coverage)
- 🔒 **Chính sách CI nghiêm ngặt** — cờ `--ci` buộc fail-on-network-error với ngưỡng cảnh báo
- 📈 **Observability Metrics** — endpoint `/metrics` hiển thị latency, cache hit rate, error count

## Cách Hoạt Động

```
Code Input → AST Parsing → Import Check → Signature Validation → Report
     │           │              │                │                  │
tree-sitter    PyPI/npm        Jedi         Rich/JSON/SARIF
 (syntax)   (async parallel) (correctness)
```

**Pipeline xác thực 4 lớp:**
1. **Cú pháp** — phân tích AST tree-sitter phát hiện code lỗi
2. **Imports** — xác minh package tồn tại trên PyPI/npm
3. **Signatures** — xác thực tham số hàm với API thực tế
4. **Deprecation** — đánh dấu mẫu lỗi thời với gợi ý thay thế (tương lai)

## Cài Đặt

Yêu cầu Python 3.11+.

```bash
# Clone và cài đặt
git clone https://github.com/tranhoangtu-it/AI-Hallucination-Firewall.git
cd AI-Hallucination-Firewall
pip install -e ".[dev]"
```

## Bắt Đầu Nhanh

```bash
# Xác thực file
firewall check app.py

# Xác thực phản hồi markdown LLM
firewall parse response.md

# Đầu ra JSON cho CI/CD
firewall check --format json app.py

# Đầu ra SARIF cho GitHub Code Scanning
firewall check --format sarif app.py

# Chế độ CI nghiêm ngặt (fail khi lỗi mạng, áp dụng ngưỡng cảnh báo)
firewall check --ci app.py

# Khởi động API server
firewall serve
```

## Sử Dụng

### Lệnh CLI

```bash
# Kiểm tra một file
firewall check mycode.py

# Kiểm tra nhiều file
firewall check src/*.py

# Pipe từ stdin
cat generated_code.py | firewall check --stdin -l python

# Chế độ CI (fail khi lỗi mạng, áp dụng ngưỡng cảnh báo)
firewall check --ci src/*.py

# Đầu ra SARIF cho GitHub Code Scanning
firewall check --format sarif --output results.sarif src/
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/tranhoangtu-it/AI-Hallucination-Firewall
    rev: v0.1.0
    hooks:
      - id: firewall-check
      - id: firewall-check-js
```

### Extension VS Code

1. Vào thư mục `vscode-extension/`, chạy `npm install && npm run compile`
2. Cài đặt qua VS Code: `Extensions: Install from VSIX`
3. Cấu hình `hallucinationFirewall.triggerMode`: `onSave` (mặc định) hoặc `onChange`

### API Server

```bash
# Khởi động server
firewall serve --host 0.0.0.0 --port 8000

# Xác thực qua API
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"code": "import fakelib", "language": "python"}'

# Xem observability metrics
curl http://localhost:8000/metrics
```

### Cấu Hình

Tạo file `.firewall.toml` trong thư mục gốc dự án:

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

## Phát Triển

```bash
# Cài đặt dependencies cho dev
pip install -e ".[dev]"

# Chạy tests
pytest

# Chạy với coverage
pytest --cov

# Lint
ruff check src/

# Type check
mypy src/
```

## Cấu Trúc Dự Án

```
src/hallucination_firewall/
├── cli.py                     # Click CLI
├── server.py                  # FastAPI server
├── pipeline/                  # Các lớp xác thực
├── parsers/                   # Phân tích đầu ra LLM
├── registries/                # PyPI/npm clients (async parallel)
└── reporters/                 # Định dạng đầu ra (JSON/SARIF)
    └── sarif_reporter.py      # SARIF format reporter

vscode-extension/              # Extension VS Code
.pre-commit-hooks.yaml         # Định nghĩa pre-commit
.github/workflows/             # CI quality gate
```

## Dành Cho Ai?

- ✅ Developers sử dụng AI code assistants (Copilot, Claude, ChatGPT)
- ✅ Teams tích hợp code do LLM tạo trong CI/CD pipelines
- ✅ Dự án áp dụng tiêu chuẩn chất lượng code cho AI output
- ✅ Bất kỳ ai muốn xác thực code trước khi chạy

## Giấy Phép

Giấy phép MIT — xem chi tiết tại [LICENSE](LICENSE).
