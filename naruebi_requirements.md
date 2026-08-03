# AI秘書「ナルエビちゃん」要件定義書

*2026年7月時点 / 開発スタイル: Vibe Coding*
*一次情報源: https://github.com/GOROman/nullevi03（ナルエビちゃん三世）*
*プロジェクト名（仮）：`nana_ebi-scheduler`（新規リポジトリとして作成）*

## 1. 概要

個人運用のAI秘書エージェント「ナルエビちゃん」。ベースは公開リポジトリ（GOROman/nullevi03、ナルエビちゃん三世＝Claude CodeをTelegram Bot経由で常時稼働させる極小ラッパー）。

**現在のスコープはMVPに絞り込む**。実装の幅出し（SNS運用、性格拡張、外部システム連携等）は目標外とし、まずは「スケジュール管理を行うAI秘書」として動かすことを最優先とする。

## 2. 目的・コンセプト

- 人間の確認を起点に、日々の大量対話を通じて信頼を積み上げ、段階的に自律範囲を広げる「育成型」エージェント
- 現時点でのコアバリューは2つ：①Googleカレンダー連携によるスケジュール管理、②日常の相談相手
- 「Claude Codeを落とさず、外部チャット（Telegram）から常時呼び出せる状態を維持する」という三世の設計思想を踏襲

## 3. 現在のスコープ（MVP）

### 3.1 スケジュール管理機能
- Google Calendarとの連携が主軸
- 予定の照会・登録・変更をTelegram経由の対話で行えることを目指す
- 連携方式は**Google Calendar公式remote MCPサーバー**を採用する。Claude Code自身に直接接続させる方針で確定（信頼性・安心感を優先し、後述4.2のクレジット節約方針の例外として扱う）

### 3.2 相談相手機能
- 日常的な相談・壁打ち相手としての対話機能
- スケジュール管理と地続きで、雑談・相談から自然にタスクや予定の話に展開できることを想定

### 3.3 実行基盤
- 三世（Claude Code + Telegram Bot常時稼働ラッパー）をベースに、Google Calendar連携を追加する形で拡張

### 3.4 現時点でスコープ外
- SNS自動投稿・Xアカウント運用
- 性格拡張（パーソナリティ機能）
- MCP経由の外部システム連携（法務局API等）
- これらは「12. 現時点でスコープ外の構想」に整理し、優先度を下げる

## 4. 開発体制・アーキテクチャ方針

### 4.1 二層エージェント体制
本人の通常の開発ワークフロー（Claude=設計・レビュー、Kilo Code=実装、Task.md/Work_Report.mdのメールボックス方式）をこのAI秘書プロジェクトにも適用する。指示の受け渡しは、**Claude CodeがBashツールでKilo Code CLIをヘッドレス実行する方式**（例：`kilo run --auto "<タスク内容>"`）を採用する。ファイルベースのTask.md/Work_Report.mdの受け渡しより単純で、Claude Code側のツール呼び出しは「Kilo CLIを1回起動する」だけで済む

```
Claude Code（窓口・設計層）
  - ユーザーとの対話窓口（Telegram経由）
  - 要件整理・仕様設計・コードレビュー
  - Google Calendar公式remote MCPサーバーに直接接続（例外的にツール実行）
  - Bashツールで `kilo run --auto "<タスク内容>"` を実行し、Kilo Codeに実装を委任
  - 意思決定は人間（弘晃さん）に帰属
        ↓ ヘッドレス起動
Kilo Code CLI（実装層）
  - `--auto` モードで自律実行。タスク完了で自動終了
  - Google Calendar以外のツール実行・コード実装
```

### 4.2 クレジット節約方針
- Claude Code側は基本的に自分でツールを実行せず、**ツールを使う作業は原則Kilo Codeに命じる**運用とする
- Claude Codeの役割はあくまで「窓口としての対話」と「設計・指示出し」に絞り、Claude Codeの利用料（クレジット）消費を抑える
- **例外：Google Calendarのみ、Claude Code自身が公式remote MCPサーバーに直接接続する**。信頼性・安心感を優先した意図的な例外であり、クレジット消費が増える点は許容する。Google Calendar以外のツール利用は引き続きKilo Codeに委任する方針を維持

## 5. 非機能要件

| 項目 | 内容 |
|---|---|
| コスト | Claude Codeは**Proプラン**で運用（README記載の月200ドル＝Maxプラン前提ではない） |
| クレジット管理 | ツール呼び出しはKilo Codeに委任し、Claude Code側のクレジット消費を抑える方針 |
| 権限管理 | `--dangerously-skip-permissions` により確認プロンプトを全スキップして動作。リスクが大きいため運用上の注意が必要 |
| 認証情報管理 | `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` 等は環境変数経由で渡す。ハードコードしない方針 |
| 実装言語制約 | 三世のboot.sh部分はPOSIX sh (`#!/bin/sh`) 準拠。bash固有構文は持ち込まない |
| 可用性 | 異常終了時は5秒待機後に自動再起動する自己復旧ループ（三世由来） |

