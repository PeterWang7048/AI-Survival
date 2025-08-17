import re
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional


def parse_rilai2_candidates(log_path: str) -> Dict[str, Any]:
    path = Path(log_path)
    if not path.exists():
        return {"success": False, "error": f"log_not_found: {log_path}"}

    player_re = re.compile(r"^(ILAI\d+|RILAI\d+)\s")
    cand_re = re.compile(r"候选规律(\d+):\s*([A-Z-]+),\s*(.*)")
    summary_re = re.compile(r"^RILAI2\s.*生成(\d+)条候选规律,\s*验证(\d+)条规律")

    current_player: Optional[str] = None
    candidates: List[Dict[str, Any]] = []
    summary: Optional[Dict[str, int]] = None

    with path.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.rstrip('\n')
            m = player_re.match(line)
            if m:
                current_player = m.group(1)
            if current_player == 'RILAI2':
                m2 = cand_re.search(line)
                if m2:
                    idx = int(m2.group(1))
                    rule_type = m2.group(2)
                    text = m2.group(3)
                    candidates.append({
                        'candidate_no': idx,
                        'rule_type': rule_type,
                        'raw_text': text
                    })
                m3 = summary_re.match(line)
                if m3:
                    summary = {'generated': int(m3.group(1)), 'validated': int(m3.group(2))}

    # 排序按 candidate_no
    candidates.sort(key=lambda x: x['candidate_no'])

    return {"success": True, "candidates": candidates, "summary": summary}


def load_rilai2_rules(db_path: str = 'five_libraries/direct_rules.db') -> Dict[str, Any]:
    db = Path(db_path)
    if not db.exists():
        return {"success": False, "error": f"db_not_found: {db_path}"}
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT rule_id, rule_type, conditions, predictions, confidence,
                   support_count, contradiction_count, validation_status,
                   created_time, content_hash, creator_id
            FROM direct_rules
            WHERE creator_id = ?
            ORDER BY created_time DESC
            LIMIT 500
            """,
            ('RILAI2',)
        ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            for jf in ('conditions', 'predictions'):
                v = d.get(jf)
                if isinstance(v, (bytes, bytearray)):
                    try:
                        v = v.decode('utf-8', errors='ignore')
                    except Exception:
                        pass
                if isinstance(v, str):
                    try:
                        d[jf] = json.loads(v)
                    except Exception:
                        pass
            out.append(d)
        return {"success": True, "rules": out}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass


def extract_tokens(raw_text: str) -> Dict[str, str]:
    # 粗略提取 environment/object_category/tool/action 等词片段
    env = None
    m_env = re.search(r"在(.+?)中", raw_text)
    if m_env:
        env = m_env.group(1)

    obj = None
    # 尝试英文目标，如 ground_plant/Rabbit/Boar
    m_obj_en = re.search(r"对([A-Za-z_]+)", raw_text)
    if m_obj_en:
        obj = m_obj_en.group(1)

    tool = None
    m_tool = re.search(r"使用(.+?)工具", raw_text)
    if m_tool:
        tool = m_tool.group(1)

    action = None
    # 简单匹配几类常见动作词
    for act in ['探索', '移动', '攻击', '采集']:
        if act in raw_text:
            action = act
            break

    return {
        'environment': env or '',
        'object_category': obj or '',
        'tool': tool or '',
        'action': action or ''
    }


def map_candidate_to_rule(cand: Dict[str, Any], rules: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    c_type = cand.get('rule_type')
    tokens = extract_tokens(cand.get('raw_text', ''))

    best = None
    best_score = -1
    for r in rules:
        if r.get('rule_type') != c_type:
            continue
        cond = r.get('conditions') or {}
        score = 0
        if tokens['environment'] and str(cond.get('environment', '')).startswith(tokens['environment']):
            score += 1
        if tokens['object_category'] and str(cond.get('object_category', '')).lower() == tokens['object_category'].lower():
            score += 1
        if tokens['tool'] and str(cond.get('tool', '')) == tokens['tool']:
            score += 1
        if tokens['action'] and str(cond.get('action', '')) == tokens['action']:
            score += 1
        if score > best_score:
            best = r
            best_score = score

    return best


def main():
    import sys
    log_path = sys.argv[1] if len(sys.argv) > 1 else 'game_20250812_110815.log'
    parsed = parse_rilai2_candidates(log_path)
    rules = load_rilai2_rules()

    result: Dict[str, Any] = {
        'success': parsed.get('success') and rules.get('success'),
        'summary': parsed.get('summary'),
        'items': []
    }
    if not result['success']:
        print(json.dumps({"success": False, "parsed": parsed, "rules": rules}, ensure_ascii=False, indent=2))
        return

    candidates: List[Dict[str, Any]] = parsed['candidates']  # type: ignore
    drules: List[Dict[str, Any]] = rules['rules']  # type: ignore

    seen_hashes = set()
    for c in candidates:
        mapped = map_candidate_to_rule(c, drules)
        content_hash = mapped.get('content_hash') if mapped else None
        is_dup = False
        if content_hash:
            if content_hash in seen_hashes:
                is_dup = True
            else:
                seen_hashes.add(content_hash)

        result['items'].append({
            'candidate_no': c.get('candidate_no'),
            'candidate_type': c.get('rule_type'),
            'raw_text': c.get('raw_text'),
            'mapped': bool(mapped),
            'is_duplicate_in_batch': is_dup,
            'mapped_formal_rule': {
                'rule_id': mapped.get('rule_id') if mapped else None,
                'rule_type': mapped.get('rule_type') if mapped else None,
                'conditions': mapped.get('conditions') if mapped else None,
                'predictions': mapped.get('predictions') if mapped else None,
                'confidence': mapped.get('confidence') if mapped else None,
                'content_hash': mapped.get('content_hash') if mapped else None,
            }
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()


