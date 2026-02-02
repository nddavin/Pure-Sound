# Pure Sound API Reference

## Overview

Pure Sound provides a comprehensive REST API for audio processing automation, cloud integration, and distributed processing management. This document provides detailed API documentation for all endpoints, request/response formats, and authentication requirements.

## Table of Contents

1. [Authentication](#authentication)
2. [Health & Status](#health--status)
3. [Job Management](#job-management)
4. [Audio Analysis](#audio-analysis)
5. [Presets](#presets)
6. [Node Management](#node-management)
7. [Cloud Storage](#cloud-storage)
8. [Error Handling](#error-handling)
9. [Rate Limiting](#rate-limiting)

---

## Authentication

All API endpoints require authentication via Bearer token (API key).

### API Key Authentication

```bash
# Include API key in Authorization header
curl -X GET "http://localhost:8000/api/v1/jobs" \
  -H "Authorization: Bearer your_api_key"
```

### Environment Configuration

```bash
# Set API key via environment variable
export PURE_SOUND_API_KEY=your_api_key_here
```

### Authentication Methods

| Method | Description | Usage |
|--------|-------------|-------|
| Bearer Token | Standard JWT-style token | `Authorization: Bearer <token>` |
| API Key | Simple API key verification | `X-API-Key: <key>` |

---

## Health & Status

### Health Check

**GET** `/`

Returns the health status of the API server and processing cluster.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "nodes": 5,
  "active_jobs": 12,
  "queue_size": 3
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Service is healthy |
| 503 | Service is unhealthy |

---

## Job Management

### Submit Processing Job

**POST** `/api/v1/jobs`

Submit a new audio processing job for asynchronous execution.

**Request Body:**

```json
{
  "input_file": "/path/to/audio.wav",
  "preset": "speech_clean",
  "quality": "high_quality",
  "output_format": "mp3",
  "bitrate": 192
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | string | Yes | - | Path to input audio file |
| `preset` | string | No | `speech_clean` | Processing preset to use |
| `quality` | string | No | `high_quality` | Output quality level |
| `output_format` | string | No | `mp3` | Output audio format |
| `bitrate` | integer | No | - | Output bitrate (kbps) |

**Response:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Job submitted successfully"
}
```

### Get Job Status

**GET** `/api/v1/jobs/{job_id}

Retrieves the current status and progress of a processing job.

**Response:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "progress": 0.45,
  "created_at": 1699900000.0,
  "started_at": 1699900005.0,
  "completed_at": null,
  "error_message": null,
  "result_url": null
}
```

**Job Status Values:**

| Status | Description |
|--------|-------------|
| `pending` | Job is queued, waiting for processing |
| `running` | Job is currently being processed |
| `completed` | Job completed successfully |
| `failed` | Job failed with an error |
| `cancelled` | Job was cancelled by user |

### Cancel Job

**DELETE** `/api/v1/jobs/{job_id}`

Cancels a pending or running job.

**Response:**

```json
{
  "message": "Job cancelled successfully"
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Job cancelled successfully |
| 400 | Cannot cancel completed job |
| 404 | Job not found |

---

## Audio Analysis

### Analyze Audio

**POST** `/api/v1/analyze`

Analyzes an audio file and returns content detection results.

**Request Body:**

```json
{
  "file_path": "/path/to/audio.wav"
}
```

**Response:**

```json
{
  "content_type": "speech",
  "confidence": 0.95,
  "quality": "high",
  "duration": 120.5,
  "sample_rate": 44100,
  "channels": 2,
  "recommended_format": "mp3",
  "recommended_bitrates": [128, 192, 256],
  "processing_steps": [
    {
      "step": "noise_reduction",
      "parameters": {"threshold": -40}
    },
    {
      "step": "normalization",
      "parameters": {"target_level": -1.0}
    }
  ]
}
```

**Analysis Result Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `content_type` | string | Detected content type (speech, music, mixed) |
| `confidence` | float | Detection confidence score (0-1) |
| `quality` | string | Audio quality assessment |
| `duration` | float | Audio duration in seconds |
| `sample_rate` | integer | Sample rate in Hz |
| `channels` | integer | Number of audio channels |
| `recommended_format` | string | Recommended output format |
| `recommended_bitrates` | array | Recommended bitrate options |
| `processing_steps` | array | Suggested processing steps |

---

## Presets

### List Available Presets

**GET** `/api/v1/presets`

Returns all available processing presets.

**Response:**

```json
{
  "presets": [
    {
      "name": "speech_clean",
      "description": "Optimized for speech content with noise reduction",
      "category": "voice",
      "parameters": {
        "noise_reduction": true,
        "compression": "light",
        "normalization": true
      }
    },
    {
      "name": "music_enhancement",
      "description": "Enhances music recordings with EQ and compression",
      "category": "music",
      "parameters": {
        "eq": "music",
        "compression": "moderate",
        "limiter": true
      }
    }
  ]
}
```

---

## Node Management

### List Processing Nodes

**GET** `/api/v1/nodes`

Returns status information for all processing nodes in the cluster.

**Response:**

```json
{
  "nodes": [
    {
      "node_id": "node-001",
      "status": "active",
      "active_jobs": 3,
      "capabilities": {
        "gpu": true,
        "max_bitrate": 320
      },
      "last_heartbeat": 1699900000.0
    }
  ]
}
```

---

## Cloud Storage

### Upload File

**POST** `/api/v1/storage/upload`

Uploads a file to cloud storage.

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | file | File to upload |
| `path` | string | Destination path in cloud storage |
| `metadata` | JSON | Optional metadata dictionary |

### Download File

**GET** `/api/v1/storage/download`

Downloads a file from cloud storage.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | string | Path to file in cloud storage |
| `destination` | string | Local destination path |

### List Files

**GET** `/api/v1/storage/files`

Lists files in cloud storage.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `prefix` | string | Filter files by prefix |
| `max_results` | integer | Maximum number of results (default: 100) |

---

## Error Handling

### Error Response Format

All errors return responses in the following format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_API_KEY` | 401 | Authentication failed |
| `INPUT_FILE_NOT_FOUND` | 400 | Input file does not exist |
| `JOB_NOT_FOUND` | 404 | Job ID not found |
| `NO_AVAILABLE_NODES` | 503 | No processing nodes available |
| `ANALYSIS_FAILED` | 500 | Audio analysis failed |
| `PROCESSING_FAILED` | 500 | Audio processing failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

### Error Example

```json
{
  "error": {
    "code": "INPUT_FILE_NOT_FOUND",
    "message": "Input file not found: /path/to/audio.wav",
    "details": {
      "file_path": "/path/to/audio.wav"
    }
  }
}
```

---

## Rate Limiting

### Rate Limit Headers

All responses include rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1699903600
```

### Rate Limit Tiers

| Tier | Requests/Hour | Description |
|------|---------------|-------------|
| Free | 100 | Basic API access |
| Pro | 10,000 | Professional use |
| Enterprise | Unlimited | Enterprise deployment |

---

## SDK Clients

### Python SDK

```python
from pure_sound_api import PureSoundAPIClient

# Initialize client
client = PureSoundAPIClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

# Submit job
job = client.submit_job(
    input_file="/path/to/audio.wav",
    preset="speech_clean"
)

# Check status
status = client.get_job_status(job.job_id)
print(f"Progress: {status.progress:.1%}")
```

### JavaScript SDK

```javascript
import { PureSoundAPIClient } from '@puresound/sdk';

const client = new PureSoundAPIClient({
  apiKey: 'your_api_key',
  baseUrl: 'http://localhost:8000'
});

// Submit job
const job = await client.submitJob({
  inputFile: '/path/to/audio.wav',
  preset: 'speech_clean'
});

// Check status
const status = await client.getJobStatus(job.jobId);
console.log(`Progress: ${(status.progress * 100).toFixed(1)}%`);
```

---

## WebSocket API

### Real-time Job Updates

Connect to WebSocket for real-time job progress updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jobs');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`Job ${update.job_id}: ${update.progress * 100}%`);
};
```

### WebSocket Events

| Event | Description |
|-------|-------------|
| `job_started` | Job has started processing |
| `job_progress` | Job progress update |
| `job_completed` | Job completed successfully |
| `job_failed` | Job failed with error |

---

## Versioning

### API Versioning

The API uses URL-based versioning:

- Current version: `v1`
- Access via: `/api/v1/...`

### Version Compatibility

| API Version | Status | Notes |
|-------------|--------|-------|
| v1 | Current | Active development |
| v0.9 | Deprecated | Legacy support |

---

## Quick Start Examples

### cURL - Submit and Monitor Job

```bash
#!/bin/bash
API_KEY="your_api_key"
BASE_URL="http://localhost:8000"

# Submit job
JOB_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/jobs" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input_file": "/app/input/audio.wav", "preset": "speech_clean"}')

JOB_ID=$(echo $JOB_RESPONSE | jq -r '.job_id')
echo "Job submitted: $JOB_ID"

# Monitor progress
while true; do
  STATUS=$(curl -s "$BASE_URL/api/v1/jobs/$JOB_ID" \
    -H "Authorization: Bearer $API_KEY")
  
  STATUS_VALUE=$(echo $STATUS | jq -r '.status')
  PROGRESS=$(echo $STATUS | jq -r '.progress // 0')
  
  echo "Status: $STATUS_VALUE, Progress: $(echo "$PROGRESS * 100" | bc)%"
  
  if [[ "$STATUS_VALUE" == "completed" || "$STATUS_VALUE" == "failed" ]]; then
    break
  fi
  
  sleep 2
done
```

### Python - Batch Processing

```python
import asyncio
from pure_sound_api import PureSoundAPIClient

async def process_batch(file_paths):
    client = PureSoundAPIClient(api_key="your_api_key")
    
    # Submit all jobs
    jobs = []
    for file_path in file_paths:
        job = await client.submit_job(
            input_file=file_path,
            preset="speech_clean"
        )
        jobs.append(job)
    
    # Wait for completion
    results = await asyncio.gather(*[
        client.wait_for_completion(job.job_id)
        for job in jobs
    ])
    
    return results

# Run batch processing
results = asyncio.run(process_batch([
    "/path/to/audio1.wav",
    "/path/to/audio2.wav",
    "/path/to/audio3.wav"
]))
```

---

## Additional Resources

- [Full API Documentation](http://localhost:8000/docs) - Interactive Swagger UI
- [Architecture Guide](architecture_design.md) - System architecture overview
- [Developer Guide](DEVELOPER_GUIDE.md) - Development setup and best practices
- [Configuration Reference](CONFIGURATION.md) - Configuration options

---

**API Version:** 1.0.0  
**Last Updated:** 2025-02-02  
