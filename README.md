# CloudCost AI

Find wasted cloud spend and get AI-powered advice on how to cut it.

CloudCost AI reads billing data from AWS, Azure, or GCP, flags idle, oversized, and suddenly expensive resources, and (optionally) asks Claude for a prioritized savings plan.

## Features

- Cost totals by provider and service
- Detects idle resources, underused resources, and cost spikes
- Estimates potential savings per finding
- Optional AI-written action plan
- Works offline with a rule-based summary if no API key is set

## Quick start

```bash
git clone https://github.com/YOUR-USERNAME/cloudcost-ai.git
cd cloudcost-ai
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env             # add your ANTHROPIC_API_KEY (optional)
```

## Usage

```bash
cloudcost report data/sample_billing.csv          # rule-based report
cloudcost report data/sample_billing.csv --ai     # adds AI advice
```

Your billing CSV needs these columns: `date, provider, service, resource_id, region, cost_usd, usage_hours, cpu_avg_pct`. See [docs/architecture.md](docs/architecture.md).

## Tests

```bash
pytest
```

## Project structure

```
src/cloudcost_ai/   application code
tests/              unit tests
data/               sample billing data
docs/               architecture notes
.github/workflows/  CI
```

## Security

Never commit `.env` or real billing exports. Both are listed in `.gitignore`.

## License

MIT. See [LICENSE](LICENSE).
