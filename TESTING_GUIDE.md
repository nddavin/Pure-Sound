# Pure Sound Testing Guide

## Overview

This guide covers testing strategies, frameworks, and best practices for the Pure Sound project. It includes information about unit tests, integration tests, end-to-end tests, and performance testing.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Framework](#test-framework)
3. [Test Types](#test-types)
4. [Running Tests](#running-tests)
5. [Writing Tests](#writing-tests)
6. [Test Fixtures](#test-fixtures)
7. [Mocking](#mocking)
8. [CI/CD Integration](#cicd-integration)
9. [Test Coverage](#test-coverage)
10. [Performance Testing](#performance-testing)

---

## Testing Philosophy

Pure Sound follows a comprehensive testing strategy:

1. **Test Pyramid**: Focus on unit tests, supplement with integration and E2E tests
2. **First, Fast, Isolated**: Tests should be fast, isolated, and repeatable
3. **Meaningful Assertions**: Test behavior, not implementation details
4. **Continuous Testing**: Run tests automatically in CI/CD pipeline

### Testing Goals

- Catch bugs before they reach production
- Ensure code correctness under various conditions
- Enable safe refactoring and feature additions
- Document expected behavior through test cases

---

## Test Framework

### Pytest Configuration

Pytest is the primary testing framework used in Pure Sound.

**Configuration in `pytest.ini`:**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### Required Dependencies

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock pytest-asyncio
```

---

## Test Types

### Unit Tests

Unit tests verify individual components in isolation.

**Location:** `tests/unit/`

**Example:**

```python
# tests/unit/test_audio_processing.py
import pytest
import numpy as np
from audio_processing_enhanced import AudioProcessingEngine

class TestAudioProcessingEngine:
    """Unit tests for audio processing engine."""
    
    def test_engine_initialization(self):
        """Test engine can be initialized with defaults."""
        engine = AudioProcessingEngine()
        assert engine.sample_rate == 44100
        assert engine.channels == 2
    
    def test_engine_initialization_custom(self):
        """Test engine initialization with custom parameters."""
        engine = AudioProcessingEngine(
            sample_rate=48000,
            channels=1
        )
        assert engine.sample_rate == 48000
        assert engine.channels == 1
```

### Integration Tests

Integration tests verify interactions between components.

**Location:** `tests/integration/`

**Example:**

```python
# tests/integration/test_job_queue.py
import pytest
from job_queue import JobQueue, JobPriority

class TestJobQueueIntegration:
    """Integration tests for job queue."""
    
    def test_job_submission_and_processing(self):
        """Test complete job flow through queue."""
        queue = JobQueue(max_workers=2)
        
        # Submit job
        job_id = queue.submit_job({
            "input_file": "test.wav",
            "preset": "speech_clean"
        })
        
        assert job_id is not None
        assert queue.get_job_status(job_id)["status"] in ["pending", "processing"]
    
    def test_job_with_dependencies(self):
        """Test job with dependency requirements."""
        queue = JobQueue(max_workers=2)
        
        # Submit dependent jobs
        parent_id = queue.submit_job({
            "input_file": "input.wav",
            "preset": "speech_clean"
        })
        
        child_id = queue.submit_job({
            "input_file": "output1.wav",
            "preset": "music_enhancement",
            "depends_on": [parent_id]
        })
        
        assert queue.get_job_status(parent_id) is not None
        assert queue.get_job_status(child_id) is not None
```

### End-to-End Tests

E2E tests verify complete user workflows.

**Location:** `tests/e2e/`

**Example:**

```python
# tests/e2e/test_complete_workflow.py
import pytest
from tests.e2e.pages import DashboardPage, ProcessingPage

class TestCompleteAudioWorkflow:
    """End-to-end tests for complete audio processing workflow."""
    
    @pytest.fixture
    def dashboard(self, browser):
        """Create dashboard page fixture."""
        return DashboardPage(browser)
    
    def test_full_processing_workflow(self, dashboard):
        """Test complete audio processing workflow."""
        # Navigate to dashboard
        dashboard.navigate()
        
        # Upload audio file
        processing = dashboard.upload_audio("tests/audio_samples/test.wav")
        
        # Select preset
        processing.select_preset("speech_clean")
        
        # Start processing
        processing.start_processing()
        
        # Wait for completion
        result = processing.wait_for_completion(timeout=120)
        
        # Verify result
        assert result.is_success()
        assert result.get_output_file() is not None
```

### Performance Tests

Performance tests measure system performance under load.

**Location:** `tests/performance/`

**Example:**

```python
# tests/performance/test_processing_performance.py
import pytest
import time
from audio_processing_enhanced import AudioProcessingEngine

class TestProcessingPerformance:
    """Performance tests for audio processing."""
    
    @pytest.fixture
    def engine(self):
        """Create engine for performance testing."""
        return AudioProcessingEngine()
    
    @pytest.mark.benchmark
    def test_processing_speed(self, engine, benchmark):
        """Benchmark audio processing speed."""
        def process():
            return engine.process(
                input_file="tests/audio_samples/test.wav",
                preset="speech_clean"
            )
        
        result = benchmark(process)
        assert result["success"] is True
    
    @pytest.mark.benchmark
    def test_batch_processing_throughput(self, engine, benchmark):
        """Benchmark batch processing throughput."""
        files = [
            f"tests/audio_samples/sample_{i}.wav"
            for i in range(10)
        ]
        
        def batch_process():
            return [engine.process(f, "speech_clean") for f in files]
        
        result = benchmark(batch_process)
        assert len(result) == 10
        assert all(r["success"] for r in result)
```

---

## Running Tests

### Test Commands

```bash
# Run all tests
python test_comprehensive.py

# Run with pytest
python -m pytest tests/ -v

# Run specific test category
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/e2e/ -v

# Run specific test file
python -m pytest tests/unit/test_audio_processing.py -v

# Run specific test class
python -m pytest tests/unit/test_audio_processing.py::TestAudioProcessingEngine -v

# Run specific test method
python -m pytest tests/unit/test_audio_processing.py::TestAudioProcessingEngine::test_engine_initialization -v

# Run tests matching pattern
python -m pytest -k "test_processing" -v

# Run tests with coverage
python -m pytest --cov=. --cov-report=html --cov-report=term-missing

# Run tests with verbose output
python -m pytest -vv

# Run tests without stopping on first failure
python -m pytest --continue-on-collection-errors
```

### Docker Testing

```bash
# Run tests in Docker container
./scripts/start.sh test

# Run specific test category in Docker
docker-compose exec pure-sound python -m pytest tests/unit/ -v

# Run with debugger in Docker
docker-compose exec pure-sound python -m pytest tests/unit/ -v --pdb
```

### Test Reports

```bash
# Generate JUnit XML report
python -m pytest tests/ --junitxml=test-results.xml

# Generate HTML report
python -m pytest tests/ --html=test-report.html

# Generate JSON report
python -m pytest tests/ --json-report --json-report-file=report.json
```

---

## Writing Tests

### Test Structure

```python
# tests/unit/test_module.py
import pytest
from module import ClassUnderTest

class TestClassUnderTest:
    """Test cases for ClassUnderTest."""
    
    @pytest.fixture
    def instance(self):
        """Create instance for testing."""
        return ClassUnderTest(param="test")
    
    def test_method_behavior(self, instance):
        """Test method produces expected behavior."""
        result = instance.method()
        assert result == expected_value
    
    def test_edge_case(self, instance):
        """Test handling of edge cases."""
        with pytest.raises(ExpectedException):
            instance.method(invalid_param)
    
    @pytest.mark.parametrize("input,expected", [
        ("case1", "result1"),
        ("case2", "result2"),
        ("case3", "result3"),
    ])
    def test_parametrized(self, instance, input, expected):
        """Test with multiple input/expected pairs."""
        result = instance.method(input)
        assert result == expected
```

### Best Practices

1. **Use descriptive test names**
   ```python
   # Good
   def test_processing_engine_handles_invalid_audio_file()
   
   # Avoid
   def test_engine_1()
   ```

2. **One assertion per test (when possible)**
   ```python
   # Good
   def test_user_creation():
       user = create_user(name="John", email="john@example.com")
       assert user.name == "John"
       assert user.email == "john@example.com"
   
   # Also acceptable
   def test_user_creation_validates_email():
       with pytest.raises(InvalidEmailError):
           create_user(name="John", email="invalid")
   ```

3. **Use fixtures for setup**
   ```python
   @pytest.fixture
   def sample_audio_file(tmp_path):
       """Create sample audio file for testing."""
       file_path = tmp_path / "sample.wav"
       create_sample_audio(file_path)
       return file_path
   ```

4. **Test edge cases and errors**
   ```python
   def test_handles_empty_input(self):
       with pytest.raises(ValueError, match="Input cannot be empty"):
           self.processor.process("")
   
   def test_handles_nonexistent_file(self):
       with pytest.raises(FileNotFoundError):
           self.processor.process("/nonexistent/file.wav")
   ```

---

## Test Fixtures

### Built-in Fixtures

Pytest provides built-in fixtures:

| Fixture | Purpose |
|---------|---------|
| `tmp_path` | Temporary directory for test |
| `tmp_path_factory` | Create temporary directories |
| `pytestconfig` | pytest configuration |
| `record_property` | Record test properties for reporting |
| `record_testsuite_property` | Record suite-level properties |

### Custom Fixtures

```python
# conftest.py
import pytest
import numpy as np

@pytest.fixture
def sample_audio_data():
    """Create sample audio data for testing."""
    return np.random.randn(44100)  # 1 second of random audio

@pytest.fixture
def audio_processor():
    """Create audio processor instance."""
    from audio_processing import AudioProcessor
    return AudioProcessor(sample_rate=44100)

@pytest.fixture(scope="session")
def test_config():
    """Session-scoped test configuration."""
    return {
        "sample_rate": 44100,
        "channels": 2,
        "test_files": ["file1.wav", "file2.wav"]
    }

@pytest.fixture
def mock_file_system(tmp_path):
    """Mock file system for testing."""
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()
    return tmp_path
```

### Fixture Scopes

| Scope | Lifetime |
|-------|----------|
| `function` | Per test function (default) |
| `class` | Per test class |
| `module` | Per test module |
| `session` | Per test session |

---

## Mocking

### Using pytest-mock

```python
# tests/unit/test_service.py
import pytest
from unittest.mock import Mock, patch

class TestExternalService:
    """Test cases for external service integration."""
    
    @pytest.fixture
    def mock_api(self):
        """Create mock API client."""
        return Mock()
    
    def test_api_call_success(self, mock_api):
        """Test successful API call."""
        mock_api.request.return_value = {"status": "success"}
        
        result = external_service.call_api(mock_api, "data")
        
        assert result["status"] == "success"
        mock_api.request.assert_called_once()
    
    def test_api_call_failure(self, mock_api):
        """Test API call with failure."""
        mock_api.request.side_effect = TimeoutError("Connection timeout")
        
        with pytest.raises(TimeoutError):
            external_service.call_api(mock_api, "data")
```

### Using patch

```python
# Patch external dependencies
@patch('module.submodule.ExternalClass')
def test_with_patch(mock_class):
    """Test with patched external dependency."""
    mock_instance = Mock()
    mock_class.return_value = mock_instance
    mock_instance.method.return_value = "mocked"
    
    result = function_under_test()
    
    assert result == "mocked"
```

### Fixture-based Mocking

```python
@pytest.fixture
def mock_audio_analysis(self):
    """Mock audio analysis engine."""
    with patch('audio_processing_enhanced.audio_analysis_engine') as mock:
        mock.analyze_file.return_value = Mock(
            content_type="speech",
            confidence=0.95
        )
        yield mock
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: python -m pytest tests/unit/ -v --cov
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Run integration tests
        run: python -m pytest tests/integration/ -v

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install Playwright
        run: |
          pip install -r tests/e2e/requirements-e2e.txt
          playwright install --with-deps chromium
      
      - name: Run E2E tests
        run: python -m pytest tests/e2e/ -v
```

---

## Test Coverage

### Coverage Configuration

**Configuration in `pyproject.toml`:**

```toml
[tool.coverage.run]
source = ["."]
omit = [
    "tests/*",
    "docs/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

### Coverage Reports

```bash
# Generate coverage report
python -m pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=. --cov-report=html

# Generate XML coverage report
python -m pytest --cov=. --cov-report=xml

# View HTML report
open htmlcov/index.html
```

### Coverage Goals

| Metric | Target |
|--------|--------|
| Line Coverage | > 80% |
| Branch Coverage | > 70% |
| Function Coverage | > 90% |

---

## Performance Testing

### Using pytest-benchmark

```bash
# Install benchmark plugin
pip install pytest-benchmark
```

### Benchmark Tests

```python
# tests/performance/test_benchmarks.py
import pytest

class TestProcessingBenchmarks:
    """Performance benchmarks for audio processing."""
    
    @pytest.mark.benchmark(
        group="audio-processing",
        min_rounds=10,
        warmup=True
    )
    def test_process_audio_benchmark(self, audio_processor, benchmark):
        """Benchmark audio processing performance."""
        result = benchmark(
            audio_processor.process,
            input_file="tests/audio_samples/test.wav",
            preset="speech_clean"
        )
        assert result["success"] is True
    
    @pytest.mark.benchmark(
        group="batch-processing",
        warmup=False
    )
    def test_batch_processing_benchmark(self, audio_processor, benchmark):
        """Benchmark batch processing performance."""
        files = [f"tests/audio_samples/sample_{i}.wav" for i in range(5)]
        
        result = benchmark(
            audio_processor.batch_process,
            files=files,
            preset="speech_clean"
        )
        assert len(result) == 5
```

### Memory Profiling

```bash
# Profile memory usage
python -m pytest tests/ -v --profile-mem

# Generate memory profile graph
mprof run --python pytest tests/
mprof plot --output memory-usage.png
```

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import asyncio
import aiohttp
from job_queue import JobQueue

class TestLoadHandling:
    """Load testing for job queue."""
    
    def test_concurrent_job_submission(self):
        """Test handling of concurrent job submissions."""
        queue = JobQueue(max_workers=10)
        num_jobs = 100
        
        async def submit_jobs():
            async with aiohttp.ClientSession() as session:
                tasks = [
                    submit_job(session, i)
                    for i in range(num_jobs)
                ]
                return await asyncio.gather(*tasks)
        
        results = asyncio.run(submit_jobs())
        assert len(results) == num_jobs
        assert all(r["success"] for r in results)
```

---

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-mock Documentation](https://pypi.org/project/pytest-mock/)
- [pytest-asyncio Documentation](https://pypi.org/project/pytest-asyncio/)
- [pytest-benchmark Documentation](https://pypi.org/project/pytest-benchmark/)
- [Developer Guide](DEVELOPER_GUIDE.md) - Development best practices
- [API Reference](API_REFERENCE.md) - API testing examples

---

**Last Updated:** 2025-02-02  
**Test Framework:** pytest 7.0+
