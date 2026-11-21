# Architecture

```
billing CSV  ->  analyzer.py  ->  findings  ->  ai_advisor.py  ->  CLI report
                 (load, group,     (idle,        (Claude API, or
                  detect waste)     underused,    rule-based
                                    spikes)       fallback)
```

## Modules

- `analyzer.py`: loads billing rows, totals cost by provider/service, and applies rules to find savings.
- `ai_advisor.py`: builds a prompt from the findings and asks Claude for a prioritized plan. Falls back to a plain summary if no API key is set.
- `cli.py`: the `cloudcost report` command.

## Billing CSV format

| column | meaning |
|---|---|
| date | YYYY-MM-DD |
| provider | AWS, Azure, GCP |
| service | e.g. EC2, S3 |
| resource_id | unique resource name |
| region | cloud region |
| cost_usd | cost for that day |
| usage_hours | hours used |
| cpu_avg_pct | average CPU %, blank for non-compute |

## Roadmap

- Pull billing directly from AWS Cost Explorer, Azure Cost Management, and GCP Billing.
- Web dashboard.
- Scheduled reports by email or Slack.
