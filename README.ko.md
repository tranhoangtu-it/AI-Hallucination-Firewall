🇺🇸 [English](README.md) | 🇻🇳 [Tiếng Việt](README.vi.md) | 🇯🇵 [日本語](README.ja.md) | 🇰🇷 **[한국어](README.ko.md)**

---

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/tranhoangtu-it/AI-Hallucination-Firewall/releases)
[![Tests](https://img.shields.io/badge/tests-140%20passed-brightgreen.svg)](#개발)
[![GitHub Pages](https://img.shields.io/badge/docs-live-blue.svg)](https://tranhoangtu-it.github.io/AI-Hallucination-Firewall/)

<p align="center">
  <img src="img/ai-hallucination-firewall.png" alt="AI Hallucination Firewall" width="600"/>
</p>

<p align="center">
  <strong>🌐 <a href="https://tranhoangtu-it.github.io/AI-Hallucination-Firewall/">랜딩 페이지 보기</a></strong>
</p>

# AI Hallucination Firewall

AI가 생성한 코드를 코드베이스에 적용하기 전에 검증하는 검증 프록시. **"AI 출력 타입 체커"**로 작동 — Python, JavaScript, TypeScript에서 환각 함수, 사용 중단된 용법, 잘못된 패턴, 잘못된 서명, 존재하지 않는 패키지를 감지합니다.

## 기능

- 🌳 **AST 구문 검증** — tree-sitter 파서가 Python, JavaScript, TypeScript의 잘못된 코드를 실행 전 감지
- 📦 **Import 검증** — PyPI 및 npm 레지스트리로 패키지 검증, 별칭 해석 지원（`import pandas as pd` → `pd.DataFrame()`）
- 🔍 **서명 검사** — Jedi + inspect가 함수 매개변수, 필수 인수, 키워드 인수를 실제 API로 검증
- 📄 **LLM 출력 파서** — 마크다운 응답에서 코드 블록을 추출하고 각 블록을 독립적으로 검증
- 🪝 **Pre-commit 통합** — Python과 JavaScript/TypeScript용 자동 Git 훅
- 🔌 **VS Code 확장** — 실시간 인라인 진단. 저장 시 또는 변경 시 트리거 구성 가능
- ⚡ **병렬 레지스트리 확인** — 세마포어 기반 조절을 사용한 PyPI/npm 비동기 동시 조회
- 📊 **SARIF 내보내기** — `--format sarif`로 GitHub Code Scanning 통합
- 🚦 **CI 품질 게이트** — lint/type-check/test 매트릭스가 있는 GitHub Actions 워크플로우（Python 3.11-3.13, 80% 커버리지）
- 🔒 **엄격한 CI 정책** — `--ci` 플래그로 네트워크 오류 시 실패 및 경고 임계값 강제
- 📈 **관찰 가능성 메트릭** — `/metrics` 엔드포인트로 지연 시간, 캐시 적중률, 오류 수 노출

## 작동 방식

```
Code Input → AST Parsing → Import Check → Signature Validation → Report
     │           │              │                │                  │
tree-sitter    PyPI/npm        Jedi         Rich/JSON/SARIF
 (syntax)   (async parallel) (correctness)
```

**4층 검증 파이프라인:**
1. **구문** — tree-sitter AST 파싱이 잘못된 코드 감지
2. **Imports** — PyPI & npm 레지스트리에서 패키지 존재 검증
3. **서명** — 실제 API 서명으로 함수 호출 검증
4. **사용 중단** — 대체 제안으로 사용 중단 패턴 플래그 (향후)

## 설치

Python 3.11+ 필요.

```bash
# 클론 및 설치
git clone https://github.com/tranhoangtu-it/AI-Hallucination-Firewall.git
cd AI-Hallucination-Firewall
pip install -e ".[dev]"
```

## 빠른 시작

```bash
# 파일 검증
firewall check app.py

# LLM 마크다운 응답 검증
firewall parse response.md

# CI/CD용 JSON 출력
firewall check --format json app.py

# GitHub Code Scanning용 SARIF 출력
firewall check --format sarif app.py

# 엄격한 CI 모드（네트워크 오류 시 실패, 경고 임계값 적용）
firewall check --ci app.py

# API 서버 시작
firewall serve
```

## 사용법

### CLI 명령

```bash
# 단일 파일 체크
firewall check mycode.py

# 여러 파일 체크
firewall check src/*.py

# stdin에서 파이프
cat generated_code.py | firewall check --stdin -l python

# CI 모드（네트워크 오류 시 실패, 경고 임계값 적용）
firewall check --ci src/*.py

# GitHub Code Scanning용 SARIF 출력
firewall check --format sarif --output results.sarif src/
```

### Pre-commit 훅

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/tranhoangtu-it/AI-Hallucination-Firewall
    rev: v0.1.0
    hooks:
      - id: firewall-check
      - id: firewall-check-js
```

### VS Code 확장

1. `vscode-extension/`으로 이동, `npm install && npm run compile` 실행
2. VS Code에서 설치: `Extensions: Install from VSIX`
3. `hallucinationFirewall.triggerMode` 설정: `onSave` (기본) 또는 `onChange`

### API 서버

```bash
# 서버 시작
firewall serve --host 0.0.0.0 --port 8000

# API로 검증
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"code": "import fakelib", "language": "python"}'

# 관찰 가능성 메트릭 보기
curl http://localhost:8000/metrics
```

### 구성

프로젝트 루트에 `.firewall.toml` 생성:

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

## 개발

```bash
# dev dependencies 설치
pip install -e ".[dev]"

# 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov

# Lint
ruff check src/

# 타입 체크
mypy src/
```

## 프로젝트 구조

```
src/hallucination_firewall/
├── cli.py                     # Click CLI
├── server.py                  # FastAPI 서버
├── pipeline/                  # 검증 레이어
├── parsers/                   # LLM 출력 파서
├── registries/                # PyPI/npm 클라이언트（비동기 병렬）
└── reporters/                 # 출력 포맷팅（JSON/SARIF）
    └── sarif_reporter.py      # SARIF 포맷 리포터

vscode-extension/              # VS Code 확장
.pre-commit-hooks.yaml         # Pre-commit 정의
.github/workflows/             # CI 품질 게이트
```

## 대상 사용자

- ✅ AI 코드 어시스턴트(Copilot, Claude, ChatGPT)를 사용하는 개발자
- ✅ CI/CD 파이프라인에서 LLM 생성 코드를 통합하는 팀
- ✅ AI 출력에 코드 품질 표준을 적용하는 프로젝트
- ✅ 실행 전에 코드를 검증하려는 모든 사람

## 라이선스

MIT 라이선스 — 자세한 내용은 [LICENSE](LICENSE)를 참조하세요.
