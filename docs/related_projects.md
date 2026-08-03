# 関連プロジェクト

## nanaka_farm_log

ナナカファームの農業記録システム。GitHub: https://github.com/hiroAkikoDy/nanaka_farm_log

### 概要
同じ所有者（hiroAkikoDy）の個人プロジェクトで、農作業記録・収穫記録を管理するシステム。
ナルエビちゃん（nana_ebi-scheduler）とは独立した別プロジェクトだが、Kilo Code連携の動作確認用タスク（Issue #2）の題材として使用している。

### アーキテクチャ
- **入力UI**: HTMLベースのローカルアプリ（サーバー不要）
  - `nanaka_farm_log.html`: 農作業記録入力（メイン）
  - `nanaka_farm_harvest.html`: 収穫記録入力
  - `nanaka_farm_lots.html`: 栽培ロット確認ビューア（参照のみ）
- **データ保存**: GitHub Gist（JSON形式）にクラウドバックアップ
- **パイプライン**: `nanaka_farm_pipeline.py` がGistからNeo4jにデータを取り込む
- **分析基盤**: Neo4j（グラフDB）をSingle Source of Truthとして使用
- **レポート出力**: 日報HTML（Google Drive同期）・週報（Notion自動生成）

### データフロー
```
入力UI（HTML）→ GitHub Gist（クラウド）→ Neo4j（分析）→ Notion/HTML（閲覧・共有）
```

### Neo4jグラフスキーマ
- WorkSession（作業セッション）が中心ノード
- Date / TaskType / Field / Worker / HarvestRecord とリレーション
- HarvestRecord は CropLot（栽培ロット）に紐付け
- 後工程比率分析・農薬散布経過日数チェック・歩留まり率時系列分析などのクエリが実装済み