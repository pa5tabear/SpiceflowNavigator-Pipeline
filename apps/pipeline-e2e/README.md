# Pipeline E2E Agent

**Owner**: Agent 1 - End-to-end orchestrator  
**Responsibility**: Reads user goals, triggers the pipeline, and produces weekly briefs

## Purpose
This agent coordinates the entire SpiceflowNavigator pipeline:
- Reads user goals from `/Goals/` directory
- Triggers RSS ingestion through navigator-ingest API
- Calls navigator-strategy for analysis and scoring
- Produces final weekly briefs in markdown format

## API Contracts
- **Input**: User goals (markdown files), podcast configuration
- **Output**: Weekly brief markdown files
- **Dependencies**: navigator-ingest API, navigator-strategy API

## Development
```bash
# Run this agent
make dev-e2e

# Test this agent
pytest apps/pipeline-e2e/tests/
``` 