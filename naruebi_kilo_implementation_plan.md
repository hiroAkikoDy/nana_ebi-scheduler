# ナルエビちゃん実装計画：Kilo Code向け指示プロンプト集

*ベース文書：AI秘書「ナルエビちゃん」要件定義書（naruebi_requirements.md）*
*プロジェクト名（仮）：`nana_ebi-scheduler`*
*方式：GitHub Issue立て＋git worktreeでの並列実行（WIP上限2、既存の憲法と判例モデルの運用ルールに準拠）*
*新規スクリプト（scripts/, tests/）はPythonで実装する*

## 0. 前提の整理（重要）

要件定義書のアーキテクチャ（4章）上、**Google Calendar連携はClaude Code自身が公式remote MCPサーバーに直接接続する**方針です。つまりOAuthクライアントID/シークレットの設定やカスタムコネクタ登録は、コードを書く作業ではなく人間・Claude Code側の設定作業です。**Kilo Codeへの実装依頼には含めません**（Issue化しない）。

**リポジトリは新規作成**：`nana_ebi-scheduler`という名前で新規リポジトリを作成します（GOROman/nullevi03のフォークにはしない、既存のnanaka_farm_logにも混在させない）。理由は、nullevi03は他者のリポジトリで大きく方向性を変える前提のため、nanaka_farm_logは別プロジェクト（農場ログ）なので混ぜると責務が曖昧になるためです。

Kilo Codeが実際にコードとして書くべきものは、MVPの範囲では以下の3系統に絞られます。
1. 三世（boot.sh）ベースの起動基盤の動作確認・環境調整
2. Claude Code→Kilo Code CLIのヘッドレス呼び出しラッパー（timeout・出力パース、Python）
3. 会話ログ・動作確認のためのテスト/検証スクリプト（Python）

**実装練習の方針**：Issue #2のラッパー動作確認は、ダミータスクではなく実際のタスク（`nanaka_farm_log`リポジトリの説明をdocsに書き込む）で行います。認証が不要で、失敗しても実害がない題材のため、Kilo Code連携の最初の練習に適しています。

## 1. Issue分解と依存関係

| # | Issueタイトル | 依存 | 並列実行可否 |
|---|---|---|---|
| #0 | リポジトリ`nana_ebi-scheduler`の新規作成・初期構成 | なし | 不可（最初の一歩） |
| #1 | 三世ベースのTelegram Bot起動基盤をProプラン環境で動作確認 | #0 | 不可（後続Issueの土台） |
| #2 | Kilo Code CLIヘッドレス実行ラッパー（timeout・出力パース、Python） | #1 | #3と並列可 |
| #3 | 会話・起動ログの検証スクリプト（自己復旧ループの動作確認、Python） | #1 | #2と並列可 |
| #4 | Google Calendar MCP連携の疎通確認テスト（Claude Code側の設定完了後） | #1, 人間によるOAuth設定完了 | 単独 |
| #5 | READMEへのセットアップ手順・環境変数一覧の追記 | #1〜#4 | 単独（最後） |

**並列実行の波（WIP上限2 worktreeに準拠）**
- **Wave 0**：Issue #0 を単独で先行（リポジトリそのものがないと何も始まらない）
- **Wave 1**：Issue #1 を単独で先行（他の全Issueの前提のため）
- **Wave 2**：Issue #2・#3 を2並列のworktreeで同時実行（互いに独立、#1完了後すぐ着手可能）
- **Wave 3**：Issue #4（人間のOAuth設定完了を待つため、Wave 2と並行して待機扱いでもよい）
- **Wave 4**：Issue #5（全体が揃ってから）

## 2. 各Issueへの実行プロンプト

以下はそれぞれ `kilo run --auto "<プロンプト>"` に渡す想定のテキストです。Task.md方式を使う場合は、そのままTask.mdの本文として使えます。

### Issue #0：リポジトリ`nana_ebi-scheduler`の新規作成・初期構成
```
GitHub上に新規リポジトリ `nana_ebi-scheduler` を作成し、初期構成を整えてください（新規リポジトリとして作成。GOROman/nullevi03のフォークにはしない）。

やること：
1. GOROman/nullevi03 の boot.sh・CLAUDE.md・README.md を参考にしつつ、新規ファイルとしてコピー・配置（参考にした旨をREADMEに一言記載）
2. scripts/, tests/, docs/, logs/ ディレクトリを作成
3. .gitignore を作成し、logs/ と .env を除外
4. .env.example を作成（TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID のダミー値を記載）

完了条件：リポジトリが作成され、上記ファイル・ディレクトリ構成が揃っていること
```

