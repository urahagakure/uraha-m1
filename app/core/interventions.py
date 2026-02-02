# app/core/interventions.py
from __future__ import annotations  # R-M0: 前方参照の簡略化

from typing import Dict, List  # R-M0: 型ヒント

from app.core.contracts import StepInput  # R-M1: 契約の入力型
from app.core.simulator import simulate_step  # R-M2: 1-stepシミュレータ（あなたの実際のimportに合わせて調整）
from app.templates_def.registry import get_template  # R-TPL1

def propose_interventions(base_cleaned: dict, base_pi_t: str) -> list[dict]:  # R16-1,R18-2: 介入候補を作る
    proposals: list[dict] = []  # R16-1: 候補を貯める
    BOUNDARY_FIELDS = get_template("boundary").fields  # R-TPL1
    for f in BOUNDARY_FIELDS:  # R16-2: 各入力を1つずつ動かす
        for delta in (-1, 1):  # R16-2: ±1だけ試す
            v0 = int(base_cleaned[f.key])  # R16-2: 現在値
            v1 = v0 + delta  # R16-2: 近傍値
            if v1 < f.min or v1 > f.max:  # R16-5: 範囲外はスキップ
                continue  # R16-5

            alt = dict(base_cleaned)  # R16-2: 入力をコピーする
            alt[f.key] = v1  # R16-2: 1項目だけ変更する

            s_t = {"energy": alt["energy"]}  # R16-3: 隠れ状態（現状どおり）
            o_t = {  # R16-3: 観測（現状どおり）
                "threat": alt["threat"],  # R16-3
                "body_alarm": alt["body_alarm"],  # R16-3
                "need_clarity": alt["need_clarity"],  # R16-3
                "energy": alt["energy"],  # R16-3
            }

            x = StepInput(  # R16-3: 契約どおり入力を作る
                s_t=s_t,  # R16-3
                o_t=o_t,  # R16-3
                prefs={"safe": 0.7, "connect": 0.3},  # R16-3: V0固定
                precision={"policy": 1.0},  # R16-3: V0固定
            )
            y = simulate_step(x)  # R16-3: 近傍ケースを評価する

            if y.pi_t != base_pi_t:  # R16-4: 方策が変わった候補だけ採用
                rng = f"{f.min}-{f.max}"  # R18-1: 範囲表示
                arrow = "↑" if v1 > v0 else "↓"  # R18-2: 方向
                proposals.append({  # R16-4: テンプレ用にまとめる
                    "label": f.label,  # R18-3: 日本語ラベル
                    "key": f.key,  # R18-4: 開発者向けキー
                    "range": rng,  # R18-5
                    "from": v0,  # R18-6
                    "to": v1,  # R18-7
                    "arrow": arrow,  # R18-8
                    "from_pi_t": base_pi_t,  # R18-9
                    "to_pi_t": y.pi_t,  # R18-10
                })

    # --- R17-1: 重複排除（表示ノイズ削減） ---
    seen: set[tuple[str, int, int, str]] = set()  # R17-1
    uniq: list[dict] = []  # R17-1
    for p in proposals:  # R17-1
        k = (p["key"], int(p["from"]), int(p["to"]), str(p["to_pi_t"]))  # R17-1: to_pi_tで同一視
        if k in seen:  # R17-1
            continue  # R17-1
        seen.add(k)  # R17-1
        uniq.append(p)  # R17-1

    # --- R17-2: 並び順固定（毎回同じ並びにする） ---
    uniq.sort(key=lambda x: (str(x["label"]), str(x["key"]), int(x["to"]), str(x["to_pi_t"])))  # R17-2

    # --- R17-3: 上限 ---
    LIMIT = 10  # R17-3
    return uniq[:LIMIT]  # R17-3

def build_proposal_view(proposals: list[dict]) -> tuple[dict[str, list[dict]], list[str]]:  # R-S1: 表示用の塊を作る
    groups: dict[str, list[dict]] = {}  # R-S1: to_pi_t ごとのグループ
    for p in proposals:  # R-S1
        k = str(p.get("to_pi_t"))  # R-S1: 変化後方策
        groups.setdefault(k, []).append(p)  # R-S1

    # R-S2: グループ内の並びも固定（念のため）
    for k in groups:  # R-S2
        groups[k].sort(key=lambda x: (str(x["label"]), str(x["key"]), int(x["to"]), str(x["to_pi_t"])))  # R-S2

    # R-S3: summary を作る（to_pi_t ごとに「効いたキー」を列挙）
    summary: list[str] = []  # R-S3
    for to_pi_t in sorted(groups.keys()):  # R-S3: グループ順を固定
        items = groups[to_pi_t]  # R-S3
        base_pi_t = str(items[0].get("from_pi_t")) if items else "?"  # R-S3: 変化前（同一前提）
        ks = ", ".join(sorted({f'{x["key"]}{x["arrow"]}' for x in items}))  # R-S3: key+矢印の集合
        summary.append(f"{ks} で pi_t が {base_pi_t} → {to_pi_t} に変化")  # R-S3

    return groups, summary  # R-S1