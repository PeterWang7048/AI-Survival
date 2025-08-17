import os
import json
import sqlite3
from typing import Dict, Any, List


DB_SETS = [
    {
        "name": "five_libraries",
        "base": "five_libraries",
        "dbs": [
            ("direct_rules", "direct_rules.db"),
            ("total_rules", "total_rules.db"),
        ],
    },
    {
        "name": "global_five_libraries",
        "base": "global_five_libraries",
        "dbs": [
            ("direct_rules", "direct_rules.db"),
            ("total_rules", "total_rules.db"),
        ],
    },
]


def list_tables(conn: sqlite3.Connection) -> List[str]:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [r[0] for r in cur.fetchall()]


def list_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    return [r[1] for r in cur.fetchall()]


def safe_count(conn: sqlite3.Connection, table: str) -> int:
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return int(cur.fetchone()[0])
    except Exception:
        return -1


def has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
    return col in list_columns(conn, table)


def sample_validated(conn: sqlite3.Connection, table: str, limit: int = 5) -> List[Dict[str, Any]]:
    cols = list_columns(conn, table)
    cur = conn.cursor()
    rows: List[Dict[str, Any]] = []
    if "validation_status" in cols:
        try:
            cur.execute(
                f"SELECT * FROM {table} WHERE validation_status='validated' LIMIT {limit}"
            )
            fetched = cur.fetchall()
            for row in fetched:
                rows.append({cols[i]: row[i] for i in range(len(cols))})
            return rows
        except Exception:
            pass
    # fallback: sample any rows
    try:
        cur.execute(f"SELECT * FROM {table} LIMIT {limit}")
        fetched = cur.fetchall()
        for row in fetched:
            rows.append({cols[i]: row[i] for i in range(len(cols))})
    except Exception:
        pass
    return rows


def analyze_db(path: str, logical_name: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "db_path": path,
        "exists": os.path.exists(path),
        "tables": [],
        "rules": {},
        "error": None,
    }
    if not result["exists"]:
        return result
    try:
        conn = sqlite3.connect(path)
        with conn:
            tables = list_tables(conn)
            result["tables"] = tables
            for t in tables:
                if "rule" in t.lower():
                    total = safe_count(conn, t)
                    validated = None
                    if has_column(conn, t, "validation_status"):
                        try:
                            cur = conn.cursor()
                            cur.execute(
                                f"SELECT COUNT(*) FROM {t} WHERE validation_status='validated'"
                            )
                            validated = int(cur.fetchone()[0])
                        except Exception:
                            validated = None
                    sample = sample_validated(conn, t, limit=5)
                    # 额外抽取关键字段的简化视图
                    key_cols = [
                        "rule_id", "rule_type", "confidence", "validation_status",
                        "conditions", "predictions", "created_time"
                    ]
                    view_rows: List[Dict[str, Any]] = []
                    try:
                        available = [c for c in key_cols if c in list_columns(conn, t)]
                        if available:
                            cur = conn.cursor()
                            cur.execute(
                                f"SELECT {', '.join(available)} FROM {t} LIMIT 5"
                            )
                            fetched = cur.fetchall()
                            for row in fetched:
                                view_rows.append({available[i]: row[i] for i in range(len(available))})
                    except Exception:
                        pass
                    result["rules"][t] = {
                        "row_count": total,
                        "validated_count": validated,
                        "columns": list_columns(conn, t),
                        "samples": sample,
                        "sample_view": view_rows,
                    }
        conn.close()
    except Exception as e:
        result["error"] = str(e)
    return result


def main():
    summary: Dict[str, Any] = {"sets": []}
    for s in DB_SETS:
        set_result: Dict[str, Any] = {
            "name": s["name"],
            "base": s["base"],
            "databases": [],
        }
        for logical, filename in s["dbs"]:
            db_path = os.path.join(s["base"], filename)
            set_result["databases"].append(
                {"logical": logical, **analyze_db(db_path, logical)}
            )
        summary["sets"].append(set_result)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


