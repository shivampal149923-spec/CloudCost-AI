"""Turn analysis results into plain-language advice, using Claude when available."""

import os

from .analyzer import Finding, CostRecord, cost_by, total_cost

DEFAULT_MODEL = "claude-sonnet-5-5"


def _fallback_summary(records: list[CostRecord], findings: list[Finding]) -> str:
    savings = round(sum(f.monthly_savings_usd for f in findings), 2)
    top = list(cost_by(records, "service").items())[:3]
    top_text = ", ".join(f"{name} (${amt})" for name, amt in top)
    return (
        f"Total spend is ${total_cost(records)}. Biggest services: {top_text}. "
        f"{len(findings)} savings opportunities found, worth about ${savings}."
    )


def build_prompt(records: list[CostRecord], findings: list[Finding]) -> str:
    lines = [
        f"Total spend: ${total_cost(records)}",
        f"By provider: {cost_by(records, 'provider')}",
        f"By service: {cost_by(records, 'service')}",
        "Findings:",
    ]
    for f in findings:
        lines.append(
            f"- {f.resource_id} ({f.provider} {f.service}): {f.issue}; "
            f"suggested: {f.recommendation} (~${f.monthly_savings_usd})"
        )
    return (
        "You are a FinOps advisor. Using the data below, write a short summary "
        "and a prioritized action plan (highest savings first). Be concrete.\n\n"
        + "\n".join(lines)
    )


def advise(records: list[CostRecord], findings: list[Finding]) -> str:
    """Return AI advice if ANTHROPIC_API_KEY is set, else a rule-based summary."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_summary(records, findings)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=os.getenv("CLOUDCOST_MODEL", DEFAULT_MODEL),
            max_tokens=1000,
            messages=[{"role": "user", "content": build_prompt(records, findings)}],
        )
        return "".join(b.text for b in message.content if b.type == "text")
    except Exception as exc:  # network, auth, or model errors
        return f"(AI advice unavailable: {exc})\n\n" + _fallback_summary(records, findings)
