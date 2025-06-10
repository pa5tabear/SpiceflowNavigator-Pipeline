# 🛠️ **Navigator-Pipeline Development Guide**

## **Technical Setup & Workflows**

This guide provides comprehensive technical context for developing the Navigator-Pipeline agent, including setup, testing, integration patterns, and best practices.

---

## 🚀 **Development Environment Setup**

### **1. Repository Structure**
```
SpiceflowNavigator-Pipeline/
├── src/
│   ├── cli.py              # Command-line interface
│   ├── workflow.py         # Workflow orchestration engine
│   ├── agents/             # Agent communication clients
│   │   ├── ingest_client.py
│   │   ├── strategy_client.py
│   │   └── ui_client.py
│   ├── core/               # Core pipeline functionality
│   │   ├── health_checker.py
│   │   ├── job_manager.py
│   │   └── error_recovery.py
│   └── utils/              # Utilities and helpers
├── tests/                  # Comprehensive test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                   # Documentation
├── scripts/                # Development and deployment scripts
└── requirements.txt        # Dependencies
```

### **2. Local Development Setup**
```bash
# Clone repository
git clone https://github.com/pa5tabear/SpiceflowNavigator-Pipeline.git
cd SpiceflowNavigator-Pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\\Scripts\\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -e .  # Install in development mode

# Install development tools
pip install pytest pytest-cov black ruff mypy

# Verify setup
python -m pytest
python src/cli.py --help
```

### **3. Environment Configuration**
```bash
# Required environment variables
export NAVIGATOR_INGEST_URL="http://localhost:8001"
export NAVIGATOR_STRATEGY_URL="http://localhost:8002"
export NAVIGATOR_UI_URL="http://localhost:8003"
export PIPELINE_LOG_LEVEL="INFO"
export PIPELINE_MAX_WORKERS="5"

# Optional for development
export PIPELINE_ENV="development"
export PIPELINE_DEBUG="true"
```

---

## 🧪 **Testing Strategy**

### **Test Structure**
Your testing approach should cover three levels:

#### **Unit Tests** (`tests/unit/`)
Test individual components in isolation:

```python
# tests/unit/test_cli.py
import pytest
from unittest.mock import Mock, patch
from src.cli import GoalValidator, AnalysisRequest

def test_goal_validator_accepts_valid_goal():
    valid_goal = "Identify AI investment opportunities in Q4 2024"
    is_valid, message = GoalValidator.validate(valid_goal)
    assert is_valid
    assert "looks good" in message.lower()

def test_goal_validator_rejects_short_goal():
    short_goal = "AI"
    is_valid, message = GoalValidator.validate(short_goal)
    assert not is_valid
    assert "too short" in message.lower()

@patch('src.workflow.WorkflowManager')
def test_cli_analyze_command(mock_workflow):
    # Test CLI command execution
    from click.testing import CliRunner
    from src.cli import cli
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        'analyze',
        '--goal', 'Test AI trends',
        '--source', 'rss://example.com/feed'
    ])
    
    assert result.exit_code == 0
    mock_workflow.assert_called_once()
```

#### **Integration Tests** (`tests/integration/`)
Test component interactions:

```python
# tests/integration/test_agent_communication.py
import pytest
import asyncio
from src.agents.ingest_client import IngestClient
from src.agents.strategy_client import StrategyClient

@pytest.mark.asyncio
async def test_ingest_to_strategy_flow():
    """Test data flow from Ingest to Strategy agent."""
    # Mock agent responses
    ingest_client = IngestClient(base_url="http://test-ingest")
    strategy_client = StrategyClient(base_url="http://test-strategy")
    
    # Test realistic data flow
    with patch.object(ingest_client, 'get_transcripts') as mock_ingest:
        mock_ingest.return_value = [
            {"episode": "AI Weekly #142", "transcript": "Sample content..."}
        ]
        
        transcripts = await ingest_client.get_transcripts(["feed1"])
        
        with patch.object(strategy_client, 'analyze') as mock_strategy:
            mock_strategy.return_value = {
                "insights": [{"title": "AI Investment", "score": 8.5}]
            }
            
            insights = await strategy_client.analyze(
                transcripts, 
                goal="AI investment opportunities"
            )
            
            assert len(insights["insights"]) > 0
            assert insights["insights"][0]["score"] > 0
```

#### **End-to-End Tests** (`tests/e2e/`)
Test complete workflows:

```python
# tests/e2e/test_full_pipeline.py
import pytest
from src.workflow import WorkflowManager
from src.cli import AnalysisRequest

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_analysis_workflow():
    """Test a complete analysis from CLI to results."""
    workflow_manager = WorkflowManager()
    
    request = AnalysisRequest(
        goal="Identify AI investment opportunities",
        sources=["rss://techcrunch.com/ai"],
        format="json"
    )
    
    # This would use actual agent endpoints in staging
    results = await workflow_manager.execute_analysis(request)
    
    assert results["status"] == "success"
    assert "insights" in results
    assert len(results["insights"]) > 0
```