## 6. セットアップ手順

1. Claude Code（Proプラン）を導入する
2. Telegramアプリを導入し、BotFatherでBotを作成する
3. Claude Code Channelsを設定する（`claude-plugins-official` のTelegramプラグイン）
4. 環境変数（Telegramトークン等）を設定して起動する
5. Google Calendar公式remote MCPサーバーへの接続をClaude Code側で設定する（カスタムコネクタ、OAuth。**Kilo Codeへの実装依頼ではない**）
6. 実装練習として、Kilo Codeに認証不要なタスク（例：`nanaka_farm_log`リポジトリの内容を確認してdocsに説明を書き込む）を実行させ、Claude Code→Kilo Code連携の動作を確認する
7. あとはひたすら会話する（HITLで信頼を積み上げるフェーズ）

## 7. アーキテクチャ / リスクと注意事項

- **`--dangerously-skip-permissions` の運用リスク**: Claude Codeの安全確認プロンプトを全てスキップするフラグ。意図しない操作が無確認で走る可能性があり、外すかどうかは要検討
- **メモリ・状態管理は自前実装なし（三世由来）**: 会話の継続性はClaude Codeの `-c`（セッション継続）に依存
- **クレジット消費の設計**: Claude Code（窓口）とKilo Code（実装）の役割分担が崩れると、Claude Code側のクレジットを浪費するリスクがあるため、指示の出し方に注意が必要

## 8. 技術スタック一覧

| 領域 | 採用技術 |
|---|---|
| 対話実行基盤 | Claude Code CLI（Proプラン） |
| チャネル連携 | Claude Code Channels機能（`plugin:telegram@claude-plugins-official`） |
| Bot作成 | Telegram BotFather |
| 実装層 | Kilo Code（ツール実行・コード実装） |
| スケジュール連携 | Google Calendar公式remote MCPサーバー（Claude Codeに直接接続。カスタムコネクタでOAuthクライアントID/シークレットを設定） |
| 実装層の起動方式 | Claude CodeがBashツールで `kilo run --auto` をヘッドレス実行 |
| 起動制御 | POSIX sh 無限ループ + 5秒リトライ（三世由来） |

## 9. 未確定・要検討事項

- **Kilo CLIヘッドレス実行（`kilo run --auto`）の信頼性**：既知の不具合として、タスク完了後もプロセスが終了せずハングするケースが報告されている。Claude Code側のBash呼び出しが無期限にブロックされないよう、`timeout`コマンド等での上限時間設定が必要
- **Kilo CLI側の権限設定**：`--auto`モードがどこまで確認プロンプトをスキップするか（Claude Codeの`--dangerously-skip-permissions`に相当する設定があるか）の確認が必要。対話待ちで停止すると同様にハングしうる
- **出力の受け渡し形式**：`kilo run`の標準出力・終了コードをClaude Code側でどう解釈するか（成功/失敗判定、結果の要約形式）の設計
- `--dangerously-skip-permissions` を付けたまま運用する上でのガードレール要否
- 相談相手としての振る舞い（性格・トーン）をどこまで定義するか

## 10. 開発哲学（背景メモ）

- 手を動かして試行錯誤し、失敗から得られる知見を重視する学習スタイル
- 「動くものを作ってから分解理解する」Vibe Codingの考え方
- Claude=設計・Kilo Code=実装という役割分担は、通常の開発ワークフローと同じ思想の踏襲

## 11. JAXA MCP構想は別プロジェクトへ分離

JAXA MCP（Earth-Observation）を使った圃場の地表面温度・NDVI等の衛星データ取得構想は、**ナルエビちゃんとは別プロジェクトとして進める**ことに決定。

- 詳細は別途整理（Neo4jの既存資産：`Fude`ノードの座標データ、`AmedasStation`/`DailyNormalValue`、`Farm`/`SatelliteData`ノードは前セクションの調査で確認済み）
- ナルエビちゃん要件定義書としては、この話題はスコープ外として扱う

## 12. 現時点でスコープ外の構想（参考情報）

優先度を下げ、MVP完成後に再検討する項目。

- OpenAI Realtime API（Realtime-2）による音声対話・通訳機能
- Xの独立アカウント（@NullEvi03）としての自動投稿・自動運用、凍結対策
- MCP（Model Context Protocol）経由の外部システム連携（法務局API等）
- 「双極性機能」などの性格拡張
- Discord/iMessage等、Telegram以外のマルチチャネル対応
