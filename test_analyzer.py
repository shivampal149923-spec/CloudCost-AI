from pathlib import Path

from cloudcost_ai.analyzer import cost_by, find_savings, load_costs, total_cost

SAMPLE = Path(__file__).parent.parent / "data" / "sample_billing.csv"


def test_load_and_total():
    records = load_costs(str(SAMPLE))
    assert len(records) == 18
    assert total_cost(records) > 0


def test_cost_by_provider_sorted_desc():
    records = load_costs(str(SAMPLE))
    totals = list(cost_by(records, "provider").values())
    assert totals == sorted(totals, reverse=True)


def test_detects_idle_instance():
    findings = find_savings(load_costs(str(SAMPLE)))
    idle = [f for f in findings if f.resource_id == "i-dev-02"]
    assert idle and idle[0].issue.startswith("Idle")


def test_detects_underused_instance():
    findings = find_savings(load_costs(str(SAMPLE)))
    assert any(f.resource_id == "i-batch-03" and f.issue.startswith("Underused") for f in findings)


def test_detects_cost_spike():
    findings = find_savings(load_costs(str(SAMPLE)))
    assert any(f.resource_id == "s3-logs" and "spike" in f.issue for f in findings)