### Issue #1：三世ベースの起動基盤確認
```
リポジトリ GOROman/nullevi03（ナルエビちゃん三世）をベースに、Claude Code Proプランでの動作確認を行ってください。

やること：
1. boot.sh を確認し、POSIX sh (#!/bin/sh) 準拠であることを検証（bash固有構文が混入していないかチェック）
2. `claude --dangerously-skip-permissions --channels plugin:telegram@claude-plugins-official -c` の起動をProプラン環境で確認
3. TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID を環境変数から読み込む形になっているか確認し、ハードコードされている箇所があれば環境変数化する
4. 異常終了時に5秒待って自動再起動するループが正しく動くことを確認するテストケースを用意する

制約：
- credentials は環境変数経由のみ。ハードコード禁止
- boot.sh 部分は POSIX sh のまま。bashに依存する変更はしない

完了条件：boot.shがProプラン環境で起動し、Telegram経由で最低1往復の会話ができること
```

### Issue #2：Kilo CLIヘッドレス呼び出しラッパー（Python）
```
Claude CodeのBashツールから `kilo run --auto "<タスク内容>"` を安全に呼び出すためのラッパースクリプトを、Pythonで実装してください（scripts/kilo_wrapper.py）。

背景：kilo run --auto はタスク完了後もプロセスが終了せずハングする既知の不具合が報告されている。Claude Code側のBash呼び出しが無期限にブロックされないようにする必要がある。

やること：
1. `subprocess`等でtimeout付きに `kilo run --auto "<プロンプト>"` を実行する関数を実装（タイムアウト秒数は引数で指定可能に）
2. 標準出力・終了コードを解析し、成功/失敗/タイムアウトの3状態を判定するロジックを実装
3. 失敗・タイムアウト時にはその旨を明確なフォーマットで返す（Claude Code側が次の判断をしやすい形式。JSON形式で {status, output, error} を返す）
4. ログをファイルに残す（logs/kilo_wrapper.log）

動作確認（実タスクでの練習）：
このラッパーを使って、実際に以下のタスクをKilo Codeに実行させてください（認証不要な実タスクなので、ダミーではなくこれで動作確認とする）。
- リポジトリ https://github.com/hiroAkikoDy/nanaka_farm_log の内容を確認し、docs/related_projects.md に「nanaka_farm_log：どんなリポジトリか」の簡単な説明を記入する

完了条件：上記の実タスクがラッパー経由で正常終了し、docs/related_projects.mdにnanaka_farm_logの説明が書き込まれること。加えて、タイムアウトを短く設定した場合にタイムアウト状態が正しく検出できることも確認する
```

### Issue #3：起動・自己復旧ログの検証スクリプト（Python）
```
boot.shの自己復旧ループ（異常終了→5秒待機→再起動）と、起動・再起動時のTelegramプッシュ通知（notify_telegram関数）が正しく動作しているかを検証するスクリプトを、Pythonで実装してください（tests/verify_boot.py）。

やること：
1. わざとプロセスを異常終了させ、5秒後に再起動されることを確認するテストケース
2. notify_telegram が起動・再起動のタイミングで正しく呼ばれることを確認するテストケース（Telegram側はモック/ダミーで可）
3. 検証結果をログファイルに残す

完了条件：異常終了→再起動→通知、の一連の流れが自動テストで再現・確認できること
```

### Issue #4：Google Calendar MCP疎通確認（人間のOAuth設定完了後）
```
前提：Google Calendar公式remote MCPサーバーへの接続は人間・Claude Code側で設定済み（OAuthクライアントID/シークレット登録済み）。このIssueではコードの新規実装ではなく、疎通確認のためのテストシナリオ作成のみを行ってください。

やること：
1. Telegram経由で「明日の予定を教えて」のような自然文を投げたときに、Claude CodeがGoogle Calendar MCP経由で正しく応答できるかの手動確認手順書を作成
2. 予定の照会・登録・変更、それぞれについて確認すべきケースを洗い出す

完了条件：確認手順書が用意され、Google Calendar連携が要件通り動くことを人間が確認できる状態になること
```

### Issue #5：README整備
```
これまでのIssue #1〜#4の内容を踏まえ、READMEにセットアップ手順・必要な環境変数一覧・既知の注意点（--dangerously-skip-permissionsのリスク、kilo run --autoのタイムアウト設定の必要性）を追記してください。
```

## 3. 実行時の注意

- WIP上限2を超えないよう、Wave 2（Issue #2・#3）以外は同時に2つ以上のworktreeを開かない
- Issue #4は人間のOAuth設定が終わるまで着手できないため、Wave 2と並行して「待機」状態にしておき、設定完了の合図があってから着手する
- 各Issue完了後は、Claude Code側でのレビュー（分解理解：diffを読み、気になる箇所だけ質問し返す）を経てからマージする
