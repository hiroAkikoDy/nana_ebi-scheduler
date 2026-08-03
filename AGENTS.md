# AGENTS.md（nana_ebi-scheduler 固有条例）

本ファイルは本プロジェクト固有の条例であり、グローバルCLAUDE.md
（憲法・全プロジェクト共通の運用規則）に優先しない。両者が矛盾する場合は
グローバルCLAUDE.mdに従う。

## プロジェクト概要

個人運用のAI秘書エージェント「ナルエビちゃん」。詳細は
`naruebi_requirements.md`（要件定義書）を正とする。
実装の進め方は`naruebi_kilo_implementation_plan.md`を参照。

## 実行環境（重要）

**本プロジェクトはWSL2（Ubuntu）上で稼働させる。Windowsネイティブでは運用しない。**

- 理由：boot.shの常時稼働ループはPCスリープの影響を受けにくいLinux環境の方が
  安定し、tmuxでのセッション維持もWSL2側でのみ想定している
- 移行手順は`docs/wsl2_migration.md`を参照
- Issue #0〜#3はWindowsネイティブ環境で実装・検証されていたことが
  2026-08-03に判明したため、この条項を新設した（`naruebi_requirements.md`の
  変更履歴も参照）

## boot.sh編集時の制約（GOROman/nullevi03「三世」由来）

- スクリプトはPOSIX sh（`#!/bin/sh`）で書くこと。bash固有構文
  （`[[`, `function`キーワード, `source`, `((`, 配列, `local`等）を
  持ち込まない
- 認証情報（`TELEGRAM_BOT_TOKEN`・`TELEGRAM_CHAT_ID`等）はboot.shに
  ハードコードせず、必ず環境変数経由で渡す
- `--dangerously-skip-permissions`を外す変更は挙動を大きく変えるため、
  実施前に必ずユーザー（弘晃さん）の確認を取ること

## 開発体制：二層エージェント

```
Claude Code（窓口・設計層）
  - ユーザーとの対話窓口（Telegram経由）
  - 要件整理・仕様設計・コードレビュー
  - Google Calendar公式remote MCPサーバーに直接接続（唯一の例外）
  - Bashツールで `kilo run --auto "<タスク内容>"` を実行し、実装を委任
  - 意思決定は人間（弘晃さん）に帰属
        ↓ ヘッドレス起動
Kilo Code CLI（実装層）
  - `--auto` モードで自律実行
  - Google Calendar以外のツール実行・コード実装
```

### クレジット節約方針

- Claude Code側は基本的に自分でツールを実行せず、ツールを使う作業は
  原則Kilo Codeに委任する
- **例外：Google Calendarのみ**、Claude Code自身が公式remote MCP
  サーバーに直接接続する（信頼性・安心感を優先した意図的な例外）

## Kilo Codeへのタスク受け渡し

- 指示は`tasks/`配下にMarkdownファイルとして作成する
- 完了報告は`work_reports/`配下にWork_Reportとして作成する
  （憲法第3条：Work_Reportは判例であり削除・改変しない）
- 完了の宣言はCIグリーンで裏取りする（憲法第4条）。CI未整備の間は、
  レビュー担当（Claude Code）が実際にコードを実行して検証する

## 参照

- 要件定義書：`naruebi_requirements.md`
- 実装計画・Issue分解：`naruebi_kilo_implementation_plan.md`
- WSL2移行手順：`docs/wsl2_migration.md`
- Google Calendar MCP疎通確認手順：`docs/calendar_mcp_verification.md`（Issue #4）
