# WSL2移行手順書

*対象：nana_ebi-scheduler の実行環境をWindowsネイティブ（Git Bash/MSYS2）からWSL2（Ubuntu）へ移行する*
*背景：要件定義前の打ち合わせでWSL2推奨が合意されていたが、`naruebi_requirements.md`への反映漏れにより、Issue #0〜#3はWindowsネイティブ環境で実装・検証されていた（2026-08-03発見、詳細は`naruebi_requirements.md`の変更履歴を参照）*

## 0. 前提確認（実施済み・Windows側/Git Bashで実行）

以下は2026-08-03時点で確認済み。`wsl`コマンド自体はWindows側にしか
存在しないため、Ubuntu側のターミナルに入った後に打っても動かない。

```
$ wsl --list --verbose
NAME              STATE      VERSION
* docker-desktop  Stopped    2
  Ubuntu          Stopped    2

$ wsl -d Ubuntu -e bash -c "cat /etc/os-release"
PRETTY_NAME="Ubuntu 26.04 LTS"
```

WSL2・Ubuntu 26.04 LTSディストリビューションは既にインストール済み。
新規インストール作業は不要。

### 導入済みツール（WSL2 Ubuntu側で`which`確認済み）

| ツール | 状態 |
|---|---|
| python3 | `/usr/bin/python3`（Ubuntuネイティブ、OK） |
| git | `/usr/bin/git`（Ubuntuネイティブ、OK） |
| tmux | `/usr/bin/tmux`（Ubuntuネイティブ、OK） |
| curl | `/usr/bin/curl`（Ubuntuネイティブ、OK） |
| npm | `/mnt/c/Program Files/nodejs/npm`（**Windows側を参照。要修正**） |
| claude | `/mnt/c/Users/Koga Hiroaki/AppData/Roaming/npm/claude`（**Windows側を参照。要修正**） |
| kilo | 未導入 |
| node | 未導入（PATHに存在せず） |

npm・claudeがWindows側バイナリを参照している状態では、
打ち合わせで期待していた「Claude CodeはLinux環境の方が安定動作する」
というメリットを実質的に得られない。Node.js・claude CLI・Kilo CLIは
WSL2内にネイティブでインストールし直す必要がある。

## 1. Node.js・CLIツールのネイティブインストール

**(Windows側/Git Bash)** まずUbuntuシェルに入る。

```bash
wsl -d Ubuntu
```

**(ここから先はWSL2/Ubuntu側)** プロンプトが`koga_hiroaki@...:~$`に
変わったことを確認してから、以下を実行する。

```bash
# nvm経由でNode.jsをインストール（WSL2内で完結させる）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install --lts

# PATHがWSL2ネイティブのnodeを指すことを確認
which node    # /home/koga_hiroaki/.nvm/... になっていること
which npm     # 同上

# Claude Code CLIをWSL2側にインストール
npm install -g @anthropic-ai/claude-code
which claude  # Windows側(/mnt/c/...)ではなくWSL2側を指すこと

# Kilo CLIをインストール（未導入だったもの）
npm install -g @kilocode/cli
kilo --help
```

## 2. グローバル設定（~/.claude/）の移行

Claude Codeのグローバル設定は、リポジトリではなくユーザーのホーム
ディレクトリ（`~/.claude/`）に置かれる。以下はWindows側→WSL2側への
移行手順で、2026-08-03に動作確認済み（MD5チェックサム一致）。

### 2.1 CLAUDE.md（Git Bash側から実行）

```bash
wsl -d Ubuntu -e bash -c "mkdir -p ~/.claude"
cat "/c/Users/Koga Hiroaki/.claude/CLAUDE.md" | wsl -d Ubuntu -e bash -c "cat > ~/.claude/CLAUDE.md"

# 検証（両方のMD5が一致すればOK）
wsl -d Ubuntu -e bash -c "md5sum ~/.claude/CLAUDE.md"
md5sum "/c/Users/Koga Hiroaki/.claude/CLAUDE.md"
```

### 2.2 スラッシュコマンド定義（.claude/commands/）（Windows側/Git Bash）