### **Test Commands**
```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration  
make test-e2e

# Run with coverage
make test-coverage

# Run performance tests
make test-performance
```

---

## 🔗 **Agent Integration Patterns**

### **HTTP Client Pattern**
Standard pattern for communicating with other agents:

```python
# src/agents/base_client.py
import httpx
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AgentResponse:
    status: str
    data: Dict[str, Any]
    error: Optional[str] = None
    latency_ms: int = 0

class BaseAgentClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def _request(self, method: str, endpoint: str, 
                      data: Dict[str, Any] = None) -> AgentResponse:
        """Make HTTP request with error handling and metrics."""
        url = f"{self.base_url}{endpoint}"
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            
            if response.status_code == 200:
                return AgentResponse(
                    status="success",
                    data=response.json(),
                    latency_ms=latency_ms
                )
            else:
                return AgentResponse(
                    status="error",
                    data={},
                    error=f"HTTP {response.status_code}: {response.text}",
                    latency_ms=latency_ms
                )
                
        except httpx.TimeoutException:
            return AgentResponse(
                status="timeout",
                data={},
                error="Request timeout",
                latency_ms=self.timeout * 1000
            )
        except Exception as e:
            return AgentResponse(
                status="error", 
                data={},
                error=str(e),
                latency_ms=int((asyncio.get_event_loop().time() - start_time) * 1000)
            )
    
    async def health_check(self) -> bool:
        """Check if agent is healthy."""
        response = await self._request("GET", "/health")
        return response.status == "success"
```

### **Specific Agent Clients**

```python
# src/agents/ingest_client.py
from .base_client import BaseAgentClient, AgentResponse
from typing import List, Dict, Any

class IngestClient(BaseAgentClient):
    async def get_recent_episodes(self, feed_urls: List[str], 
                                 count: int = 10) -> AgentResponse:
        """Get recent episodes from RSS feeds."""
        return await self._request("POST", "/rss/episodes", {
            "feed_urls": feed_urls,
            "count": count
        })
    
    async def transcribe_episodes(self, audio_urls: List[str]) -> AgentResponse:
        """Transcribe audio episodes."""
        return await self._request("POST", "/transcribe", {
            "audio_urls": audio_urls
        })
    
    async def get_cached_transcripts(self, episode_ids: List[str]) -> AgentResponse:
        """Get cached transcripts."""
        return await self._request("POST", "/transcripts/cached", {
            "episode_ids": episode_ids
        })

# src/agents/strategy_client.py  
class StrategyClient(BaseAgentClient):
    async def analyze_goal_alignment(self, transcripts: List[Dict], 
                                   goal: str) -> AgentResponse:
        """Analyze transcript alignment with strategic goal."""
        return await self._request("POST", "/analyze/goal-alignment", {
            "transcripts": transcripts,
            "goal": goal
        })
    
    async def extract_insights(self, aligned_content: List[Dict]) -> AgentResponse:
        """Extract strategic insights from aligned content."""
        return await self._request("POST", "/analyze/insights", {
            "content": aligned_content
        })
    
    async def score_relevance(self, content: List[Dict], 
                            goal: str) -> AgentResponse:
        """Score content relevance to goal.""" 
        return await self._request("POST", "/score/relevance", {
            "content": content,
            "goal": goal
        })
```

---

## 🔄 **Workflow Orchestration Patterns**

