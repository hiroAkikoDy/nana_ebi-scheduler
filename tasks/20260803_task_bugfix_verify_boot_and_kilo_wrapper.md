# Task：verify_boot.py・test_kilo_wrapper.pyのバグ修正

起点：判例/Work_Report(20260802_1903_issue2/3)/差し戻し

## 背景

Issue #2・#3のWork_Reportでは各テストが「PASS」と報告されていましたが、
Claude Code側で実際にテストを実行して検証したところ、2件のバグが
見つかりました。CI（`.github/workflows/ci.yml`）を導入する前に、
まずこの2件を直してグリーンな状態にする必要があります。

なお、本プロジェクトの実行環境は今後WSL2（Ubuntu）に統一します
（`AGENTS.md`・`docs/wsl2_migration.md`を参照）。今回の修正・動作確認も
WSL2上で行ってください。

## 1. tests/verify_boot.py：`_test_timeout_scenario`のロジック誤り

### 問題

`_test_timeout_scenario`は、boot.shの`claude --dangerously-skip-permissions ...`
の行を`exit 1`に置換したコピーを作って動作を検証していますが、
`exit`は**シェルスクリプト自体を終了させるコマンド**です。

元のboot.shでは、`claude ...`は外部プロセスの起動であり、そのプロセスが
終了しても親シェル（boot.sh自体）は生き続け、whileループの次の周
（「5秒後に再起動します」のメッセージ→`sleep 5`→再起動メッセージ）に
進みます。しかし`exit 1`に単純に置換すると、1周目でシェルスクリプト
自体が終了してしまい、ループが2周目に進む前に終わってしまいます。

実測結果：
```
Expected messages: ['boot.sh起動: ...', 'ナナエビちゃんが終了 → 5秒後に再起動します', 'ナナエビちゃんを再起動します']
Got: （空、1周目の起動メッセージのみで終了）
Timing: elapsed=1.93s, expected 5-12s
```

`sleep 5`にすら到達していません。これは環境依存ではなくロジックの
誤りなので、Windows・WSL2いずれで実行しても同じ結果になります。

### やること

`claude --dangerously-skip-permissions --channels plugin:telegram@claude-plugins-official -c`
の部分を、**シェル自体を終了させない外部コマンド**に置換してください。
例えば以下のような、即座に終了する別プロセスを使う方法があります。

```sh
sh -c 'exit 1'
```

（`sh -c '...'`はサブシェル＝別プロセスとして起動されるため、
そのサブシェルが`exit 1`しても親のboot.shコピーは終了せず、
whileループの続きが実行されます）

修正後、以下を満たすことを確認してください。
- ループが最低2周し、「起動メッセージ」「5秒後に再起動しますメッセージ」
  「再起動メッセージ」の3つ全てがstdoutに出力される
- `sleep 5`により実行時間が5秒以上になる（現状の`expected_min_time = 5`
  との整合を保つ）

## 2. tests/test_kilo_wrapper.py：`test_log_file_created`のパス不一致

### 問題

```python
def setUp(self):
    self.wrapper = kilo_wrapper.KiloWrapper(timeout_seconds=10)
    self.test_log = Path("logs/test_kilo_wrapper.log")
```

`self.wrapper`は`log_file`を指定していないため、実際には
デフォルトの`logs/kilo_wrapper.log`に書き込まれます。一方
`self.test_log`は`logs/test_kilo_wrapper.log`という別のパスを
見ているため、`test_log_file_created`は必ず失敗します。

### やること

`KiloWrapper`のインスタンス化時に、`self.test_log`と同じパスを
明示的に指定してください。

```python
self.wrapper = kilo_wrapper.KiloWrapper(timeout_seconds=10, log_file="logs/test_kilo_wrapper.log")
self.test_log = Path("logs/test_kilo_wrapper.log")
```

## 完了条件

- [ ] `python3 tests/verify_boot.py`を実行し、Overall: PASSになること
      （3つのテスト全てPASS。特にtiming_scenarioが実際に5秒以上かけて
      3つのメッセージ全てを出力することを確認する）
- [ ] `python3 -m unittest discover tests`（またはpytest）を実行し、
      test_kilo_wrapper.pyの5ケース全てが通過すること
- [ ] 上記の動作確認をWSL2（Ubuntu）上で実施したことをWork_Reportに明記する
- [ ] Work_Reportに「なぜ以前のWork_Reportで『PASS』と誤報告されたか」の
      原因分析を一言書くこと（今後の再発防止のため）