```bash
tar -C "/c/Users/Koga Hiroaki/.claude" -cf - commands | wsl -d Ubuntu -e bash -c "mkdir -p ~/.claude && tar -C ~/.claude -xf -"
```

`/spec:feature` `/spec:lite` `/spec:bug` `/spec:review` `/spec:status`
の4コマンドが対象。

### 2.3 settings.json は意図的にコピーしない

`settings.json`のpermissions.allowには、Windows形式のパス
（例：`Read(//c/Users/Koga Hiroaki/.claude/**)`）や、他プロジェクト
（nanaka-fmd-lineage等）向けの許可ルールが多数含まれている。
WSL2側にそのままコピーすると、パス形式の不一致（WSL2では`/mnt/c/...`）
で一部のルールが機能しないほか、無関係なプロジェクトの許可ルールを
持ち込むことになる。

**方針**：WSL2側では`settings.json`を空の状態から始め、
このプロジェクトで実際に必要になった許可ルールのみを都度追加する。

## 3. リポジトリのclone（WSL2/Ubuntu側）

WSL2のネイティブファイルシステム内（`/mnt/c/...`経由ではなく`~/`配下）
にcloneする。`/mnt/c/`経由だとWindows-WSL2間のファイルI/Oオーバーヘッドで
動作が遅くなるため。1章と同じUbuntuシェルの中で続けて実行してよい
（既にUbuntu側にいれば`wsl -d Ubuntu`は不要）。

```bash
cd ~
git clone https://github.com/hiroAkikoDy/nana_ebi-scheduler.git
cd nana_ebi-scheduler
```

## 4. .envの再設定（WSL2/Ubuntu側）

`.env`は`.gitignore`で除外されているため、Windows側の`.env`は
そのままではWSL2側に持ち込まれない（gitに乗らないため）。

**認証情報の再入力は弘晃さんご自身の手で行ってください**
（Claude Code・Kilo Codeに認証情報を扱わせないという方針を維持するため）。

```bash
cp .env.example .env
# .envを編集し、TELEGRAM_BOT_TOKEN・TELEGRAM_CHAT_IDを実際の値に置き換える
```

## 5. Kilo CLIの認証設定（WSL2/Ubuntu側）

```bash
kilo
/connect
# Z.ai のAPIキーを登録
```

## 6. 動作確認（WSL2/Ubuntu側）

```bash
# boot.shの疎通確認
TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=xxx sh boot.sh

# 既存の検証スクリプトをWSL2上で再実行
python3 tests/verify_boot.py
python3 -m unittest discover tests

# CI導入後は、CI側でもubuntu-latestランナーで同じテストを実行する想定
```

**注意**：`tests/verify_boot.py`の`_test_timeout_scenario`と
`tests/test_kilo_wrapper.py`の`test_log_file_created`には
既知のバグがあり、WSL2上で実行しても失敗する（2026-08-03、
Windows環境での実行時に発見。ロジックの誤りのため環境を問わず失敗する）。
これらはWSL2移行とは別に、Kilo Codeへの修正依頼で対応する。

## 7. tmuxでの常時稼働（WSL2/Ubuntu側）

```bash
tmux new-session -d -s nana_ebi
tmux send-keys -t nana_ebi "cd ~/nana_ebi-scheduler && sh boot.sh" Enter
tmux capture-pane -t nana_ebi -p
```

## 8. Windowsのスリープ設定確認（Windows側/PowerShell）

boot.shをWSL2上で常時稼働させる場合、Windows本体がスリープすると
WSL2ごと停止する。打ち合わせ時の合意通り、スリープを無効化する。
これはUbuntu側ではなく、Windowsのスタートメニューから
「PowerShell」を開いて実行する。

```powershell
# PowerShell（Windows側）で確認
powercfg /query SCHEME_CURRENT SUB_SLEEP
```

## 変更履歴

| 日付 | 内容 |
|---|---|
| 2026-08-03 | 初版作成。WSL2/Ubuntu 26.04 LTSの導入状況調査、CLAUDE.md・commands/のコピー手順を実機検証（MD5一致）の上で記載 |