### **Pipeline Builder Pattern**
```python
# src/core/pipeline_builder.py
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
import asyncio

@dataclass
class PipelineStep:
    name: str
    agent_client: Any
    method: str
    inputs: Dict[str, Any]
    parallel_group: Optional[str] = None
    depends_on: List[str] = None

class PipelineBuilder:
    def __init__(self):
        self.steps: List[PipelineStep] = []
        self.context: Dict[str, Any] = {}
    
    def add_step(self, name: str, agent_client: Any, method: str,
                 inputs: Dict[str, Any], depends_on: List[str] = None) -> 'PipelineBuilder':
        """Add a sequential step to the pipeline."""
        step = PipelineStep(
            name=name,
            agent_client=agent_client,
            method=method,
            inputs=inputs,
            depends_on=depends_on or []
        )
        self.steps.append(step)
        return self
    
    def add_parallel_group(self, group_name: str, steps: List[Dict]) -> 'PipelineBuilder':
        """Add multiple steps that can run in parallel."""
        for step_config in steps:
            step = PipelineStep(
                name=step_config["name"],
                agent_client=step_config["agent_client"],
                method=step_config["method"],
                inputs=step_config["inputs"],
                parallel_group=group_name,
                depends_on=step_config.get("depends_on", [])
            )
            self.steps.append(step)
        return self
    
    async def execute(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline with dependency resolution."""
        self.context.update(initial_context)
        completed_steps = set()
        
        # Group steps by parallel groups
        parallel_groups = {}
        sequential_steps = []
        
        for step in self.steps:
            if step.parallel_group:
                if step.parallel_group not in parallel_groups:
                    parallel_groups[step.parallel_group] = []
                parallel_groups[step.parallel_group].append(step)
            else:
                sequential_steps.append(step)
        
        # Execute parallel groups and sequential steps
        for step in sequential_steps:
            if self._dependencies_satisfied(step, completed_steps):
                result = await self._execute_step(step)
                self.context[step.name] = result
                completed_steps.add(step.name)
        
        # Execute parallel groups
        for group_name, group_steps in parallel_groups.items():
            if all(self._dependencies_satisfied(step, completed_steps) for step in group_steps):
                tasks = [self._execute_step(step) for step in group_steps]
                results = await asyncio.gather(*tasks)
                
                for step, result in zip(group_steps, results):
                    self.context[step.name] = result
                    completed_steps.add(step.name)
        
        return self.context
    
    def _dependencies_satisfied(self, step: PipelineStep, completed: set) -> bool:
        """Check if step dependencies are satisfied."""
        return all(dep in completed for dep in step.depends_on)
    
    async def _execute_step(self, step: PipelineStep) -> Any:
        """Execute a single pipeline step."""
        print(f"🔄 Executing: {step.name}")
        
        # Resolve inputs from context
        resolved_inputs = {}
        for key, value in step.inputs.items():
            if isinstance(value, str) and value.startswith("$"):
                # Reference to context value
                context_key = value[1:]
                resolved_inputs[key] = self.context.get(context_key, value)
            else:
                resolved_inputs[key] = value
        
        # Call agent method
        method = getattr(step.agent_client, step.method)
        result = await method(**resolved_inputs)
        
        return result
```

### **Usage Example**
```python
# Example: Building a complex analysis pipeline
async def create_analysis_pipeline():
    ingest = IngestClient("http://navigator-ingest")
    strategy = StrategyClient("http://navigator-strategy")
    ui = UIClient("http://navigator-ui")
    
    pipeline = (PipelineBuilder()
        # Parallel content gathering
        .add_parallel_group("content_gathering", [
            {
                "name": "rss_episodes",
                "agent_client": ingest,
                "method": "get_recent_episodes",
                "inputs": {"feed_urls": "$feed_urls", "count": 10}
            },
            {
                "name": "cached_content", 
                "agent_client": ingest,
                "method": "get_cached_transcripts",
                "inputs": {"episode_ids": "$cached_ids"}
            }
        ])
        # Sequential transcription
        .add_step("transcription", ingest, "transcribe_episodes", 
                 {"audio_urls": "$rss_episodes.audio_urls"}, 
                 depends_on=["rss_episodes"])
        # Parallel analysis
        .add_parallel_group("analysis", [
            {
                "name": "goal_alignment",
                "agent_client": strategy,
                "method": "analyze_goal_alignment", 
                "inputs": {"transcripts": "$transcription", "goal": "$user_goal"},
                "depends_on": ["transcription"]
            },
            {
                "name": "relevance_scoring",
                "agent_client": strategy,
                "method": "score_relevance",
                "inputs": {"content": "$transcription", "goal": "$user_goal"}, 
                "depends_on": ["transcription"]
            }
        ])
        # Final insight extraction
        .add_step("insights", strategy, "extract_insights",
                 {"aligned_content": "$goal_alignment"},
                 depends_on=["goal_alignment"])
    )
    
    # Execute pipeline
    results = await pipeline.execute({
        "feed_urls": ["https://feeds.example.com/ai"],
        "cached_ids": ["ep1", "ep2"],
        "user_goal": "Identify AI investment opportunities"
    })
    
    return results
```

---

## 🛡️ **Error Handling & Recovery**

### **Circuit Breaker Pattern**
```python
# src/core/circuit_breaker.py
import asyncio
from enum import Enum
from typing import Callable, Any
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open" # Testing if service recovered

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Reset failure count on successful call."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Increment failure count and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False
            
        return (datetime.now() - self.last_failure_time).seconds >= self.recovery_timeout
```

### **Retry with Exponential Backoff**
```python
# src/core/retry.py
import asyncio
import random
from typing import Callable, Any

async def retry_with_backoff(func: Callable, max_attempts: int = 3,
                           base_delay: float = 1.0, max_delay: float = 60.0,
                           exponential_factor: float = 2.0,
                           jitter: bool = True) -> Any:
    """Retry function with exponential backoff and jitter."""
    
    for attempt in range(max_attempts):
        try:
            return await func()
            
        except Exception as e:
            if attempt == max_attempts - 1:
                # Last attempt, re-raise exception
                raise e
            
            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_factor ** attempt), max_delay)
            
            # Add jitter to prevent thundering herd
            if jitter:
                delay = delay * (0.5 + random.random() * 0.5)
            
            print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            print(f"🔄 Retrying in {delay:.2f} seconds...")
            
            await asyncio.sleep(delay)
```

