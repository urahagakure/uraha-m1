from __future__ import annotations  # R3-1: 将来の型注釈の前方参照を安定させる

from typing import Any, Dict, List  # R3-1: 返却値の辞書・配列の型を明示する

from app.core.contracts import StepInput, StepOutput  # R3-1: 契約（contracts）に従う


def _get_int(o: Dict[str, Any], key: str, default: int = 0) -> int:  # R3-3: 単純ルール用に観測から整数を安全に取り出す
    v = o.get(key, default)  # R3-3: キーが無い場合は default を使う
    try:  # R3-3: 入力が文字列でも整数化できるなら整数化する
        return int(v)  # R3-3: 整数化して返す
    except (TypeError, ValueError):  # R3-3: 整数化できない場合
        return default  # R3-3: default を返す


def simulate_step(x: StepInput) -> StepOutput:  # R3-1: StepInput→StepOutput の1-stepシミュレータ
    o_t = dict(x.o_t)  # R3-3: 観測を編集しやすいように dict にコピーする

    threat = _get_int(o_t, "threat", 0)  # R3-2: 境界テンプレの暫定入力（脅威推定）を読む
    body_alarm = _get_int(o_t, "body_alarm", 0)  # R3-2: 身体警報（緊張など）を読む
    need_clarity = _get_int(o_t, "need_clarity", 0)  # R3-2: ニーズ明確度（境界文の材料）を読む
    energy = _get_int(o_t, "energy", 0)  # R3-2: 余力（睡眠/疲労の代理）を読む

    notes: List[str] = []  # R3-1: 介入案・説明の出力領域を用意する

    if threat >= 2 or body_alarm >= 2:  # R3-2: 高脅威/高警報なら撤退（withdraw）を優先する
        pi_t = "withdraw"  # R3-2: 方策ID withdraw を返す
        notes.append("脅威/身体警報が高いので、まず距離を取る方策（withdraw）を推奨します。")  # R3-2: 介入案（説明可能な文）
        notes.append("具体例：返答保留、退出、場所を変える、第三者同席など。")  # R3-2: 具体行動の候補
    elif need_clarity >= 2 and energy >= 1:  # R3-2: ニーズが明確で余力があるなら主張（assert）を選ぶ
        pi_t = "assert"  # R3-2: 方策ID assert を返す
        notes.append("ニーズが明確で余力もあるため、主張（assert）を推奨します。")  # R3-2: 介入案
        notes.append("テンプレ：Iメッセージ＋要望＋代替案＋期限（例：『今は難しい。明日なら可能』）。")  # R3-2: 境界文の雛形
    else:  # R3-2: それ以外は迎合（comply）に倒す（※後で改善対象）
        pi_t = "comply"  # R3-2: 方策ID comply を返す
        notes.append("情報が不足しているため暫定で迎合（comply）を返します（後で改善します）。")  # R3-3: ダミーであることを明示する
        notes.append("改善案：need_clarity を上げる（紙に書く/テンプレ入力）→ assert を選べるようにする。")  # R3-3: 次の介入の方向性

    # R3-3: 次の観測予測（o_{t+1}）は現段階ではダミーでよい（説明可能性を優先）
    o_t1_pred: Dict[str, Any] = {  # R3-1: 予測観測を辞書で返す
        "predicted_policy": pi_t,  # R3-3: 選んだ方策をそのまま予測に反映する（ダミー）
        "predicted_threat": max(threat - (1 if pi_t == "withdraw" else 0), 0),  # R3-3: withdraw なら脅威が少し下がる仮定
        "predicted_body_alarm": max(body_alarm - (1 if pi_t in ("withdraw", "assert") else 0), 0),  # R3-3: withdraw/assert で警報が少し下がる仮定
    }  # R3-3: 後でDBN/FEPの推論に差し替える前提の簡易予測

    return StepOutput(pi_t=pi_t, o_t1_pred=o_t1_pred, notes=notes)  # R3-1: 契約どおり StepOutput を返す