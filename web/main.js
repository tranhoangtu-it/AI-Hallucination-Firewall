// Translations
const translations = {
  en: {
    "nav.title": "Hallucination Firewall",
    "nav.features": "Features",
    "nav.pipeline": "Pipeline",
    "nav.integrations": "Integrations",
    "nav.quickstart": "Quick Start",
    "nav.demo": "Demo",
    "nav.faq": "FAQ",
    "hero.badge": "v0.1.0 — Open Source",
    "hero.title": "Type Checker",
    "hero.subtitle": "for AI Output",
    "hero.description": "Validate AI-generated code before it enters your codebase. Catches hallucinated APIs, wrong signatures, and nonexistent packages across Python, JavaScript, and TypeScript.",
    "hero.cta_start": "Get Started",
    "hero.cta_source": "View Source",
    "hero.stats.layers": "Validation Layers",
    "hero.stats.languages": "Languages",
    "hero.stats.tests": "Tests Passing",
    "hero.stats.coverage": "Coverage",
    "social.github_stars": "GitHub Stars",
    "social.metric_tests": "140+ Tests",
    "social.metric_layers": "4 Validation Layers",
    "social.metric_languages": "3 Languages",
    "social.metric_coverage": "87% Coverage",
    "demo.title": "See It In Action",
    "demo.subtitle": "Watch the firewall detect hallucinated imports, invalid signatures, and nonexistent packages in real-time.",
    "demo.run_button": "Run Validation",
    "demo.input_title": "AI-Generated Code",
    "demo.output_title": "Validation Results",
    "demo.result_syntax": "Syntax Check",
    "demo.result_import_fail": "Import: sklearn.magic_solver",
    "demo.result_import_fail_desc": "Package not found on PyPI",
    "demo.result_import_fail2": "Import: nonexistent_package",
    "demo.result_import_fail2_desc": "Package does not exist",
    "demo.result_signature": "Signature: DataFrame.magic_method()",
    "demo.result_signature_desc": "Method does not exist in pandas API",
    "demo.status_pass": "PASS",
    "demo.status_error": "ERROR",
    "features.title": "Everything You Need",
    "features.subtitle": "Four validation layers plus seamless integrations for your entire development workflow.",
    "features.ast.title": "AST Syntax Validation",
    "features.ast.description": "Tree-sitter powered parsing catches malformed code in Python, JavaScript, and TypeScript before it runs.",
    "features.import.title": "Import Verification",
    "features.import.description": "Validates every import against PyPI and npm registries. Catches hallucinated packages instantly with parallel checks.",
    "features.signature.title": "Signature Checking",
    "features.signature.description": "Jedi-powered introspection with alias resolution. Validates function calls against real APIs.",
    "features.parser.title": "LLM Output Parser",
    "features.parser.description": "Extracts code blocks from ChatGPT/Claude markdown responses and validates each block independently.",
    "features.precommit.title": "Pre-commit Hook",
    "features.precommit.description": "Automatic validation on every git commit. Catches issues before they enter your codebase. SQLite cached.",
    "features.vscode.title": "VS Code Extension",
    "features.vscode.description": "Real-time inline diagnostics. Squiggly underlines for errors. Configurable on-save or on-change trigger.",
    "features.cicd.title": "CI/CD Integration",
    "features.cicd.description": "GitHub Actions pipeline with SARIF output for Code Scanning. Strict CI mode with --ci flag.",
    "features.observability.title": "Observability",
    "features.observability.description": "/metrics endpoint with Prometheus format. Latency histogram, cache hit rate, validation counts.",
    "features.performance.title": "10x Faster",
    "features.performance.description": "Parallel registry validation with asyncio.gather. Up to 10x speedup on multi-file checks.",
    "pipeline.title": "4-Layer Validation Pipeline",
    "pipeline.subtitle": "Each layer catches different categories of AI hallucinations, from syntax errors to wrong function signatures.",
    "pipeline.layer1.badge": "Layer 1",
    "pipeline.layer1.title": "Syntax",
    "pipeline.layer1.description": "tree-sitter AST parsing catches malformed code",
    "pipeline.layer2.badge": "Layer 2",
    "pipeline.layer2.title": "Imports",
    "pipeline.layer2.description": "Verifies packages exist on PyPI & npm registries",
    "pipeline.layer3.badge": "Layer 3",
    "pipeline.layer3.title": "Signatures",
    "pipeline.layer3.description": "Validates function calls against real API signatures",
    "pipeline.layer4.badge": "Layer 4",
    "pipeline.layer4.title": "Deprecation",
    "pipeline.layer4.description": "Flags deprecated patterns with replacement suggestions",
    "integrations.title": "Fits Your Workflow",
    "integrations.subtitle": "CLI, API server, pre-commit hooks, VS Code extension — use it however you work.",
    "integrations.cli.title": "CLI",
    "integrations.cli.badge": "Primary",
    "integrations.api.title": "REST API",
    "integrations.api.badge": "FastAPI",
    "integrations.precommit.title": "Pre-commit Hook",
    "integrations.precommit.badge": "Automatic",
    "integrations.vscode.title": "VS Code Extension",
    "integrations.vscode.badge": "Real-time",
    "integrations.vscode.feature1": "Inline diagnostics with squiggly underlines",
    "integrations.vscode.feature2": "Configurable trigger: on-save or on-change",
    "integrations.vscode.feature3": "Status bar with validation state",
    "integrations.vscode.feature4": "Python, JavaScript, TypeScript support",
    "quickstart.title": "Get Started in 30 Seconds",
    "faq.title": "Frequently Asked Questions",
    "faq.subtitle": "Everything you need to know about using AI Hallucination Firewall.",
    "faq.q1": "Does it slow down my CI pipeline?",
    "faq.a1": "No, average validation is under 2 seconds per file. Parallel async checks ensure minimal overhead.",
    "faq.q2": "What about false positives?",
    "faq.a2": "Fail-open policy. Unknown functions are skipped, not flagged. We only report what we can verify is wrong.",
    "faq.q3": "Which languages are supported?",
    "faq.a3": "Python, JavaScript, TypeScript. More languages coming soon based on community feedback.",
    "faq.q4": "How is this different from ESLint/Pylint?",
    "faq.a4": "Those check code style. We check if AI-generated APIs actually exist in the real world.",
    "faq.q5": "Can I use it offline?",
    "faq.a5": "Syntax and signature checks work offline. Import checks need network for registry lookups (with caching).",
    "faq.q6": "Is it safe to use?",
    "faq.a6": "Read-only validation. Never executes your code. Restricted to allowlisted stdlib modules for safety.",
    "comparison.title": "Why AI Hallucination Firewall?",
    "comparison.subtitle": "Built specifically for AI-generated code validation.",
    "comparison.feature": "Feature",
    "comparison.firewall": "Hallucination Firewall",
    "comparison.linters": "ESLint/Pylint",
    "comparison.manual": "Manual Review",
    "comparison.row1": "Detects hallucinated APIs",
    "comparison.row2": "Registry verification",
    "comparison.row3": "Signature validation",
    "comparison.row4": "Works with any LLM",
    "comparison.row5": "Automated CI integration",
    "comparison.row6": "Zero config",
    "comparison.yes": "✓",
    "comparison.no": "✗",
    "comparison.sometimes": "Sometimes",
    "comparison.slow": "Slow",
    "comparison.na": "N/A",
    "cta.title": "Stop AI Hallucinations Today",
    "cta.subtitle": "Open source, MIT licensed, zero config. Works with ChatGPT, Claude, Copilot, and any LLM output.",
    "cta.github": "Star on GitHub",
    "cta.download": "Download v0.1.0",
    "footer.title": "AI Hallucination Firewall v0.1.0",
    "footer.license": "MIT License",
    "footer.made_by": "Made by"
  },
  vi: {
    "nav.title": "Tường lửa Hallucination",
    "nav.features": "Tính năng",
    "nav.pipeline": "Pipeline",
    "nav.integrations": "Tích hợp",
    "nav.quickstart": "Bắt đầu nhanh",
    "nav.demo": "Demo",
    "nav.faq": "Câu hỏi",
    "hero.badge": "v0.1.0 — Mã nguồn mở",
    "hero.title": "Bộ Kiểm Tra Code AI",
    "hero.subtitle": "cho AI Output",
    "hero.description": "Xác thực code do AI tạo trước khi đưa vào dự án của bạn. Phát hiện API ảo, tham số sai và package không tồn tại trong Python, JavaScript và TypeScript.",
    "hero.cta_start": "Bắt đầu",
    "hero.cta_source": "Xem mã nguồn",
    "hero.stats.layers": "Lớp xác thực",
    "hero.stats.languages": "Ngôn ngữ",
    "hero.stats.tests": "Tests đạt",
    "hero.stats.coverage": "Độ phủ",
    "social.github_stars": "GitHub Stars",
    "social.metric_tests": "140+ Tests",
    "social.metric_layers": "4 Lớp Xác Thực",
    "social.metric_languages": "3 Ngôn Ngữ",
    "social.metric_coverage": "87% Độ Phủ",
    "demo.title": "Xem Hoạt Động",
    "demo.subtitle": "Xem tường lửa phát hiện imports ảo, signatures sai và packages không tồn tại trong thời gian thực.",
    "demo.run_button": "Chạy Xác Thực",
    "demo.input_title": "Code Do AI Tạo",
    "demo.output_title": "Kết Quả Xác Thực",
    "demo.result_syntax": "Kiểm Tra Cú Pháp",
    "demo.result_import_fail": "Import: sklearn.magic_solver",
    "demo.result_import_fail_desc": "Package không tìm thấy trên PyPI",
    "demo.result_import_fail2": "Import: nonexistent_package",
    "demo.result_import_fail2_desc": "Package không tồn tại",
    "demo.result_signature": "Signature: DataFrame.magic_method()",
    "demo.result_signature_desc": "Method không tồn tại trong pandas API",
    "demo.status_pass": "ĐẠT",
    "demo.status_error": "LỖI",
    "features.title": "Mọi thứ bạn cần",
    "features.subtitle": "Bốn lớp xác thực cùng tích hợp liền mạch cho toàn bộ quy trình phát triển của bạn.",
    "features.ast.title": "Xác thực cú pháp AST",
    "features.ast.description": "Phân tích cú pháp tree-sitter phát hiện code lỗi trong Python, JavaScript và TypeScript trước khi chạy.",
    "features.import.title": "Xác minh Import",
    "features.import.description": "Xác thực mọi import với PyPI và npm registries. Phát hiện ngay package ảo với kiểm tra song song.",
    "features.signature.title": "Kiểm tra Signature",
    "features.signature.description": "Jedi-powered introspection với phân giải alias. Xác thực function calls với API thật.",
    "features.parser.title": "Trình phân tích LLM",
    "features.parser.description": "Trích xuất code blocks từ markdown ChatGPT/Claude và xác thực từng block độc lập.",
    "features.precommit.title": "Pre-commit Hook",
    "features.precommit.description": "Tự động xác thực mỗi lần git commit. Phát hiện lỗi trước khi vào codebase. SQLite cached.",
    "features.vscode.title": "Extension VS Code",
    "features.vscode.description": "Chẩn đoán inline thời gian thực. Gạch dưới lỗi. Trigger on-save hoặc on-change.",
    "features.cicd.title": "Tích hợp CI/CD",
    "features.cicd.description": "GitHub Actions pipeline với SARIF output cho Code Scanning. Chế độ CI nghiêm ngặt với --ci flag.",
    "features.observability.title": "Khả năng quan sát",
    "features.observability.description": "/metrics endpoint với định dạng Prometheus. Histogram độ trễ, tỷ lệ cache hit, số lần xác thực.",
    "features.performance.title": "Nhanh hơn 10 lần",
    "features.performance.description": "Xác thực registry song song với asyncio.gather. Tăng tốc đến 10 lần trên kiểm tra multi-file.",
    "pipeline.title": "Pipeline xác thực 4 lớp",
    "pipeline.subtitle": "Mỗi lớp phát hiện các loại hallucination AI khác nhau, từ lỗi cú pháp đến signature sai.",
    "pipeline.layer1.badge": "Lớp 1",
    "pipeline.layer1.title": "Cú pháp",
    "pipeline.layer1.description": "Phân tích AST tree-sitter phát hiện code lỗi",
    "pipeline.layer2.badge": "Lớp 2",
    "pipeline.layer2.title": "Imports",
    "pipeline.layer2.description": "Xác minh package tồn tại trên PyPI & npm registries",
    "pipeline.layer3.badge": "Lớp 3",
    "pipeline.layer3.title": "Signatures",
    "pipeline.layer3.description": "Xác thực function calls với API signatures thật",
    "pipeline.layer4.badge": "Lớp 4",
    "pipeline.layer4.title": "Deprecation",
    "pipeline.layer4.description": "Đánh dấu patterns lỗi thời với gợi ý thay thế",
    "integrations.title": "Phù hợp quy trình của bạn",
    "integrations.subtitle": "CLI, API server, pre-commit hooks, VS Code extension — dùng theo cách bạn làm việc.",
    "integrations.cli.title": "CLI",
    "integrations.cli.badge": "Chính",
    "integrations.api.title": "REST API",
    "integrations.api.badge": "FastAPI",
    "integrations.precommit.title": "Pre-commit Hook",
    "integrations.precommit.badge": "Tự động",
    "integrations.vscode.title": "Extension VS Code",
    "integrations.vscode.badge": "Thời gian thực",
    "integrations.vscode.feature1": "Chẩn đoán inline với gạch dưới lỗi",
    "integrations.vscode.feature2": "Trigger cấu hình: on-save hoặc on-change",
    "integrations.vscode.feature3": "Status bar với trạng thái xác thực",
    "integrations.vscode.feature4": "Hỗ trợ Python, JavaScript, TypeScript",
    "quickstart.title": "Bắt đầu trong 30 giây",
    "faq.title": "Câu Hỏi Thường Gặp",
    "faq.subtitle": "Mọi thứ bạn cần biết về việc sử dụng AI Hallucination Firewall.",
    "faq.q1": "Nó có làm chậm CI pipeline không?",
    "faq.a1": "Không, xác thực trung bình dưới 2 giây mỗi file. Kiểm tra async song song đảm bảo overhead tối thiểu.",
    "faq.q2": "Còn false positives thì sao?",
    "faq.a2": "Chính sách fail-open. Functions không rõ được bỏ qua, không gắn cờ. Chúng tôi chỉ báo cáo những gì chúng tôi có thể xác minh là sai.",
    "faq.q3": "Những ngôn ngữ nào được hỗ trợ?",
    "faq.a3": "Python, JavaScript, TypeScript. Nhiều ngôn ngữ hơn sắp ra mắt dựa trên phản hồi cộng đồng.",
    "faq.q4": "Khác gì ESLint/Pylint?",
    "faq.a4": "Những cái đó kiểm tra code style. Chúng tôi kiểm tra xem API do AI tạo có thực sự tồn tại trong thế giới thực không.",
    "faq.q5": "Tôi có thể dùng offline không?",
    "faq.a5": "Kiểm tra syntax và signature hoạt động offline. Kiểm tra import cần mạng cho registry lookups (có caching).",
    "faq.q6": "Nó có an toàn không?",
    "faq.a6": "Xác thực chỉ đọc. Không bao giờ thực thi code của bạn. Hạn chế đối với stdlib modules được phép để an toàn.",
    "comparison.title": "Tại Sao AI Hallucination Firewall?",
    "comparison.subtitle": "Được xây dựng đặc biệt cho xác thực code do AI tạo.",
    "comparison.feature": "Tính Năng",
    "comparison.firewall": "Hallucination Firewall",
    "comparison.linters": "ESLint/Pylint",
    "comparison.manual": "Kiểm Tra Thủ Công",
    "comparison.row1": "Phát hiện API ảo",
    "comparison.row2": "Xác minh registry",
    "comparison.row3": "Xác thực signature",
    "comparison.row4": "Hoạt động với mọi LLM",
    "comparison.row5": "Tích hợp CI tự động",
    "comparison.row6": "Không cần config",
    "comparison.yes": "✓",
    "comparison.no": "✗",
    "comparison.sometimes": "Đôi khi",
    "comparison.slow": "Chậm",
    "comparison.na": "N/A",
    "cta.title": "Dừng AI Hallucinations hôm nay",
    "cta.subtitle": "Mã nguồn mở, giấy phép MIT, không cần config. Hoạt động với ChatGPT, Claude, Copilot và mọi LLM output.",
    "cta.github": "Star trên GitHub",
    "cta.download": "Tải v0.1.0",
    "footer.title": "AI Hallucination Firewall v0.1.0",
    "footer.license": "Giấy phép MIT",
    "footer.made_by": "Tạo bởi"
  },
  ja: {
    "nav.title": "Hallucination Firewall",
    "nav.features": "機能",
    "nav.pipeline": "パイプライン",
    "nav.integrations": "統合",
    "nav.quickstart": "クイックスタート",
    "nav.demo": "デモ",
    "nav.faq": "FAQ",
    "hero.badge": "v0.1.0 — オープンソース",
    "hero.title": "AI出力の型チェッカー",
    "hero.subtitle": "for AI Output",
    "hero.description": "AIが生成したコードをコードベースに入る前に検証。Python、JavaScript、TypeScriptで幻覚API、間違った署名、存在しないパッケージを検出。",
    "hero.cta_start": "始める",
    "hero.cta_source": "ソースを見る",
    "hero.stats.layers": "検証レイヤー",
    "hero.stats.languages": "言語",
    "hero.stats.tests": "テスト合格",
    "hero.stats.coverage": "カバレッジ",
    "social.github_stars": "GitHubスター",
    "social.metric_tests": "140+テスト",
    "social.metric_layers": "4検証レイヤー",
    "social.metric_languages": "3言語",
    "social.metric_coverage": "87%カバレッジ",
    "demo.title": "実際に見る",
    "demo.subtitle": "ファイアウォールがリアルタイムで幻覚インポート、無効な署名、存在しないパッケージを検出する様子をご覧ください。",
    "demo.run_button": "検証を実行",
    "demo.input_title": "AIが生成したコード",
    "demo.output_title": "検証結果",
    "demo.result_syntax": "構文チェック",
    "demo.result_import_fail": "インポート: sklearn.magic_solver",
    "demo.result_import_fail_desc": "PyPIでパッケージが見つかりません",
    "demo.result_import_fail2": "インポート: nonexistent_package",
    "demo.result_import_fail2_desc": "パッケージが存在しません",
    "demo.result_signature": "署名: DataFrame.magic_method()",
    "demo.result_signature_desc": "pandas APIにメソッドが存在しません",
    "demo.status_pass": "合格",
    "demo.status_error": "エラー",
    "features.title": "必要なすべて",
    "features.subtitle": "4つの検証レイヤーと開発ワークフロー全体のシームレスな統合。",
    "features.ast.title": "AST構文検証",
    "features.ast.description": "Tree-sitterパーサーがPython、JavaScript、TypeScriptの不正なコードを実行前に検出。",
    "features.import.title": "インポート検証",
    "features.import.description": "すべてのインポートをPyPIとnpmレジストリで検証。並列チェックで幻覚パッケージを即座に検出。",
    "features.signature.title": "署名チェック",
    "features.signature.description": "エイリアス解決を備えたJediパワードイントロスペクション。実際のAPIで関数呼び出しを検証。",
    "features.parser.title": "LLM出力パーサー",
    "features.parser.description": "ChatGPT/Claudeマークダウンレスポンスからコードブロックを抽出し、各ブロックを独立して検証。",
    "features.precommit.title": "Pre-commitフック",
    "features.precommit.description": "すべてのgitコミットで自動検証。コードベースに入る前に問題を検出。SQLiteキャッシュ。",
    "features.vscode.title": "VS Code拡張機能",
    "features.vscode.description": "リアルタイムインライン診断。エラーの波線下線。保存時または変更時のトリガー設定可能。",
    "features.cicd.title": "CI/CD統合",
    "features.cicd.description": "コードスキャン用SARIF出力を備えたGitHub Actionsパイプライン。--ciフラグで厳格なCIモード。",
    "features.observability.title": "可観測性",
    "features.observability.description": "Prometheus形式の/metricsエンドポイント。レイテンシヒストグラム、キャッシュヒット率、検証カウント。",
    "features.performance.title": "10倍高速",
    "features.performance.description": "asyncio.gatherによる並列レジストリ検証。マルチファイルチェックで最大10倍高速化。",
    "pipeline.title": "4層検証パイプライン",
    "pipeline.subtitle": "各レイヤーは構文エラーから間違った関数署名まで、異なるカテゴリのAI幻覚を検出。",
    "pipeline.layer1.badge": "レイヤー 1",
    "pipeline.layer1.title": "構文",
    "pipeline.layer1.description": "tree-sitter AST解析が不正なコードを検出",
    "pipeline.layer2.badge": "レイヤー 2",
    "pipeline.layer2.title": "インポート",
    "pipeline.layer2.description": "PyPI & npmレジストリでパッケージ存在を検証",
    "pipeline.layer3.badge": "レイヤー 3",
    "pipeline.layer3.title": "署名",
    "pipeline.layer3.description": "実際のAPI署名で関数呼び出しを検証",
    "pipeline.layer4.badge": "レイヤー 4",
    "pipeline.layer4.title": "非推奨",
    "pipeline.layer4.description": "非推奨パターンを置換提案でフラグ",
    "integrations.title": "ワークフローに適合",
    "integrations.subtitle": "CLI、APIサーバー、pre-commitフック、VS Code拡張機能 — あなたの働き方で使用。",
    "integrations.cli.title": "CLI",
    "integrations.cli.badge": "プライマリ",
    "integrations.api.title": "REST API",
    "integrations.api.badge": "FastAPI",
    "integrations.precommit.title": "Pre-commitフック",
    "integrations.precommit.badge": "自動",
    "integrations.vscode.title": "VS Code拡張機能",
    "integrations.vscode.badge": "リアルタイム",
    "integrations.vscode.feature1": "波線下線付きインライン診断",
    "integrations.vscode.feature2": "設定可能なトリガー：保存時または変更時",
    "integrations.vscode.feature3": "検証状態付きステータスバー",
    "integrations.vscode.feature4": "Python、JavaScript、TypeScriptサポート",
    "quickstart.title": "30秒で始める",
    "faq.title": "よくある質問",
    "faq.subtitle": "AI Hallucination Firewallの使用について知っておくべきすべて。",
    "faq.q1": "CIパイプラインが遅くなりますか？",
    "faq.a1": "いいえ、ファイルあたりの平均検証時間は2秒未満です。並列非同期チェックにより最小限のオーバーヘッドを保証します。",
    "faq.q2": "誤検出はどうですか？",
    "faq.a2": "フェイルオープンポリシー。不明な関数はスキップされ、フラグが付けられません。検証できるもののみを報告します。",
    "faq.q3": "どの言語がサポートされていますか？",
    "faq.a3": "Python、JavaScript、TypeScript。コミュニティのフィードバックに基づいてさらに多くの言語が近日公開予定。",
    "faq.q4": "ESLint/Pylintとの違いは？",
    "faq.a4": "それらはコードスタイルをチェックします。私たちはAI生成APIが実際に存在するかどうかをチェックします。",
    "faq.q5": "オフラインで使用できますか？",
    "faq.a5": "構文と署名のチェックはオフラインで動作します。インポートチェックはレジストリルックアップにネットワークが必要です（キャッシュあり）。",
    "faq.q6": "使用しても安全ですか？",
    "faq.a6": "読み取り専用検証。コードを実行することはありません。安全のため許可リストのstdlibモジュールに制限されています。",
    "comparison.title": "なぜAI Hallucination Firewall？",
    "comparison.subtitle": "AI生成コード検証専用に構築。",
    "comparison.feature": "機能",
    "comparison.firewall": "Hallucination Firewall",
    "comparison.linters": "ESLint/Pylint",
    "comparison.manual": "手動レビュー",
    "comparison.row1": "幻覚APIを検出",
    "comparison.row2": "レジストリ検証",
    "comparison.row3": "署名検証",
    "comparison.row4": "すべてのLLMで動作",
    "comparison.row5": "自動CI統合",
    "comparison.row6": "ゼロ設定",
    "comparison.yes": "✓",
    "comparison.no": "✗",
    "comparison.sometimes": "時々",
    "comparison.slow": "遅い",
    "comparison.na": "N/A",
    "cta.title": "今日AI幻覚を止める",
    "cta.subtitle": "オープンソース、MITライセンス、設定不要。ChatGPT、Claude、Copilot、すべてのLLM出力で動作。",
    "cta.github": "GitHubでスター",
    "cta.download": "v0.1.0をダウンロード",
    "footer.title": "AI Hallucination Firewall v0.1.0",
    "footer.license": "MITライセンス",
    "footer.made_by": "作成者"
  },
  ko: {
    "nav.title": "Hallucination Firewall",
    "nav.features": "기능",
    "nav.pipeline": "파이프라인",
    "nav.integrations": "통합",
    "nav.quickstart": "빠른 시작",
    "nav.demo": "데모",
    "nav.faq": "FAQ",
    "hero.badge": "v0.1.0 — 오픈소스",
    "hero.title": "AI 출력 타입 체커",
    "hero.subtitle": "for AI Output",
    "hero.description": "AI가 생성한 코드를 코드베이스에 적용하기 전에 검증. Python, JavaScript, TypeScript에서 환각 API, 잘못된 서명, 존재하지 않는 패키지 감지.",
    "hero.cta_start": "시작하기",
    "hero.cta_source": "소스 보기",
    "hero.stats.layers": "검증 레이어",
    "hero.stats.languages": "언어",
    "hero.stats.tests": "테스트 통과",
    "hero.stats.coverage": "커버리지",
    "social.github_stars": "GitHub 스타",
    "social.metric_tests": "140+ 테스트",
    "social.metric_layers": "4 검증 레이어",
    "social.metric_languages": "3 언어",
    "social.metric_coverage": "87% 커버리지",
    "demo.title": "실제로 보기",
    "demo.subtitle": "방화벽이 실시간으로 환각 가져오기, 잘못된 서명 및 존재하지 않는 패키지를 감지하는 것을 지켜보세요.",
    "demo.run_button": "검증 실행",
    "demo.input_title": "AI가 생성한 코드",
    "demo.output_title": "검증 결과",
    "demo.result_syntax": "구문 검사",
    "demo.result_import_fail": "가져오기: sklearn.magic_solver",
    "demo.result_import_fail_desc": "PyPI에서 패키지를 찾을 수 없습니다",
    "demo.result_import_fail2": "가져오기: nonexistent_package",
    "demo.result_import_fail2_desc": "패키지가 존재하지 않습니다",
    "demo.result_signature": "서명: DataFrame.magic_method()",
    "demo.result_signature_desc": "pandas API에 메서드가 존재하지 않습니다",
    "demo.status_pass": "통과",
    "demo.status_error": "오류",
    "features.title": "필요한 모든 것",
    "features.subtitle": "4개의 검증 레이어와 전체 개발 워크플로우를 위한 원활한 통합.",
    "features.ast.title": "AST 구문 검증",
    "features.ast.description": "Tree-sitter 파서가 Python, JavaScript, TypeScript의 잘못된 코드를 실행 전 감지.",
    "features.import.title": "Import 검증",
    "features.import.description": "모든 import를 PyPI 및 npm 레지스트리로 검증. 병렬 검사로 환각 패키지를 즉시 감지.",
    "features.signature.title": "서명 검사",
    "features.signature.description": "별칭 해석을 갖춘 Jedi 기반 인트로스펙션. 실제 API로 함수 호출 검증.",
    "features.parser.title": "LLM 출력 파서",
    "features.parser.description": "ChatGPT/Claude 마크다운 응답에서 코드 블록을 추출하고 각 블록을 독립적으로 검증.",
    "features.precommit.title": "Pre-commit 훅",
    "features.precommit.description": "모든 git 커밋에서 자동 검증. 코드베이스에 들어가기 전 문제 감지. SQLite 캐시.",
    "features.vscode.title": "VS Code 확장",
    "features.vscode.description": "실시간 인라인 진단. 오류 물결 밑줄. 저장 시 또는 변경 시 트리거 구성 가능.",
    "features.cicd.title": "CI/CD 통합",
    "features.cicd.description": "코드 스캐닝을 위한 SARIF 출력이 있는 GitHub Actions 파이프라인. --ci 플래그로 엄격한 CI 모드.",
    "features.observability.title": "관찰 가능성",
    "features.observability.description": "Prometheus 형식의 /metrics 엔드포인트. 지연 히스토그램, 캐시 적중률, 검증 카운트.",
    "features.performance.title": "10배 빠름",
    "features.performance.description": "asyncio.gather를 사용한 병렬 레지스트리 검증. 다중 파일 검사에서 최대 10배 속도 향상.",
    "pipeline.title": "4층 검증 파이프라인",
    "pipeline.subtitle": "각 레이어는 구문 오류부터 잘못된 함수 서명까지 다양한 AI 환각 범주를 감지.",
    "pipeline.layer1.badge": "레이어 1",
    "pipeline.layer1.title": "구문",
    "pipeline.layer1.description": "tree-sitter AST 파싱이 잘못된 코드 감지",
    "pipeline.layer2.badge": "레이어 2",
    "pipeline.layer2.title": "Imports",
    "pipeline.layer2.description": "PyPI & npm 레지스트리에서 패키지 존재 검증",
    "pipeline.layer3.badge": "레이어 3",
    "pipeline.layer3.title": "서명",
    "pipeline.layer3.description": "실제 API 서명으로 함수 호출 검증",
    "pipeline.layer4.badge": "레이어 4",
    "pipeline.layer4.title": "사용 중단",
    "pipeline.layer4.description": "대체 제안으로 사용 중단 패턴 플래그",
    "integrations.title": "워크플로우에 맞춤",
    "integrations.subtitle": "CLI, API 서버, pre-commit 훅, VS Code 확장 — 작업 방식대로 사용.",
    "integrations.cli.title": "CLI",
    "integrations.cli.badge": "기본",
    "integrations.api.title": "REST API",
    "integrations.api.badge": "FastAPI",
    "integrations.precommit.title": "Pre-commit 훅",
    "integrations.precommit.badge": "자동",
    "integrations.vscode.title": "VS Code 확장",
    "integrations.vscode.badge": "실시간",
    "integrations.vscode.feature1": "물결 밑줄이 있는 인라인 진단",
    "integrations.vscode.feature2": "구성 가능한 트리거: 저장 시 또는 변경 시",
    "integrations.vscode.feature3": "검증 상태가 있는 상태 표시줄",
    "integrations.vscode.feature4": "Python, JavaScript, TypeScript 지원",
    "quickstart.title": "30초 만에 시작",
    "faq.title": "자주 묻는 질문",
    "faq.subtitle": "AI Hallucination Firewall 사용에 대해 알아야 할 모든 것.",
    "faq.q1": "CI 파이프라인 속도가 느려지나요?",
    "faq.a1": "아니요, 파일당 평균 검증 시간은 2초 미만입니다. 병렬 비동기 검사로 최소한의 오버헤드를 보장합니다.",
    "faq.q2": "오탐은 어떻게 되나요?",
    "faq.a2": "페일 오픈 정책. 알 수 없는 함수는 건너뛰고 플래그를 지정하지 않습니다. 검증할 수 있는 것만 보고합니다.",
    "faq.q3": "어떤 언어가 지원되나요?",
    "faq.a3": "Python, JavaScript, TypeScript. 커뮤니티 피드백을 기반으로 곧 더 많은 언어가 제공될 예정입니다.",
    "faq.q4": "ESLint/Pylint와 어떻게 다른가요?",
    "faq.a4": "그것들은 코드 스타일을 검사합니다. 우리는 AI 생성 API가 실제로 존재하는지 확인합니다.",
    "faq.q5": "오프라인에서 사용할 수 있나요?",
    "faq.a5": "구문 및 서명 검사는 오프라인에서 작동합니다. 가져오기 검사는 레지스트리 조회를 위해 네트워크가 필요합니다(캐싱 포함).",
    "faq.q6": "사용해도 안전한가요?",
    "faq.a6": "읽기 전용 검증. 코드를 실행하지 않습니다. 안전을 위해 허용 목록 stdlib 모듈로 제한됩니다.",
    "comparison.title": "왜 AI Hallucination Firewall인가?",
    "comparison.subtitle": "AI 생성 코드 검증을 위해 특별히 제작되었습니다.",
    "comparison.feature": "기능",
    "comparison.firewall": "Hallucination Firewall",
    "comparison.linters": "ESLint/Pylint",
    "comparison.manual": "수동 검토",
    "comparison.row1": "환각 API 감지",
    "comparison.row2": "레지스트리 검증",
    "comparison.row3": "서명 검증",
    "comparison.row4": "모든 LLM과 작동",
    "comparison.row5": "자동 CI 통합",
    "comparison.row6": "제로 구성",
    "comparison.yes": "✓",
    "comparison.no": "✗",
    "comparison.sometimes": "때때로",
    "comparison.slow": "느림",
    "comparison.na": "N/A",
    "cta.title": "오늘 AI 환각 중지",
    "cta.subtitle": "오픈소스, MIT 라이선스, 설정 불필요. ChatGPT, Claude, Copilot 및 모든 LLM 출력과 작동.",
    "cta.github": "GitHub에서 스타",
    "cta.download": "v0.1.0 다운로드",
    "footer.title": "AI Hallucination Firewall v0.1.0",
    "footer.license": "MIT 라이선스",
    "footer.made_by": "제작자"
  }
};

