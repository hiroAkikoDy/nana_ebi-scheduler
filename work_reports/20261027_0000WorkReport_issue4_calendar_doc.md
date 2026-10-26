<!-- precedent_id: (採番不要・ingest側で付与)
     source_type: experience
     report_schema: v2
     project: nana_ebi-scheduler
     tags: issue4,google-calendar,mcp,verification,docs -->
### 完了報告：Issue #4 Google Calendar MCP疎通確認手順書の作成
実施日時：2026-10-27
目標：OAuth設定完了後に弘晃さんが実施する、Google Calendar MCP疎通確認の手順書を作成する（`tasks/20260803_task_issue4_calendar_doc.md`）

**注記（重要）**：**このtaskでは実際の疎通確認は行っていない。**
Google Calendar公式remote MCPサーバーのOAuth設定が未完了のため、今回の範囲は
手順書の作成のみ。Google Calendar MCPへの接続・予定の照会/登録/変更/削除は
一切実行していない。手順書に沿った疎通確認は、OAuth設定完了後に弘晃さんが実施する。

## 変更ファイル一覧

| ファイル | 種別 |
|---|---|
| `docs/calendar_mcp_verification.md` | 新規作成 |
| `work_reports/20261027_0000WorkReport_issue4_calendar_doc.md` | 新規作成（本ファイル） |

コードの変更はなし。git commit・pushは行っていない。

## やったこと

`docs/calendar_mcp_verification.md`を新規作成。構成は以下のとおり。

- **0章 前提条件**：Telegramペアリング・OAuth認可・`/mcp`での`connected`確認・タイムゾーン（JST）確認。テスト予定のタイトルに`【疎通テスト】`を付ける、変更・削除の対象は手動登録した準備用予定に限定する、等のテストデータ運用
- **1章 共通の期待動作（C-1〜C-7）**：Telegramへの応答、実データとの一致（捏造しない）、相対日付の具体化、JST、書き込み前の確認、書き込み後の報告、Kilo Codeへ委任しないこと
- **2章 照会（Q-1〜Q-9）**：日付指定（明日・今日・具体日付）、期間指定（来週）、空き時間、キーワード検索、場所の照会、終日予定、予定なしの日
- **3章 登録（R-1〜R-9）**：日時・タイトル指定、場所指定・終了時刻省略、曖昧な日時（「来週の月曜」）、終日、繰り返し（毎週・毎月、終了日あり）、既存予定との重複、日時不明、過去日時
- **4章 変更・削除**：
  - 変更（U-1〜U-7）：時刻変更、日付移動、同名予定が複数ある場合の聞き返し、単発/繰り返しの区別、繰り返しの1回だけ変更、タイトル変更、該当なし
  - 削除（D-1〜D-6）：確認付きキャンセル、確認段階での中止、複数該当時の聞き返し、繰り返しの1回だけ削除、シリーズ全体削除、一括削除の確認
- **5章 異常系（E-1〜E-2、任意）**：MCP切断時の応答、boot.sh再起動後の接続維持
- **6章 後片付け**、**7章 結果記録表**

各ケースに「入力（Telegramに投げる文面）」「期待される動作」「確認方法（Google Calendar側で目視確認する項目）」の3列を設けた。

## 設計上の判断

| # | 判断 | 理由 |
|---|---|---|
| 1 | 削除・曖昧な変更では「Telegram上での確認」を期待動作とした（C-5） | `--dangerously-skip-permissions`稼働のため、誤削除の歯止めがナルエビちゃん自身の確認しかない。確認なしで削除された場合はNGとし、運用ルールへの追記を検討する旨を明記 |
| 2 | 変更・削除の対象は、登録ケースの結果ではなく事前に手動登録した準備用予定とした | 登録ケースがNGでも変更・削除ケースを独立して確認できるようにするため |
| 3 | 異常系（E-1, E-2）は任意扱いとした | タスクの完了条件外だが、OAuth/MCP接続トラブルの切り分けに役立つため |

## 完了条件チェック（`tasks/20260803_task_issue4_calendar_doc.md`照合）

- [x] `docs/calendar_mcp_verification.md`が作成されていること
- [x] 照会・登録・変更（削除含む）の3種類それぞれについて、具体的な確認ケースが列挙されていること
- [x] 各ケースに入力文面・期待動作・確認方法が明記されていること
- [x] Work_Reportを作成すること（このtaskでは実際の疎通確認は行っていない旨を明記する）

## 次のステップ

- 人間・Claude Code側でGoogle Calendar公式remote MCPサーバーのOAuth設定を完了させる
- 前提としてTelegram Channelsのペアリング（`20260803_1902WorkReport_wsl2_migration_progress.md`でブロッカー）の解消も必要
- 設定完了後、弘晃さんが本手順書に沿って疎通確認を実施し、結果をWork_Reportに記録する

## 起点

起点：計画/naruebi_kilo_implementation_plan.md#4/採用
