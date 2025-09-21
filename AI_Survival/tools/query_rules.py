import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


def get_existing_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    try:
        cur = conn.execute(f"PRAGMA table_info({table})")
        return [row[1] for row in cur.fetchall()]
    except Exception:
        return []


def select_columns(conn: sqlite3.Connection, table: str, desired: List[str]) -> List[str]:
    existing = set(get_existing_columns(conn, table))
    return [c for c in desired if c in existing]


def sample_rows(db_path: str, table: str, desired_cols: List[str], limit: int = 10,
                where: Optional[str] = None, params: Optional[tuple] = None,
                order_by: str = "created_time DESC") -> Dict[str, Any]:
    db_file = Path(db_path)
    if not db_file.exists():
        return {"success": False, "error": f"db_not_found: {db_path}"}

    try:
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        cols = select_columns(conn, table, desired_cols)
        if not cols:
            return {"success": False, "error": f"no_desired_columns_in_{table}", "available": get_existing_columns(conn, table)}

        sql = f"SELECT {', '.join(cols)} FROM {table}"
        if where:
            sql += f" WHERE {where}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit:
            sql += f" LIMIT {limit}"
        rows = [dict(r) for r in conn.execute(sql, params or ()).fetchall()]

        # 尝试解析 JSON 字段
        for r in rows:
            for jf in ("conditions", "predictions"):
                if jf in r and isinstance(r[jf], (str, bytes)):
                    v = r[jf]
                    try:
                        if isinstance(v, bytes):
                            v = v.decode("utf-8", errors="ignore")
                        r[jf] = json.loads(v)
                    except Exception:
                        # 保留原字符串
                        r[jf] = v.decode("utf-8", errors="ignore") if isinstance(v, bytes) else v

        return {"success": True, "count": len(rows), "columns": cols, "rows": rows}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            conn.close()
        except Exception:
            pass


def unique_by_content_hash(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    unique = []
    for r in rows:
        ch = r.get("content_hash")
        if ch in seen:
            continue
        seen.add(ch)
        unique.append(r)
    return unique


def main():
    direct = sample_rows(
        db_path="five_libraries/direct_rules.db",
        table="direct_rules",
        desired_cols=[
            "rule_id", "rule_type", "conditions", "predictions",
            "confidence", "support_count", "contradiction_count",
            "validation_status", "created_time", "content_hash", "creator_id"
        ],
        limit=10,
    )

    total = sample_rows(
        db_path="five_libraries/total_rules.db",
        table="total_rules",
        desired_cols=[
            "rule_id", "rule_type", "conditions", "predictions",
            "confidence", "support_count", "contradiction_count",
            "validation_status", "created_time", "occurrence_count", "content_hash"
        ],
        limit=10,
    )

    # RILAI2 最近规则（支持回答“RILAI2 验证34条”内容）
    rilai2 = sample_rows(
        db_path="five_libraries/direct_rules.db",
        table="direct_rules",
        desired_cols=[
            "rule_id", "rule_type", "conditions", "predictions",
            "confidence", "support_count", "contradiction_count",
            "validation_status", "created_time", "content_hash", "creator_id"
        ],
        where="creator_id = ?",
        params=("RILAI2",),
        limit=200,
        order_by="created_time DESC"
    )

    out = {
        "DIRECT_RULES": direct,
        "TOTAL_RULES": total,
        "RILAI2": rilai2,
    }

    if rilai2.get("success"):
        uniq = unique_by_content_hash(rilai2["rows"])  # type: ignore
        out["RILAI2_UNIQUE_COUNT"] = len(uniq)
        out["RILAI2_UNIQUE_ITEMS"] = uniq[:50]

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