---

## 📊 **Performance Monitoring**

### **Metrics Collection**
```python
# src/core/metrics.py
import time
from typing import Dict, List
from dataclasses import dataclass, field
from collections import defaultdict, deque

@dataclass
class Metric:
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    def __init__(self, max_history: int = 1000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, int] = defaultdict(int)
        self.timers: Dict[str, List[float]] = defaultdict(list)
    
    def increment(self, name: str, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        self.counters[name] += 1
        self._record_metric(name, self.counters[name], tags or {})
    
    def timing(self, name: str, duration: float, tags: Dict[str, str] = None):
        """Record timing metric."""
        self.timers[name].append(duration)
        self._record_metric(name, duration, tags or {})
    
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record gauge metric."""
        self._record_metric(name, value, tags or {})
    
    def _record_metric(self, name: str, value: float, tags: Dict[str, str]):
        """Record metric with timestamp."""
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags
        )
        self.metrics[name].append(metric)
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if name not in self.metrics:
            return {}
        
        values = [m.value for m in self.metrics[name]]
        if not values:
            return {}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1]
        }
```

### **Performance Decorators**
```python
# src/core/decorators.py
import asyncio
import functools
from .metrics import MetricsCollector

metrics = MetricsCollector()

def measure_performance(metric_name: str):
    """Decorator to measure function performance."""
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    metrics.increment(f"{metric_name}.success")
                    return result
                except Exception as e:
                    metrics.increment(f"{metric_name}.error")
                    raise
                finally:
                    duration = time.time() - start_time
                    metrics.timing(f"{metric_name}.duration", duration)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    metrics.increment(f"{metric_name}.success")
                    return result
                except Exception as e:
                    metrics.increment(f"{metric_name}.error")
                    raise
                finally:
                    duration = time.time() - start_time
                    metrics.timing(f"{metric_name}.duration", duration)
            return sync_wrapper
    return decorator

# Usage example
@measure_performance("agent.ingest.transcribe")
async def transcribe_with_metrics(audio_urls: List[str]):
    # Function automatically gets performance metrics
    pass
```

---

## 🔧 **Development Commands**

### **Makefile Targets**
```makefile
# Makefile
.PHONY: help install test lint format type-check dev clean

help:
	@echo "Navigator-Pipeline Development Commands"
	@echo "====================================="
	@echo "install     Install dependencies"
	@echo "test        Run all tests"
	@echo "test-unit   Run unit tests only"
	@echo "test-e2e    Run end-to-end tests"
	@echo "lint        Run code linting"
	@echo "format      Format code"
	@echo "type-check  Run type checking"
	@echo "dev         Start development server"
	@echo "clean       Clean temporary files"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	python -m pytest tests/ -v --cov=src --cov-report=html

test-unit:
	python -m pytest tests/unit/ -v

test-integration:
	python -m pytest tests/integration/ -v -m "not e2e"

test-e2e:
	python -m pytest tests/e2e/ -v -m e2e

lint:
	ruff check src/ tests/
	black --check src/ tests/

format:
	black src/ tests/
	ruff --fix src/ tests/

type-check:
	mypy src/

dev:
	python src/cli.py status
	@echo "Development environment ready!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage
```

---

## 🎯 **Best Practices Summary**

### **Code Organization**
- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Use dependency injection for testability
- **Type Hints**: Use comprehensive type hints for better IDE support
- **Async First**: Design for async/await patterns throughout

### **Error Handling**
- **Explicit Error Types**: Define custom exceptions for different failure modes
- **Graceful Degradation**: Always provide fallback options
- **Comprehensive Logging**: Log errors with context for debugging
- **Circuit Breakers**: Protect against cascade failures

### **Testing**
- **Test Pyramid**: More unit tests, fewer integration tests, minimal e2e tests
- **Mocking**: Mock external dependencies for reliable unit tests
- **Test Data**: Use factories for creating test data
- **Performance Tests**: Include performance regression tests

### **Performance**
- **Async Operations**: Use async/await for I/O operations
- **Connection Pooling**: Reuse HTTP connections with connection pools
- **Caching**: Cache expensive operations appropriately
- **Monitoring**: Instrument code with metrics and tracing

This development guide provides the foundation for building a robust, scalable Pipeline agent. Use it as your technical reference throughout the development process!

---

**Next Step**: Start with Feature 1 (Smart CLI Interface) using the patterns and examples provided in this guide. 