<!-- precedent_id: (採番不要・ingest側で付与)
     source_type: experience
     report_schema: v2
     project: nana_ebi-scheduler
     tags: bugfix,test,verify_boot,kilo_wrapper,wsl2 -->
### 完了報告：verify_boot.py・test_kilo_wrapper.pyのバグ修正
実施日時：2026-08-03 16:41
目標：CI導入前に2件のテストバグを修正し、グリーンな状態にする

## 変更ファイル一覧
| ファイル | 変更内容 | ブランチ |
|---|---|---|
| tests/verify_boot.py | _test_timeout_scenarioのロジック修正（3点） | issue-3-boot-test |
| tests/test_kilo_wrapper.py | ログファイルパス修正・importパス修正 | issue-2-kilo-wrapper |

## 修正内容

### Bug 1: tests/verify_boot.py の _test_timeout_scenario（3点修正）

1. **exit 1 → sh -c 'exit 1'**
   - 問題: `exit 1`はboot.shコピーのシェル自体を終了させ、whileループが2周目に進まなかった
   - 修正: `sh -c 'exit 1'`（サブシェル＝別プロセス）に置換し、親シェルが継続するようにした

2. **notify_telegram関数のecho化**
   - 問題: boot.shのnotify_telegramはcurl出力を`> /dev/null 2>&1`で抑制するため、メッセージがstdoutに出力されず、テストで検出できなかった
   - 修正: boot.shコピーのnotify_telegram関数をechoベースに置換（行単位パースで安全に置換）

3. **subprocess.run → subprocess.Popen**
   - 問題: 無限ループのboot.shコピーをtimeout付きで実行するとTimeoutExpired例外でstdoutが取得できない
   - 修正: Popen + communicate(timeout=8)で実行し、timeout時にkillしてからstdoutを取得

### Bug 2: tests/test_kilo_wrapper.py（2点修正）

1. **ログファイルパス不一致**
   - 問題: KiloWrapperのデフォルトlog_fileは`logs/kilo_wrapper.log`だが、test_logは`logs/test_kilo_wrapper.log`を見ていた
   - 修正: setUpで`log_file=str(self.test_log)`を明示的に指定

2. **ModuleNotFoundError**
   - 問題: `import kilo_wrapper`が失敗（scripts/がsys.pathに含まれていない）
   - 修正: `sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))`を追加

## 発生したエラーと対処
| # | エラー内容 | 原因 | 対処法 |
|---|---|---|---|
| 1 | exit 1でシェル自体が終了 | exitはプロセス終了コマンド | sh -c 'exit 1'に置換 |
| 2 | notify_telegramメッセージがstdoutに出ない | curl出力が/dev/nullへリダイレクト | echoベースに置換 |
| 3 | 正規表現置換が部分的失敗 | ${TELEGRAM_BOT_TOKEN}内の}にマッチ | 行単位パースに変更 |
| 4 | test_log_file_createdが必ず失敗 | ログファイルパスの不一致 | log_fileを明示指定 |
| 5 | import kilo_wrapperが失敗 | scripts/がsys.pathにない | sys.path.insertを追加 |

## Git操作
- issue-3-boot-testブランチ：
  - コミットID: 0367b45
  - push状況：完了
- issue-2-kilo-wrapperブランチ：
  - コミットID: 5a48af4
  - push状況：完了
- CIステータス：未実行（CI未設定）

## 動作確認結果（WSL2 Ubuntu上で実施）

### verify_boot.py
```
Running notify_telegram function... PASS
Running restart loop structure... PASS
Running timeout scenario... PASS
--------------------------------------------------
Overall: PASS
```
- timeout scenario: 3つのメッセージ全てがstdoutに出力されることを確認
- sleep 5により実行時間が5秒以上になることを確認

### test_kilo_wrapper.py
```
test_execute_kilo_task_failure ... ok
test_execute_kilo_task_not_found ... ok
test_execute_kilo_task_success ... ok
test_execute_kilo_task_timeout ... ok
test_log_file_created ... ok
----------------------------------------------------------------------
Ran 5 tests in 0.297s
OK
```
- 全5ケース通過

## 完了条件チェック
- [x] python3 tests/verify_boot.pyを実行し、Overall: PASSになること
- [x] python3 -m unittest discover testsを実行し、test_kilo_wrapper.pyの5ケース全てが通過すること
- [x] 上記の動作確認をWSL2（Ubuntu）上で実施したことをWork_Reportに明記する
- [x] Work_Reportに「なぜ以前のWork_Reportで『PASS』と誤報告されたか」の原因分析を書くこと

## 車検結果（受け入れ基準と照合）
├── CIグリーン：[?]（CI未設定・別途Issue化検討中）
├── pytest：全8件通過（verify_boot: 3件 + test_kilo_wrapper: 5件）[○]
├── セキュリティ（分類A）：[○]
├── 型アノテーション：[—]（テストコードのみ）
└── テストを弱める変更なし：[○]

## セキュリティ確認
├── 外部APIへの意図しない送信：[なし]
├── ハードコードされたシークレット：[なし]
└── 入力値のバリデーション：[—]（テストコードのみ）

## なぜ以前のWork_Reportで「PASS」と誤報告されたか（原因分析）

前回のWork_Report（20260802_1903）では、Windows環境（CP932エンコーディング）
でテストを実行し、UnicodeEncodeError等の環境固有のエラーに遭遇した後、
エラーが出ない設定に変更して再実行し「PASS」と報告した。しかし実際には、
以下の理由で「PASS」と判定されるべきでなかったテストが誤って通過していた：

1. **_test_timeout_scenario**: `exit 1`置換により1周目でシェルが終了し、
   期待メッセージが出力されなかったが、Windows環境での実行時は
   CP932のエンコーディング問題に気を取られ、テストロジック自体の
   正しさを検証しなかった。テストが「通った」と言う前に、
   期待されるメッセージが実際にstdoutに出力されているかを確認すべきだった。

2. **test_log_file_created**: ログファイルパスの不一致により
   本来失敗するべきテストだったが、unittest discoverではなく
   個別にテストを実行した際に、importエラーでテストがロードされず、
   「失敗」ではなく「エラー」として扱われたため、問題に気づかなかった。

**再発防止策**: 今後はテスト実行時に「期待される出力が実際に出力されているか」を
ログで確認し、CI（GitHub Actions）を導入して環境に依存しない自動検証を行う。

## 学習ポイント・次のステップへの展望
- `exit`と`sh -c 'exit 1'`の違い（プロセス終了 vs サブシェル終了）を学習
- テストの「通過」は出力内容の実証確認で裏付けるべき
- CI（.github/workflows/ci.yml）の早期導入が望ましい

## 起点
起点：判例/Work_Report(20260802_1903_issue2/3)/差し戻し

## Claudeへの質問・相談事項
なし