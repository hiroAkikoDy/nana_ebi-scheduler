# Task：Issue #1差し戻し＋tests/verify_boot.py統合＋Issue #2内容充実

起点：判例/Work_Report(20260802_1903_issue1/2/3)/レビュー結果

## 前置き（Issue #2・#3について）

Issue #2・#3は前回の差し戻し指摘（push未了・_logメソッドの非効率実装・
timeout_scenarioの形骸化）にすべて的確に対応済みであることを確認しました。
特にverify_boot.pyのtimeout_scenarioを、boot.sh本体をコピーしclaude呼び出し
部分だけモックに差し替えて実際に動かす形に書き直した点はよい対応です。
この2件への追加指示はありません。

今回はIssue #1の差し戻しと、Issue #1・#3間のファイル重複の解消、
Issue #2の成果物の中身を充実させる作業をお願いします。

## 1. Issue #1：ブランチ分離とコミット

現状、Issue #1の成果物（tests/verify_boot.py等）がmainブランチ上で
直接staged状態のまま、コミットもpushもされていません。
他のIssueと同様、専用ブランチ・専用worktreeで作業してください。

やること：
1. mainブランチ上のstaged変更（tests/verify_boot.py）を一旦取り消す
   （git restore --staged、ファイル自体は後述の統合作業で使うため保持）
2. `issue-1-boot-verify` ブランチ・worktreeを新規作成する
3. そちらでIssue #1の成果物をコミットし、originにpushする

## 2. tests/verify_boot.py の重複解消

mainブランチ側のtests/verify_boot.py（BootScriptValidatorクラス、
POSIX準拠・環境変数・restart loopの静的チェックのみ、98行）と、
issue-3-boot-testブランチ側のtests/verify_boot.py（BootRestartTesterクラス、
静的チェック＋動的検証、182行）が、同名で別内容のファイルとして
それぞれのブランチに存在しています。このままではどちらかのブランチを
マージした時点でもう一方の内容が失われます。

やること：
1. issue-3-boot-test側の内容（動的検証を含む方）を正とし、
   issue-1-boot-verify側では同名の新規ファイルを作らないでください
2. Issue #1のWork_Report・完了報告では、
   「boot.shの検証はIssue #3のtests/verify_boot.pyに統合済み」と明記し、
   Issue #1固有の確認結果（POSIX準拠であることの目視確認結果など）は
   Work_Reportの文章として残す形にしてください（新規Pythonファイルは不要）

## 3. Issue #2：docs/related_projects.md の内容充実

現在の内容が「(詳細は確認中)」のままで止まっています。

やること：
1. https://github.com/hiroAkikoDy/nanaka_farm_log の内容を確認し、
   「nanaka_farm_log：どんなリポジトリか」の説明を実際に記入する
   （実装計画書の完了条件に明記されている元々の要件です）
2. 「(詳細は確認中)」のプレースホルダーを削除する

## 今回のtaskに含めないこと（人間側で対応するため）

以下は環境構築が必要でKilo Codeの作業範囲を超えるため、今回のtaskには
含めません。弘晃さん側で対応・判断します。
- Claude Code Proプラン環境でのboot.sh起動確認（Issue #1完了条件の一部）
- Telegram Bot経由の実会話確認（Issue #1完了条件の一部）
- kiloコマンドのインストール、それに伴うIssue #2の実タスク実行確認・
  タイムアウト実機確認
- CI（.github/workflows/）が未設定な件（別途Issue化を検討中）

## 完了条件

- [ ] issue-1-boot-verifyブランチが作成され、push済みであること
- [ ] tests/verify_boot.pyがリポジトリ全体で1つに統合されていること
      （main・issue-1-boot-verify・issue-3-boot-testの間で内容が矛盾しないこと）
- [ ] docs/related_projects.mdにnanaka_farm_logの実質的な説明が
      書かれていること（「確認中」のプレースホルダーが残っていないこと）
- [ ] Work_Reportを作成し、上記の対応内容と、対応できなかった項目
      （環境構築系）を正直に記載すること