// i18n function
function setLanguage(lang) {
  const trans = translations[lang] || translations.en;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (trans[key]) {
      el.textContent = trans[key];
    }
  });
  localStorage.setItem('lang', lang);
  document.documentElement.setAttribute('lang', lang);
}

// Theme toggle
function setTheme(theme) {
  if (theme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    document.querySelector('.theme-icon-dark').style.display = 'none';
    document.querySelector('.theme-icon-light').style.display = 'block';
  } else {
    document.documentElement.removeAttribute('data-theme');
    document.querySelector('.theme-icon-dark').style.display = 'block';
    document.querySelector('.theme-icon-light').style.display = 'none';
  }
  localStorage.setItem('theme', theme);
  lucide.createIcons();
}

// Demo validation animation
function runDemoValidation() {
  const demoContainer = document.getElementById('demoValidation');
  const runButton = document.getElementById('runDemoButton');
  const resultsPanel = document.getElementById('demoResults');

  // Disable button
  runButton.disabled = true;
  runButton.style.opacity = '0.5';

  // Add validating class
  demoContainer.classList.add('demo-validating');

  // Clear previous results
  resultsPanel.innerHTML = '<div class="text-muted text-sm">Running validation...</div>';

  // Simulate validation process
  setTimeout(() => {
    const trans = translations[localStorage.getItem('lang') || 'en'];
    resultsPanel.innerHTML = `
      <div class="demo-result-item flex items-start gap-3 p-3 rounded-lg" style="background-color: rgba(34,197,94,0.1);">
        <i data-lucide="check-circle" class="w-5 h-5 text-success shrink-0 mt-0.5"></i>
        <div class="flex-1">
          <div class="font-semibold text-sm" data-i18n="demo.result_syntax">${trans['demo.result_syntax']}</div>
          <div class="text-xs text-muted mt-1">
            <span class="px-2 py-0.5 rounded text-xs font-medium" style="background-color: rgba(34,197,94,0.2); color: var(--success);" data-i18n="demo.status_pass">${trans['demo.status_pass']}</span>
          </div>
        </div>
      </div>

      <div class="demo-result-item flex items-start gap-3 p-3 rounded-lg" style="background-color: rgba(239,68,68,0.1);">
        <i data-lucide="x-circle" class="w-5 h-5 text-danger shrink-0 mt-0.5"></i>
        <div class="flex-1">
          <div class="font-semibold text-sm" data-i18n="demo.result_import_fail">${trans['demo.result_import_fail']}</div>
          <div class="text-xs text-muted mt-1" data-i18n="demo.result_import_fail_desc">${trans['demo.result_import_fail_desc']}</div>
          <div class="mt-1">
            <span class="px-2 py-0.5 rounded text-xs font-medium" style="background-color: rgba(239,68,68,0.2); color: var(--danger);" data-i18n="demo.status_error">${trans['demo.status_error']}</span>
          </div>
        </div>
      </div>

      <div class="demo-result-item flex items-start gap-3 p-3 rounded-lg" style="background-color: rgba(239,68,68,0.1);">
        <i data-lucide="x-circle" class="w-5 h-5 text-danger shrink-0 mt-0.5"></i>
        <div class="flex-1">
          <div class="font-semibold text-sm" data-i18n="demo.result_import_fail2">${trans['demo.result_import_fail2']}</div>
          <div class="text-xs text-muted mt-1" data-i18n="demo.result_import_fail2_desc">${trans['demo.result_import_fail2_desc']}</div>
          <div class="mt-1">
            <span class="px-2 py-0.5 rounded text-xs font-medium" style="background-color: rgba(239,68,68,0.2); color: var(--danger);" data-i18n="demo.status_error">${trans['demo.status_error']}</span>
          </div>
        </div>
      </div>

      <div class="demo-result-item flex items-start gap-3 p-3 rounded-lg" style="background-color: rgba(239,68,68,0.1);">
        <i data-lucide="x-circle" class="w-5 h-5 text-danger shrink-0 mt-0.5"></i>
        <div class="flex-1">
          <div class="font-semibold text-sm" data-i18n="demo.result_signature">${trans['demo.result_signature']}</div>
          <div class="text-xs text-muted mt-1" data-i18n="demo.result_signature_desc">${trans['demo.result_signature_desc']}</div>
          <div class="mt-1">
            <span class="px-2 py-0.5 rounded text-xs font-medium" style="background-color: rgba(239,68,68,0.2); color: var(--danger);" data-i18n="demo.status_error">${trans['demo.status_error']}</span>
          </div>
        </div>
      </div>
    `;

    // Reinitialize icons for new elements
    lucide.createIcons();

    // Remove validating class
    demoContainer.classList.remove('demo-validating');

    // Re-enable button
    runButton.disabled = false;
    runButton.style.opacity = '1';
  }, 2000);
}

