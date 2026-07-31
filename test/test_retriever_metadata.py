import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.planner import PlannerAgent
from agents.retriever import RetrieverAgent

planner = PlannerAgent()
retriever = RetrieverAgent()


def assert_has_table_column(docs, table=None, column=None):
    table_l = table.lower() if table else None
    col_l = column.lower() if column else None
    for d in docs:
        md = d.metadata or {}
        t = (md.get("table") or "").lower()
        c = (md.get("target_column") or md.get("target") or "").lower()
        if table_l and col_l:
            if table_l == t and (col_l == c or col_l.replace('_','') == c.replace('_','')):
                return True
        elif table_l:
            if table_l == t:
                return True
        elif col_l:
            if col_l == c or col_l.replace('_','') == c.replace('_',''):
                return True
    return False


def test_transformation_snapshot_id_in_bill_promo_fct():
    q = "What is the Transformation for SNAPSHOT_ID in BILL_PROMO_FCT?"
    plan = planner.plan(q)
    docs = retriever.retrieve(plan)
    assert len(docs) > 0
    assert assert_has_table_column(docs, table="bill_promo_fct", column="snapshot_id")


def test_source_column_for_snapshot_id():
    q = "What is the source column for SNAPSHOT_ID in BILL_PROMO_FCT?"
    plan = planner.plan(q)
    docs = retriever.retrieve(plan)
    assert len(docs) > 0
    assert assert_has_table_column(docs, table="bill_promo_fct", column="snapshot_id")
    # also ensure at least one doc has a non-empty source_column
    assert any((d.metadata.get('source_column') or '').strip() for d in docs)


def test_list_all_columns_in_bill_promo_fct():
    q = "List all columns in BILL_PROMO_FCT."
    plan = planner.plan(q)
    docs = retriever.retrieve(plan)
    assert len(docs) > 0
    assert assert_has_table_column(docs, table="bill_promo_fct")


def test_explain_marketing_mart():
    q = "Explain Marketing Mart."
    plan = planner.plan(q)
    docs = retriever.retrieve(plan)
    assert len(docs) > 0


def test_explain_bread_client():
    q = "Explain Bread Client."
    plan = planner.plan(q)
    docs = retriever.retrieve(plan)
    assert len(docs) > 0


def test_unknown_table_column():
    q = "What is SNAPSHOT_ID in UNKNOWN_TABLE_XYZ?"
    plan = planner.plan(q)
    docs = retriever.retrieve(plan)
    assert len(docs) > 0
    assert not assert_has_table_column(docs, table="unknown_table_xyz")


def test_show_mapping_for_bill_promo_fct_returns_rows():
    q = "Show mapping for BILL_PROMO_FCT"
    plan = planner.plan(q)
    docs = retriever.retrieve(plan)
    assert len(docs) > 0
    assert any((d.metadata.get("table") or "").lower() == "bill_promo_fct" for d in docs)


def test_source_column_for_snapshot_id_returns_date_last_stmt_dt():
    q = "What is the source column for SNAPSHOT_ID?"
    plan = planner.plan(q)
    docs = retriever.retrieve(plan)
    assert len(docs) > 0
    assert any(
        (d.metadata.get("target_column") or "").lower() == "snapshot_id"
        and (d.metadata.get("source_column") or "").lower() == "date_last_stmt_dt"
        for d in docs
    )


def test_reasoning_returns_source_column_value_for_snapshot_id():
    from agents.reasoning import ReasoningAgent

    q = "What is the source column for SNAPSHOT_ID?"
    reasoning = ReasoningAgent()
    docs = retriever.retrieve(planner.plan(q))
    result = reasoning.generate_answer(q, docs)

    assert result["answer"]
    assert "I could not find" not in result["answer"]
    assert "date_last_stmt_dt" in result["answer"].lower()


def test_reasoning_explains_bread_client_from_retrieved_docs():
    from agents.reasoning import ReasoningAgent

    q = "Explain Bread Client."
    reasoning = ReasoningAgent()
    docs = retriever.retrieve(planner.plan(q))
    result = reasoning.generate_answer(q, docs)

    assert result["answer"]
    assert "I could not find" not in result["answer"]
    assert "bread" in result["answer"].lower()
