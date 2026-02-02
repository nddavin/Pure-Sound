# Pure Sound Configuration Reference

## Overview

This document provides a comprehensive reference for all configuration options available in Pure Sound. It covers environment variables, configuration files, and API configuration parameters.

## Table of Contents

1. [Configuration Files](#configuration-files)
2. [Environment Variables](#environment-variables)
3. [Application Configuration](#application-configuration)
4. [Processing Configuration](#processing-configuration)
5. [Security Configuration](#security-configuration)
6. [Cloud Configuration](#cloud-configuration)
7. [Docker Configuration](#docker-configuration)
8. [API Configuration](#api-configuration)

---

## Configuration Files

### Main Configuration File

**Location:** `compress_audio_config.json`

```json
{
  "app": {
    "name": "Pure Sound",
    "version": "2.0.0",
    "environment": "development"
  },
  "processing": {
    "default_preset": "speech_clean",
    "default_quality": "high_quality",
    "max_workers": 4,
    "timeout": 300,
    "output_directory": "./output"
  },
  "audio": {
    "sample_rate": 44100,
    "channels": 2,
    "bitrate": 192,
    "format": "mp3"
  },
  "security": {
    "encryption_enabled": false,
    "api_key": null
  },
  "cloud": {
    "provider": "local",
    "bucket_name": null,
    "region": "us-east-1"
  }
}
```

### Docker Environment File

**Location:** `docker/.env`

```bash
# Application Settings
PURE_SOUND_APP_NAME=Pure Sound
PURE_SOUND_VERSION=2.0.0
PURE_SOUND_ENV=development

# Processing Settings
PURE_SOUND_DEFAULT_PRESET=speech_clean
PURE_SOUND_DEFAULT_QUALITY=high_quality
PURE_SOUND_MAX_WORKERS=4
PURE_SOUND_TIMEOUT=300

# Audio Settings
PURE_SOUND_SAMPLE_RATE=44100
PURE_SOUND_CHANNELS=2
PURE_SOUND_BITRATE=192
PURE_SOUND_FORMAT=mp3

# Security Settings
PURE_SOUND_SECURITY_LEVEL=standard
PURE_SOUND_API_KEY=your_api_key_here
PURE_SOUND_ENCRYPTION_ENABLED=false

# Cloud Settings
PURE_SOUND_CLOUD_PROVIDER=aws
PURE_SOUND_S3_BUCKET=your-bucket-name
PURE_SOUND_AWS_REGION=us-east-1
PURE_SOUND_AWS_ACCESS_KEY_ID=your_access_key
PURE_SOUND_AWS_SECRET_ACCESS_KEY=your_secret_key

# API Settings
PURE_SOUND_API_HOST=0.0.0.0
PURE_SOUND_API_PORT=8000
PURE_SOUND_DEBUG=false

# Logging
PURE_SOUND_LOG_LEVEL=INFO
PURE_SOUND_LOG_FILE=/var/log/pure-sound/app.log

# Redis Settings (for job queue)
PURE_SOUND_REDIS_HOST=redis
PURE_SOUND_REDIS_PORT=6379
PURE_SOUND_REDIS_DB=0
```

---

## Environment Variables

### Application Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PURE_SOUND_APP_NAME` | string | `Pure Sound` | Application name |
| `PURE_SOUND_VERSION` | string | `2.0.0` | Application version |
| `PURE_SOUND_ENV` | string | `development` | Environment (development/staging/production) |

### Processing Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PURE_SOUND_DEFAULT_PRESET` | string | `speech_clean` | Default processing preset |
| `PURE_SOUND_DEFAULT_QUALITY` | string | `high_quality` | Default quality setting |
| `PURE_SOUND_MAX_WORKERS` | integer | `4` | Maximum concurrent workers |
| `PURE_SOUND_TIMEOUT` | integer | `300` | Processing timeout in seconds |
| `PURE_SOUND_OUTPUT_DIR` | string | `./output` | Output directory path |

### Audio Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PURE_SOUND_SAMPLE_RATE` | integer | `44100` | Default sample rate (Hz) |
| `PURE_SOUND_CHANNELS` | integer | `2` | Default number of channels |
| `PURE_SOUND_BITRATE` | integer | `192` | Default bitrate (kbps) |
| `PURE_SOUND_FORMAT` | string | `mp3` | Default output format |

### Security Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PURE_SOUND_SECURITY_LEVEL` | string | `standard` | Security level (standard/high/enterprise) |
| `PURE_SOUND_API_KEY` | string | - | API authentication key |
| `PURE_SOUND_ENCRYPTION_ENABLED` | boolean | `false` | Enable AES-256 encryption |
| `PURE_SOUND_SESSION_TIMEOUT` | integer | `3600` | Session timeout in seconds |

### Cloud Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PURE_SOUND_CLOUD_PROVIDER` | string | `local` | Cloud provider (aws/azure/gcp/local) |
| `PURE_SOUND_S3_BUCKET` | string | - | S3 bucket name |
| `PURE_SOUND_AWS_REGION` | string | `us-east-1` | AWS region |
| `PURE_SOUND_AWS_ACCESS_KEY_ID` | string | - | AWS access key |
| `PURE_SOUND_AWS_SECRET_ACCESS_KEY` | string | - | AWS secret key |

### API Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PURE_SOUND_API_HOST` | string | `0.0.0.0` | API server host |
| `PURE_SOUND_API_PORT` | integer | `8000` | API server port |
| `PURE_SOUND_DEBUG` | boolean | `false` | Enable debug mode |
| `PURE_SOUND_CORS_ORIGINS` | string | `*` | CORS allowed origins |

### Logging Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PURE_SOUND_LOG_LEVEL` | string | `INFO` | Log level (DEBUG/INFO/WARNING/ERROR) |
| `PURE_SOUND_LOG_FILE` | string | - | Log file path |
| `PURE_SOUND_LOG_FORMAT` | string | - | Log format string |

### Redis Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PURE_SOUND_REDIS_HOST` | string | `localhost` | Redis host |
| `PURE_SOUND_REDIS_PORT` | integer | `6379` | Redis port |
| `PURE_SOUND_REDIS_DB` | integer | `0` | Redis database number |

---

## Application Configuration

### App Section

```json
{
  "app": {
    "name": "Pure Sound",
    "version": "2.0.0",
    "environment": "development",
    "debug": false,
    "log_level": "INFO"
  }
}
```

### Processing Section

```json
{
  "processing": {
    "default_preset": "speech_clean",
    "default_quality": "high_quality",
    "max_workers": 4,
    "timeout": 300,
    "output_directory": "./output",
    "temporary_directory": "/tmp/pure-sound",
    "cache_enabled": true,
    "cache_ttl": 3600
  }
}
```

### Presets

| Preset Name | Description | Use Case |
|-------------|-------------|----------|
| `speech_clean` | Optimized for speech with noise reduction | Podcasts, lectures |
| `music_enhancement` | Enhanced for music content | Music recordings |
| `broadcast` | Broadcast-ready processing | Radio, TV |
| `voice_over` | Optimized for voice-over | Narration |
| `podcast` | Podcast-specific processing | Podcast production |
| `minimal` | Light processing, minimal changes | Archives |

---

## Audio Configuration

### Format Support

| Format | Extension | Codec | Notes |
|--------|-----------|-------|-------|
| MP3 | .mp3 | libmp3lame | Most compatible |
| AAC | .aac | aac | Apple devices |
| OGG | .ogg | libopus | Open source |
| FLAC | .flac | flac | Lossless |
| WAV | .wav | pcm_s16le | Uncompressed |
| Opus | .opus | libopus | Low bitrate |

### Quality Presets

| Quality | Bitrate (kbps) | Use Case |
|---------|----------------|----------|
| `low_quality` | 96 | Voice only |
| `standard_quality` | 128 | General use |
| `high_quality` | 192 | Music, podcasts |
| `premium_quality` | 256 | High-fidelity |
| `lossless` | - | Archive quality |

---

## Security Configuration

### Basic Security

```json
{
  "security": {
    "encryption_enabled": false,
    "encryption_algorithm": "AES-256",
    "api_key": null,
    "rate_limiting": {
      "enabled": true,
      "requests_per_minute": 60,
      "burst_size": 10
    }
  }
}
```

### Enterprise Security

```json
{
  "security": {
    "encryption_enabled": true,
    "encryption_algorithm": "AES-256-GCM",
    "api_key": "your-enterprise-key",
    "oauth": {
      "enabled": true,
      "client_id": "your-client-id",
      "client_secret": "your-client-secret",
      "token_url": "https://auth.example.com/token"
    },
    "rate_limiting": {
      "enabled": true,
      "requests_per_minute": 600,
      "burst_size": 100
    },
    "ip_whitelisting": {
      "enabled": false,
      "allowed_ips": ["10.0.0.0/8", "192.168.0.0/16"]
    }
  }
}
```

---

## Cloud Configuration

### AWS S3 Configuration

```json
{
  "cloud": {
    "provider": "aws",
    "region": "us-east-1",
    "bucket_name": "your-bucket-name",
    "endpoint_url": null,
    "verify_ssl": true,
    "signed_url_expiry": 3600
  }
}
```

### Azure Blob Storage

```json
{
  "cloud": {
    "provider": "azure",
    "account_name": "your-account",
    "account_key": "your-key",
    "container_name": "your-container",
    "connection_string": "your-connection-string"
  }
}
```

### Google Cloud Storage

```json
{
  "cloud": {
    "provider": "gcp",
    "project_id": "your-project",
    "bucket_name": "your-bucket",
    "credentials_file": "/path/to/credentials.json"
  }
}
```

---

## Docker Configuration

### Docker Compose Override

```yaml
# docker-compose.override.yml
services:
  pure-sound:
    environment:
      - PURE_SOUND_ENV=production
      - PURE_SOUND_MAX_WORKERS=8
      - PURE_SOUND_LOG_LEVEL=INFO
    volumes:
      - ./custom-config.json:/app/config.json:ro
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

### Kubernetes ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pure-sound-config
data:
  PURE_SOUND_ENV: "production"
  PURE_SOUND_DEFAULT_PRESET: "speech_clean"
  PURE_SOUND_MAX_WORKERS: "8"
  PURE_SOUND_LOG_LEVEL: "INFO"
  PURE_SOUND_AWS_REGION: "us-east-1"
  PURE_SOUND_S3_BUCKET: "your-bucket"
```

---

## API Configuration

### FastAPI Configuration

```python
# API configuration options
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": False,
    "title": "Pure Sound API",
    "description": "Enterprise Audio Processing API",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json"
}
```

### CORS Configuration

```python
CORS_CONFIG = {
    "allow_origins": ["*"],  # Configure for production
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["Content-Length", "X-Request-ID"],
    "max_age": 600
}
```

### Rate Limiting

```python
RATE_LIMIT_CONFIG = {
    "default": {
        "requests": 60,
        "seconds": 60
    },
    "authentication": {
        "requests": 10,
        "seconds": 60
    },
    "upload": {
        "requests": 20,
        "seconds": 60
    }
}
```

---

## Environment-Specific Configurations

### Development

```bash
PURE_SOUND_ENV=development
PURE_SOUND_DEBUG=true
PURE_SOUND_LOG_LEVEL=DEBUG
PURE_SOUND_MAX_WORKERS=2
PURE_SOUND_ENCRYPTION_ENABLED=false
```

### Staging

```bash
PURE_SOUND_ENV=staging
PURE_SOUND_DEBUG=false
PURE_SOUND_LOG_LEVEL=INFO
PURE_SOUND_MAX_WORKERS=4
PURE_SOUND_ENCRYPTION_ENABLED=true
PURE_SOUND_RATE_LIMITING_ENABLED=true
```

### Production

```bash
PURE_SOUND_ENV=production
PURE_SOUND_DEBUG=false
PURE_SOUND_LOG_LEVEL=WARNING
PURE_SOUND_MAX_WORKERS=8
PURE_SOUND_ENCRYPTION_ENABLED=true
PURE_SOUND_SECURITY_LEVEL=high
PURE_SOUND_RATE_LIMITING_ENABLED=true
PURE_SOUND_OAUTH_ENABLED=true
```

---

## Configuration Precedence

Configuration is loaded in the following order (highest to lowest priority):

1. **Environment Variables** (highest priority)
2. **Command-line Arguments**
3. **User Configuration File** (`~/.pure-sound/config.json`)
4. **Project Configuration File** (`compress_audio_config.json`)
5. **Docker Environment File** (`docker/.env`)
6. **Default Values** (lowest priority)

---

## Additional Resources

- [Developer Guide](DEVELOPER_GUIDE.md) - Development setup
- [API Reference](API_REFERENCE.md) - API configuration
- [Docker README](README-Docker.md) - Docker deployment
- [Security Guide](SECURITY.md) - Security configuration

---

**Last Updated:** 2025-02-02
