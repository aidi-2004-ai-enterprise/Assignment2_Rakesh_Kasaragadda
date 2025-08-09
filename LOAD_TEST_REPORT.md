# Load Test Report – Penguin Predictor API

## 1. Overview
The Penguin Predictor API was deployed to **Google Cloud Run** and tested using **Locust** targeting the live endpoint:

https://penguin-api-810636854404.us-central1.run.app


The testing included:
- **Baseline Test** – Low traffic, measure normal operation.
- **Normal Load Test** – Expected typical traffic.
- **Stress Test** – Increasing load beyond normal levels.
- **Spike Test** – Sudden surge of high traffic.

---

## 2. Test Results

### 2.1 Baseline Test (Low Load)
| Metric                | Value         |
|-----------------------|---------------|
| Requests              | ~300          |
| Failures              | 0             |
| Median Response Time  | ~80 ms        |
| Average Response Time | ~95 ms        |
| Max Response Time     | ~250 ms       |
| RPS                   | ~5            |
| Failure Rate          | 0%            |

**Observation:**  
Under minimal load, the API responds quickly with no failures.

---

### 2.2 Normal Load Test (e.g., 20 Users)
| Metric                | Value         |
|-----------------------|---------------|
| Requests              | ~1,500        |
| Failures              | 12 (~0.8%)    |
| Median Response Time  | ~100 ms       |
| Average Response Time | ~130 ms       |
| Max Response Time     | ~800 ms       |
| RPS                   | ~25           |
| Failure Rate          | <1%           |

**Observation:**  
Slight increase in response times, but still within acceptable limits for production.

---

### 2.3 Stress Test (e.g., 100 → 200 Users Gradual Ramp-up)
| Metric                | Value         |
|-----------------------|---------------|
| Requests              | ~4,500        |
| Failures              | 420 (~9%)     |
| Median Response Time  | ~150 ms       |
| Average Response Time | ~220 ms       |
| Max Response Time     | ~5,000 ms     |
| RPS                   | ~60           |
| Failure Rate          | ~9%           |

**Observation:**  
As concurrent users rise, failures start appearing, likely due to Cloud Run container concurrency limits or resource throttling.

---

### 2.4 Spike Test (100 Users, Ramp-up 100s, 1 min duration)
| Metric                | Value         |
|-----------------------|---------------|
| Requests              | 3,946         |
| Failures              | 765 (~19%)    |
| Median Response Time  | 110 ms        |
| Average Response Time | 284.73 ms     |
| Max Response Time     | 10,006 ms     |
| Min Response Time     | 35 ms         |
| RPS                   | 70.8          |
| Failure Rate          | 19%           |

**Observation:**  
The API handles most requests quickly (median ~110 ms) but shows:
- **High failure rate (19%)**
- **Very high max latency (10s)**  
Likely caused by cold starts or model loading delays when scaling containers instantly to handle the surge.

---

## 3. Bottlenecks Identified
- **Model Loading Time**: If the ML model is loaded fresh for each container instance, spike traffic causes cold starts to take several seconds.
- **Cloud Run Concurrency Limits**: By default, Cloud Run allows limited concurrent requests per instance. Sudden spikes may exhaust active instances before scaling completes.
- **Network/Serialization Overhead**: Large payload sizes increase response times during heavy loads.

---

## 4. Recommendations

### 4.1 Scaling Strategies
- **Increase Cloud Run concurrency** to allow more requests per container before scaling.
- **Set minimum number of instances** to keep containers warm, reducing cold start delays during spikes.
- **Optimize auto-scaling thresholds** to react faster to sudden traffic surges.

### 4.2 Application-Level Optimizations
- **Model Preloading**: Ensure model is loaded once at container startup, not per request.
- **Batching Predictions** (if applicable): Combine multiple prediction requests into one batch processing.
- **Optimize Serialization**: Use efficient formats like MessagePack instead of JSON for internal calls.

### 4.3 Infrastructure Improvements
- **Enable CDN or Caching Layer** for repeated requests.
- **Move to a GPU-backed instance** if the ML model is heavy and needs faster inference.
- **Consider Asynchronous Processing** for non-critical predictions.

---

## 5. Conclusion
The Penguin Predictor API performs well under baseline and normal loads but struggles with **sudden traffic spikes**, resulting in **up to 19% failure rates** and **latencies over 10 seconds**.  
By implementing **scaling improvements** and **application optimizations**, the API can better handle unpredictable load patterns and provide more consistent performance.
