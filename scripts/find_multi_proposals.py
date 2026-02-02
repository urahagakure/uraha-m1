# 要求: 「介入点」が2件以上出る入力を探す（simulate_step仕様に合わせる）

from __future__ import annotations  # 要求: 型注釈を安定させる
from dataclasses import dataclass  # 要求: フィールド定義を読みやすくする

from app.core.contracts import StepInput  # 要求: simulate_stepの入力契約を使う
from app.core.simulator import simulate_step  # 要求: 現状の方策計算ロジックを使う


@dataclass(frozen=True)  # 要求: フィールド定義は不変にする
class Field:  # 要求: 探索対象フィールドをまとめる
    key: str  # 要求: 入力キー名
    label: str  # 要求: 表示名
    min: int = 0  # 要求: 範囲下限
    max: int = 3  # 要求: 範囲上限


BOUNDARY_FIELDS = [  # 要求: 現行UIの4項目を探索する
    Field("threat", "脅威推定"),  # 要求: threatを探索対象に含める
    Field("body_alarm", "身体警報"),  # 要求: body_alarmを探索対象に含める
    Field("need_clarity", "ニーズ明確度"),  # 要求: need_clarityを探索対象に含める
    Field("energy", "余力"),  # 要求: energyを探索対象に含める
]


def policy_of(o: dict) -> str:  # 要求: o_tからpi_tを得る
    s_t = {"energy": o["energy"]}  # 要求: 現状ロジックに合わせてs_tを作る
    x = StepInput(  # 要求: 契約どおりの入力を作る
        s_t=s_t,  # 要求: 隠れ状態を渡す
        o_t=o,  # 要求: 観測を渡す
        prefs={"safe": 0.7, "connect": 0.3},  # 要求: 現状の固定値を使う
        precision={"policy": 1.0},  # 要求: 現状の固定値を使う
    )
    y = simulate_step(x)  # 要求: 方策を計算する
    return str(y.pi_t)  # 要求: pi_tを文字列で返す


def proposals_for(base: dict) -> list[dict]:  # 要求: ±1近傍で方策が変わる候補を列挙する
    base_pi = policy_of(base)  # 要求: 基準方策を得る
    out: list[dict] = []  # 要求: 候補を貯める
    for f in BOUNDARY_FIELDS:  # 要求: 各フィールドを1つずつ動かす
        for delta in (-1, 1):  # 要求: ±1だけ試す
            v0 = int(base[f.key])  # 要求: 現在値を読む
            v1 = v0 + delta  # 要求: 近傍値を作る
            if v1 < f.min or v1 > f.max:  # 要求: 範囲外は除外する
                continue  # 要求: 無効な候補は出さない
            alt = dict(base)  # 要求: 入力をコピーする
            alt[f.key] = v1  # 要求: 1項目だけ変更する
            alt_pi = policy_of(alt)  # 要求: 変更後の方策を計算する
            if alt_pi != base_pi:  # 要求: 方策が変わったものだけ採用する
                out.append(  # 要求: 表示に必要な情報をまとめる
                    {"key": f.key, "label": f.label, "from": v0, "to": v1, "pi_t": alt_pi}
                )
    # 要求: 重複排除（同一候補を1つにする）
    seen = set()  # 要求: 重複判定キー集合
    uniq: list[dict] = []  # 要求: ユニーク候補
    for p in out:  # 要求: 候補を走査する
        k = (p["key"], int(p["from"]), int(p["to"]), str(p["pi_t"]))  # 要求: 同一判定キー
        if k in seen:  # 要求: 既出は捨てる
            continue  # 要求: 重複除去
        seen.add(k)  # 要求: 既出登録
        uniq.append(p)  # 要求: 採用
    # 要求: 並び順を安定化する（毎回同じ順）
    uniq.sort(key=lambda x: (str(x["label"]), int(x["to"]), str(x["pi_t"])))  # 要求: 安定ソート
    return uniq  # 要求: 候補一覧を返す


def main() -> None:  # 要求: 上位の「候補が多い入力」を表示する
    scored = []  # 要求: (候補数, base入力, 候補一覧) を貯める
    for threat in range(4):  # 要求: 0..3を探索する
        for body_alarm in range(4):  # 要求: 0..3を探索する
            for need_clarity in range(4):  # 要求: 0..3を探索する
                for energy in range(4):  # 要求: 0..3を探索する
                    base = {  # 要求: base入力を構成する
                        "threat": threat,  # 要求: threatを入れる
                        "body_alarm": body_alarm,  # 要求: body_alarmを入れる
                        "need_clarity": need_clarity,  # 要求: need_clarityを入れる
                        "energy": energy,  # 要求: energyを入れる
                    }
                    props = proposals_for(base)  # 要求: 介入点候補を計算する
                    if len(props) >= 2:  # 要求: 2件以上のものだけ採用する
                        scored.append((len(props), base, props, policy_of(base)))  # 要求: スコア付け
    scored.sort(key=lambda t: (-t[0], t[3], t[1]["threat"], t[1]["body_alarm"], t[1]["need_clarity"], t[1]["energy"]))  # 要求: 多い順
    print(f"found {len(scored)} inputs with >=2 proposals")  # 要求: 件数を表示する
    for n, base, props, pi in scored[:15]:  # 要求: 上位15件だけ表示する
        print("-" * 60)  # 要求: 見やすい区切り
        print(f"base={base}  pi_t={pi}  proposals={n}")  # 要求: 概要を表示する
        for p in props:  # 要求: 候補を列挙する
            print(f"  - {p['label']}({p['key']}): {p['from']} -> {p['to']}  => pi_t={p['pi_t']}")  # 要求: 1行表示


if __name__ == "__main__":  # 要求: 直接実行できるようにする
    main()  # 要求: メイン処理を呼ぶ
