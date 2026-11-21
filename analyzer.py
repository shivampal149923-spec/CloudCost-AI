"""Load billing data and detect cost-saving opportunities."""

import csv
from collections import defaultdict
from dataclasses import dataclass
from statistics import mean
from typing import Optional


@dataclass
class CostRecord:
    date: str
    provider: str
    service: str
    resource_id: str
    region: str
    cost_usd: float
    usage_hours: float
    cpu_avg_pct: Optional[float]


@dataclass
class Finding:
    resource_id: str
    provider: str
    service: str
    issue: str
    recommendation: str
    monthly_savings_usd: float


def _to_float(value: str) -> Optional[float]:
    value = (value or "").strip()
    return float(value) if value else None


def load_costs(path: str) -> list[CostRecord]:
    """Read a billing CSV into a list of CostRecord objects."""
    records = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            records.append(
                CostRecord(
                    date=row["date"],
                    provider=row["provider"],
                    service=row["service"],
                    resource_id=row["resource_id"],
                    region=row["region"],
                    cost_usd=_to_float(row["cost_usd"]) or 0.0,
                    usage_hours=_to_float(row["usage_hours"]) or 0.0,
                    cpu_avg_pct=_to_float(row.get("cpu_avg_pct", "")),
                )
            )
    return records


def total_cost(records: list[CostRecord]) -> float:
    return round(sum(r.cost_usd for r in records), 2)


def cost_by(records: list[CostRecord], field: str) -> dict[str, float]:
    """Group total cost by a field such as 'provider' or 'service'."""
    totals: dict[str, float] = defaultdict(float)
    for r in records:
        totals[getattr(r, field)] += r.cost_usd
    return dict(sorted(((k, round(v, 2)) for k, v in totals.items()), key=lambda kv: -kv[1]))


def find_savings(records: list[CostRecord]) -> list[Finding]:
    """Apply simple rules to flag idle, oversized, and spiking resources."""
    findings: list[Finding] = []
    by_resource: dict[str, list[CostRecord]] = defaultdict(list)
    for r in records:
        by_resource[r.resource_id].append(r)

    for resource_id, rows in by_resource.items():
        first = rows[0]
        cost = sum(r.cost_usd for r in rows)
        cpus = [r.cpu_avg_pct for r in rows if r.cpu_avg_pct is not None]

        if cpus:
            avg_cpu = mean(cpus)
            if avg_cpu < 5:
                findings.append(Finding(
                    resource_id, first.provider, first.service,
                    f"Idle: average CPU {avg_cpu:.1f}%",
                    "Stop or terminate this resource if it is not needed.",
                    round(cost, 2),
                ))
            elif avg_cpu < 20:
                findings.append(Finding(
                    resource_id, first.provider, first.service,
                    f"Underused: average CPU {avg_cpu:.1f}%",
                    "Rightsize to a smaller instance type.",
                    round(cost * 0.5, 2),
                ))

        if len(rows) >= 3:
            for r in rows:
                others = [o.cost_usd for o in rows if o is not r]
                if others and r.cost_usd > 2 * mean(others):
                    findings.append(Finding(
                        resource_id, r.provider, r.service,
                        f"Cost spike on {r.date}: ${r.cost_usd:.2f} vs ${mean(others):.2f} typical",
                        "Investigate what changed (traffic, misconfiguration, data transfer).",
                        round(r.cost_usd - mean(others), 2),
                    ))

    return sorted(findings, key=lambda f: -f.monthly_savings_usd)
