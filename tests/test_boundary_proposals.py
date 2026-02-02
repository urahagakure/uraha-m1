# tests/test_boundary_proposals.py
# R-test-1: propose_interventions の出力契約を固定して壊れにくくする

from app.web.routes_boundary import propose_interventions  # R-test-2: 対象関数を直接テストする


def test_proposals_contract_and_dedup_and_arrow():  # R-test-3: 出力契約+重複排除+矢印の妥当性
    base_cleaned = {  # R-test-4: validate後の入力(dict)を模擬する
        "threat": 1,
        "body_alarm": 1,
        "need_clarity": 2,
        "energy": 1,
    }

    base_pi_t = "assert"  # R-test-5: 変化前の方策を固定する（表示で from_pi_t に使う）
    proposals = propose_interventions(base_cleaned, base_pi_t)  # R-test-6: 介入候補を生成する

    assert isinstance(proposals, list)  # R-test-7: listで返ること
    if not proposals:  # R-test-8: 候補0件でも契約違反ではない
        return  # R-test-8

    required_keys = {  # R-test-9: テンプレで必要なキー集合
        "label",
        "key",
        "range",
        "from",
        "to",
        "arrow",
        "from_pi_t",
        "to_pi_t",
    }

    seen = set()  # R-test-10: 重複検出用
    for p in proposals:  # R-test-11: 全候補を検査する
        assert required_keys.issubset(set(p.keys()))  # R-test-12: 必須キーが揃うこと
        assert p["arrow"] in ("↑", "↓")  # R-test-13: 矢印は↑か↓のみ
        k = (p["key"], int(p["from"]), int(p["to"]), str(p["to_pi_t"]))  # R-test-14: 同一視キー
        assert k not in seen  # R-test-15: 重複がないこと
        seen.add(k)  # R-test-16: 既出登録

def _sig(p: dict) -> tuple:  # S-P1: 重複判定用の署名を作る
    return (p.get("key"), p.get("from"), p.get("to"), p.get("to_pi_t"))  # S-P1


def test_proposals_no_duplicates_v2():  # S-P1: 重複がない（追加テスト）
    base_cleaned = {  # S-P1
        "threat": 1,
        "body_alarm": 1,
        "need_clarity": 2,
        "energy": 1,
    }
    base_pi_t = "assert"  # S-P1
    proposals = propose_interventions(base_cleaned, base_pi_t)  # S-P1
    sigs = [_sig(p) for p in proposals]  # S-P1
    assert len(sigs) == len(set(sigs))  # S-P1


def test_proposals_stable_order_v2():  # S-P2: 並び順が安定（追加テスト）
    base_cleaned = {  # S-P2
        "threat": 1,
        "body_alarm": 1,
        "need_clarity": 2,
        "energy": 1,
    }
    base_pi_t = "assert"  # S-P2
    p1 = propose_interventions(base_cleaned, base_pi_t)  # S-P2
    p2 = propose_interventions(base_cleaned, base_pi_t)  # S-P2
    s1 = [_sig(p) for p in p1]  # S-P2
    s2 = [_sig(p) for p in p2]  # S-P2
    assert s1 == s2  # S-P2