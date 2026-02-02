# MODULE: boundary (uraha-m1)

## 目的
- 「境界」テンプレ boundary_v0 を実行し、HTML画面とJSON APIの両方を提供する
- 実行結果を JSONL に追記して保存する（監査・学習・将来統合のため）

## 提供I/F（外部仕様）
### HTML
- GET  /boundary : 入力フォーム表示（200）
- POST /boundary : 入力→simulate→結果表示＋ログ保存（200 or 400）

### JSON API（将来フロント統合用）
- POST /api/boundary : 入力→simulate→JSON返却＋ログ保存（200 or 400）

レスポンス例（200）
- ok: true
- pi_t, o_t1_pred, notes
- saved_to: ログ保存先（※方針：絶対パス or 相対パスどちらかに統一）

レスポンス例（400）
- ok: false
- error
- input（クリーニング後）

## 依存（このモジュールが使うもの）
- StepInput（契約）
- simulate_step（ドメインロジック）
- append_event（jsonl追記）

## ログ仕様（events.jsonl）
- 1リクエスト = 1行（JSONL）
- event最低限フィールド：
  - app, template, ts, input, output
- 追加フィールド（推奨）：
  - ok, source, route, endpoint, method

## 保存先（重要：ブレやすい）
- create_app() で app.config["EVENT_LOG_PATH"] を設定する
- routes_boundary.py は current_app.config["EVENT_LOG_PATH"] を必ず参照する
- 可能なら EVENT_LOG_PATH は「絶対パス」で設定してブレを潰す

## 制約
- 既存のルート名・URLは変えない
- 大規模リファクタ禁止（最小差分）
- 例外時は 4xx を返す（APIは400）
- ログは壊さない（キーを減らさない）

## Done（受け入れ条件）
1) GET /health が 200
2) GET /boundary が 200（HTML）
3) POST /api/boundary が 200（JSON）
4) instance/events.jsonl に追記される
5) python -m compileall app が通る