// Init on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  // Init theme
  const savedTheme = localStorage.getItem('theme') ||
    (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  setTheme(savedTheme);

  // Init language
  const savedLang = localStorage.getItem('lang') || 'en';
  document.getElementById('langSwitcher').value = savedLang;
  setLanguage(savedLang);

  // Theme toggle event
  document.getElementById('themeToggle').addEventListener('click', () => {
    const currentTheme = localStorage.getItem('theme') || 'dark';
    setTheme(currentTheme === 'dark' ? 'light' : 'dark');
  });

  // Language switcher event
  document.getElementById('langSwitcher').addEventListener('change', (e) => {
    setLanguage(e.target.value);
  });

  // Mobile menu toggle
  document.getElementById('mobileMenuBtn').addEventListener('click', () => {
    const menu = document.getElementById('mobileMenu');
    const btn = document.getElementById('mobileMenuBtn');
    menu.classList.toggle('active');
    btn.setAttribute('aria-expanded', menu.classList.contains('active'));
  });

  // Close mobile menu on link click
  document.querySelectorAll('#mobileMenu a').forEach(link => {
    link.addEventListener('click', () => {
      const btn = document.getElementById('mobileMenuBtn');
      document.getElementById('mobileMenu').classList.remove('active');
      btn.setAttribute('aria-expanded', 'false');
    });
  });

  // Demo validation button
  const demoButton = document.getElementById('runDemoButton');
  if (demoButton) {
    demoButton.addEventListener('click', runDemoValidation);
  }

  // Init Lucide icons
  lucide.createIcons();

  // Fade-in on scroll
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
  );

  document.querySelectorAll('.fade-up').forEach((el) => observer.observe(el));
});
