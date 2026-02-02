# Pure Sound Developer Guide

## Introduction

This guide provides comprehensive information for developers working on the Pure Sound project. It covers development environment setup, coding standards, architecture overview, and best practices for contributing to the project.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Coding Standards](#coding-standards)
4. [Architecture Overview](#architecture-overview)
5. [Development Workflow](#development-workflow)
6. [Debugging](#debugging)
7. [Performance Profiling](#performance-profiling)
8. [Testing](#testing)
9. [Documentation](#documentation)
10. [Common Tasks](#common-tasks)

---

## Development Environment Setup

### Prerequisites

| Requirement | Minimum Version | Recommended |
|-------------|-----------------|-------------|
| Python | 3.8+ | 3.13 |
| FFmpeg | 4.0+ | Latest |
| Git | 2.0+ | Latest |
| Docker | 20.10+ | Latest |
| Redis | 6.0+ | 7.x |

### Initial Setup

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/pure-sound.git
cd pure-sound
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Upgrade pip
pip install --upgrade pip
```

#### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install FFmpeg (macOS)
brew install ffmpeg

# Install FFmpeg (Ubuntu/Debian)
sudo apt install ffmpeg
```

#### 4. Verify Installation

```bash
# Run comprehensive tests
python test_comprehensive.py

# Verify FFmpeg installation
ffmpeg -version
```

### Docker Development

```bash
# Start development environment
./scripts/start.sh dev

# Run tests in container
./scripts/start.sh test

# Build documentation
./scripts/start.sh docs
```

---

## Project Structure

```
pure-sound/
├── api_backend.py           # REST/gRPC API server
├── audio_analysis.py        # Audio analysis module
├── audio_analysis_enhanced.py  # Enhanced analysis engine
├── audio_processing.py      # Audio processing module
├── audio_processing_enhanced.py # Enhanced processing
├── cloud_integration.py     # Cloud storage integration
├── compress_audio.py        # Main compression CLI
├── config.py                # Configuration management
├── di_container.py          # Dependency injection
├── events.py                # Event system
├── gui.py                   # Basic GUI interface
├── gui_enterprise.py        # Enterprise GUI
├── interfaces.py            # Interface definitions
├── job_queue.py             # Job queue management
├── multi_stream.py          # Multi-stream processing
├── presets.py               # Processing presets
├── resource_pool.py         # Resource management
├── security.py              # Security module
├──
├── docker/
│   ├── Dockerfile           # Production Docker image
│   ├── Dockerfile.dev       # Development Docker image
│   ├── .env.example         # Environment template
│   └── monitoring/          # Prometheus/Grafana configs
│
├── scripts/
│   └── start.sh             # Docker management script
│
├── tests/
│   ├── e2e/                 # End-to-end tests
│   ├── audio_samples/       # Test audio files
│   └── config/              # Test configurations
│
├── docs/                    # Documentation (to be created)
│
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── docker-compose.yml       # Docker composition
└── README.md                # Project documentation
```

---

## Coding Standards

### Python Style Guide

Follow PEP 8 guidelines with the following additions:

#### Naming Conventions

| Component | Convention | Example |
|-----------|------------|---------|
| Classes | PascalCase | `AudioProcessor` |
| Functions | snake_case | `process_audio()` |
| Constants | UPPER_SNAKE_CASE | `MAX_BUFFER_SIZE` |
| Variables | snake_case | `audio_file` |
| Private methods | snake_case with leading underscore | `_internal_process()` |
| Protected attributes | snake_case with leading underscore | `_protected_attr` |

#### Code Organization

```python
"""
Module docstring explaining purpose and usage.
"""

# Standard library imports
import os
from typing import Dict, List

# Third-party imports
import numpy as np
from fastapi import FastAPI

# Local imports
from .base import BaseClass
from .utils import helper_function


class PublicClass:
    """Public class docstring."""
    
    PUBLIC_CONSTANT = 1000
    
    def __init__(self, param: str) -> None:
        """Initialize instance."""
        self.param = param
        self._private_attr = None
    
    def public_method(self) -> bool:
        """Public method docstring."""
        return True
    
    def _private_method(self) -> None:
        """Private method docstring."""
        pass
```

#### Type Hints

```python
from typing import Optional, Union, List, Dict
from dataclasses import dataclass
from enum import Enum

class ProcessingMode(Enum):
    """Processing mode options."""
    FAST = "fast"
    QUALITY = "quality"
    BALANCED = "balanced"

@dataclass
class AudioConfig:
    """Audio configuration."""
    sample_rate: int
    channels: int
    format: str
    bitrate: Optional[int] = None

def process_audio(
    input_path: str,
    output_path: str,
    config: AudioConfig,
    mode: ProcessingMode = ProcessingMode.BALANCED
) -> bool:
    """
    Process audio file with specified configuration.
    
    Args:
        input_path: Path to input audio file
        output_path: Path for output audio file
        config: Audio configuration parameters
        mode: Processing mode selection
        
    Returns:
        True if processing successful, False otherwise
    """
    # Implementation
    return True
```

#### Documentation

```python
def complex_function(
    param1: str,
    param2: int,
    param3: Optional[List[str]] = None
) -> Dict[str, Union[str, int]]:
    """
    Brief description of function purpose.
    
    Extended description explaining the function's behavior,
    edge cases, and any important considerations.
    
    Args:
        param1: Description of param1, including constraints
        param2: Description of param2, valid range if applicable
        param3: Optional description, defaults to None if not provided
        
    Returns:
        Dictionary containing processed results
        
    Raises:
        ValueError: When parameters are invalid
        FileNotFoundError: When input file doesn't exist
        
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success', 'value': 42}
    """
    pass
```

---

## Architecture Overview

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Interfaces                        │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Enterprise    │    REST/gRPC    │     Command Line       │
│      GUI        │      API        │      Interface         │
│  (PyQt6/Tkinter)│   (FastAPI)     │  (compress_audio.py)   │
└─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Services                     │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Audio         │     Job         │      Security          │
│  Processing     │   Management    │      Service           │
│   Engine        │   (job_queue)   │      (security)        │
├─────────────────┼─────────────────┼─────────────────────────┤
│   Analysis      │    Events       │    Configuration       │
│    Engine       │   (events)      │      (config)          │
└─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Shared Infrastructure                     │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Dependency    │    Resource     │      Plugin            │
│   Injection     │    Pooling      │     System             │
│  (di_container) │ (resource_pool) │                       │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Key Modules

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| `audio_processing_enhanced.py` | Core audio processing | `AudioProcessingEngine`, `ProcessingJob` |
| `audio_analysis_enhanced.py` | Audio analysis | `AudioAnalysisEngine`, `AnalysisResult` |
| `job_queue.py` | Job management | `JobQueue`, `JobPriority` |
| `security.py` | Security/encryption | `SecurityManager`, `EncryptionService` |
| `events.py` | Event system | `EventBus`, `EventPublisher` |
| `api_backend.py` | REST API | `PureSoundAPI`, `CloudStorageManager` |

---

## Development Workflow

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-audio-filter
   ```

2. **Make Changes**
   ```bash
   # Edit source files
   # Add tests
   # Update documentation
   ```

3. **Run Tests**
   ```bash
   # Run specific tests
   python -m pytest tests/test_audio_processing.py -v
   
   # Run all tests
   python test_comprehensive.py
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add new audio filter for noise reduction"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/new-audio-filter
   ```

### Code Review Guidelines

When reviewing code, check for:

- [ ] **Correctness**: Does the code do what it's supposed to?
- [ ] **Style**: Does it follow the coding standards?
- [ ] **Tests**: Are tests added/updated?
- [ ] **Documentation**: Are docstrings complete?
- [ ] **Performance**: Any obvious performance issues?
- [ ] **Security**: Any security concerns?

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting changes (no code change)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Example:**
```
feat(audio): add noise reduction filter

Implemented new adaptive noise reduction filter using spectral
subtraction method. Filter automatically detects and reduces
background noise while preserving speech clarity.

Closes #123
```

---

## Debugging

### Python Debugger

```python
import pdb

def process_audio(audio_data):
    pdb.set_trace()  # Set breakpoint
    # Continue execution
    result = audio_data.process()
    return result
```

### Using debugpy (VS Code)

```python
import debugpy

# Listen for debugger connections
debugpy.listen(('0.0.0.0', 5678))
print("Waiting for debugger...")
debugpy.wait_for_client()
```

### Docker Debugging

```bash
# Attach to running container
docker-compose exec pure-sound bash

# Debug with Python debugger
docker-compose exec pure-sound python -m pdb script.py
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def process_audio(file_path):
    logger.info(f"Processing audio file: {file_path}")
    try:
        # Processing logic
        logger.debug(f"Audio details: {audio_info}")
        return True
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
```

---

## Performance Profiling

### Memory Profiling

```bash
# Profile memory usage
python -m memory_profiler script.py

# Detailed line-by-line
mprof run --python script.py
mprof plot
```

### CPU Profiling

```bash
# Profile CPU usage
python -m cProfile -o profile.pstats script.py

# Visualize profile
python -c "import pstats; p = pstats.Stats('profile.pstats'); p.sort_stats('cumulative').print_stats(20)"
```

### Line Profiling

```python
from line_profiler import LineProfiler

def profile_function():
    profiler = LineProfiler()
    profiler.add_function(target_function)
    profiler.runctx('target_function()', globals(), locals())
    profiler.print_stats()
```

---

## Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_audio_processing.py
│   ├── test_analysis.py
│   └── test_security.py
├── integration/             # Integration tests
│   ├── test_api.py
│   └── test_job_queue.py
├── e2e/                     # End-to-end tests
│   ├── test_complete_workflow.py
│   └── test_gui.py
└── fixtures/                # Test data
    ├── audio_samples/
    └── test_configurations/
```

### Running Tests

```bash
# Run all tests
python test_comprehensive.py

# Run with pytest
python -m pytest tests/ -v

# Run specific test category
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/e2e/ -v

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run smoke tests
python test_smoke.py
```

### Writing Tests

```python
import pytest
from audio_processing_enhanced import AudioProcessingEngine

class TestAudioProcessing:
    """Test cases for audio processing engine."""
    
    @pytest.fixture
    def engine(self):
        """Create test engine instance."""
        return AudioProcessingEngine()
    
    @pytest.fixture
    def sample_audio(self, tmp_path):
        """Create sample audio file for testing."""
        audio_file = tmp_path / "test.wav"
        # Create test audio file
        return str(audio_file)
    
    def test_process_audio(self, engine, sample_audio):
        """Test basic audio processing."""
        result = engine.process(
            input_file=sample_audio,
            preset="speech_clean"
        )
        assert result["success"] is True
        assert "output_file" in result
    
    def test_invalid_file(self, engine):
        """Test handling of invalid input file."""
        with pytest.raises(FileNotFoundError):
            engine.process(
                input_file="/nonexistent/file.wav",
                preset="speech_clean"
            )
    
    @pytest.mark.parametrize("preset", [
        "speech_clean",
        "music_enhancement",
        "broadcast"
    ])
    def test_different_presets(self, engine, sample_audio, preset):
        """Test processing with different presets."""
        result = engine.process(
            input_file=sample_audio,
            preset=preset
        )
        assert result["success"] is True
```

---

## Documentation

### Building Documentation

```bash
# Using Sphinx
python -m sphinx -b html docs/ docs/_build/html

# View documentation
open docs/_build/html/index.html
```

### Documentation Standards

- All public classes and functions must have docstrings
- Include type hints in function signatures
- Provide usage examples where helpful
- Document exceptions that may be raised
- Keep README.md up to date with features

---

## Common Tasks

### Adding a New Audio Preset

1. **Define preset in presets.py:**

```python
class Preset(Enum):
    MY_CUSTOM = "my_custom"
    
PRESETS = {
    "my_custom": {
        "description": "Custom preset for special use case",
        "parameters": {
            "bitrate": 192,
            "normalize": True,
            "noise_reduction": True
        }
    }
}
```

2. **Add processing logic in audio_processing_enhanced.py:**

```python
def _apply_custom_preset(self, audio_data, params):
    """Apply custom preset parameters."""
    # Implementation
    return processed_data
```

3. **Add tests:**

```python
def test_custom_preset(self, engine, sample_audio):
    """Test custom preset processing."""
    result = engine.process(
        input_file=sample_audio,
        preset="my_custom"
    )
    assert result["success"] is True
```

### Adding a New API Endpoint

1. **Add route in api_backend.py:**

```python
@self.app.get("/api/v1/new-endpoint")
async def new_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(self.security)
):
    """New endpoint description."""
    if not self._verify_api_key(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Implementation
    return {"result": "data"}
```

2. **Add Pydantic model:**

```python
class NewEndpointResponse(BaseModel):
    result: str
    status: str
```

3. **Add tests:**

```python
def test_new_endpoint(self, api_client):
    """Test new endpoint."""
    response = api_client.get(
        "/api/v1/new-endpoint",
        headers={"Authorization": "Bearer test_key"}
    )
    assert response.status_code == 200
```

### Adding a New Processing Filter

1. **Create filter class in audio_processing_enhanced.py:**

```python
class AudioFilter(ABC):
    """Abstract base class for audio filters."""
    
    @abstractmethod
    def apply(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply filter to audio data."""
        pass

class NoiseReducer(AudioFilter):
    """Noise reduction filter."""
    
    def __init__(self, threshold: float = -40.0):
        self.threshold = threshold
    
    def apply(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply noise reduction."""
        # Implementation
        return filtered_data
```

2. **Integrate with processing pipeline:**

```python
def process_audio(self, audio_data, filters=None):
    """Process audio with optional filters."""
    if filters is None:
        filters = []
    
    for filter_obj in filters:
        audio_data = filter_obj.apply(audio_data)
    
    return audio_data
```

---

## Additional Resources

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Architecture Guide](architecture_design.md) - System architecture
- [Configuration Reference](CONFIGURATION.md) - Configuration options
- [Testing Guide](TESTING_GUIDE.md) - Testing best practices
- [Security Guide](SECURITY.md) - Security considerations

---

**Last Updated:** 2025-02-02  
**Maintainers:** Pure Sound Development Team
