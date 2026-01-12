from __future__ import annotations  # R1: 型注釈で前方参照を安定させ、契約を読みやすくする

from dataclasses import dataclass  # R2: “契約”を構造体として固定する
from typing import Any, Dict, List, Literal, Mapping, Optional  # R3: 依存しない最小型で表現する


# R4: 時刻tでの「隠れ状態 s_t」を汎用的に表す（テーマ別にキーが変わってよい）
State = Mapping[str, Any]  # R4: 例: {"vulnerability": 2, "agency": 1}


# R5: 時刻tでの「観測 o_t」を汎用的に表す（外部入力＋身体＋結果）
Obs = Mapping[str, Any]  # R5: 例: {"cue": 1, "craving": 7}


# R6: 方策（policy）の最小表現（文字列IDで扱う）
PolicyId = str  # R6: 例: "assert", "withdraw", "pay", "delay"


# R7: 好み P(o) の最小表現（望ましい観測の重み付け）
Prefs = Mapping[str, float]  # R7: 例: {"safe": 0.8, "connect": 0.2}


# R8: 精度（precision）の最小表現（方策選択の確信度）
Precision = Mapping[str, float]  # R8: 例: {"policy": 1.5}


@dataclass(frozen=True)  # R9: コアが参照する“1ステップ入力”を固定する
class StepInput:  # R9: DBN-FEPを回す最小の入力
    s_t: State  # R10: 隠れ状態（推定値でも可）
    o_t: Obs  # R11: 観測（ユーザー入力＋センサー＋状況）
    prefs: Prefs  # R12: 好み（長期/短期、安全/つながり等）
    precision: Precision  # R13: 精度（ロックイン/柔軟性の表現）


@dataclass(frozen=True)  # R14: コアが返す“1ステップ出力”を固定する
class StepOutput:  # R14: 次の観測・推奨方策・ログを返す
    pi_t: PolicyId  # R15: 選ばれた方策ID
    o_t1_pred: Dict[str, Any]  # R16: 次時刻の観測予測（まずはダミーで良い）
    notes: List[str]  # R17: 介入案や説明（まずは文字列で良い）