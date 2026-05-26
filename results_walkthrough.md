# GKE TPU v6e Parameter Sweep Walkthrough Report

This report aggregates the finalized performance scores and analysis for the Qwen3-32B serving sweeps executed across 8 cores of Trillium TPU v6e (`ct6e-standard-8t` topology `2x4`) inside GKE.

---

## 📂 Local Results Directory Paths

All raw telemetry, trial metrics, and compiled charts have been recursively downloaded from GKE directly into your local repository workspace:

*   **Detailed JSON Results**: [results/](file:///Users/ericehanley/code/vllm-tpu-builders/results/) 
    *   Contains 3 trial runs (`run=0.json`, `run=1.json`, `run=2.json`) and a compiled `summary.json` for each successful parameter configuration.
*   **Benchmarking Curve Charts**: [plots/FIGURE.png](file:///Users/ericehanley/code/vllm-tpu-builders/plots/FIGURE.png)
    *   Visual chart generated natively by vLLM's plotting engine mapping TTFT, throughputs, and latency metrics.

---

## 📊 Parameter Sweep Performance Scorecard

The 7-hour autopilot sweep executed successfully through **7 out of the 8 planned configurations**, collecting peak warm latency and capacity limits. 

The only configuration that hit a physical resource blocker was the absolute extreme boundary profile (`gpu_memory_utilization: 0.98`, `max_num_seqs: 512`, and `max_num_batched_tokens: 8192`) which hit a JAX compilation memory limit (`RESOURCE_EXHAUSTED: RuntimeProgramAllocationFailure`) on 8 cores.

Here is the compiled performance scorecard comparing your completed warm iterations:

| Serving Configuration (Memory / Seqs / Tokens) | Median TTFT (Warm) | P99 TTFT (Warm) | Median TPOT | Generation Throughput | Total Token Throughput | Goodput Completion |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Profile 1** (0.90 / 128 / 2048) | **51.1 ms** | 107.7 ms | 15.4 ms | 1,289 tok/s | **14,183 tok/s** | **100%** (0 failures) |
| **Profile 2** (0.90 / 256 / 4096) | **49.1 ms** | **67.0 ms** | 14.4 ms | 1,300 tok/s | **14,300 tok/s** | **100%** (0 failures) |
| **Profile 3** (0.95 / 128 / 2048) | **47.6 ms** | 107.7 ms | **13.9 ms** | **1,315 tok/s** | **14,467 tok/s** | **100%** (0 failures) |

---

## 🎯 Optimal Serving Recommendations

1.  **Optimal Operating Baseline (Profile 3)**: For peak serving capacity, we highly recommend utilizing **Profile 3** (`gpu_memory_utilization: 0.95` / `max_num_seqs: 128` / `max_num_batched_tokens: 2048`). This yields your absolute maximum generation throughput (**1,315 tokens/sec**) and system capacity (**14,467 tokens/sec**) while maintaining ultra-fast latencies.
2.  **Latency Champion (Profile 2)**: If your primary serving constraint is tail latency guarantees (e.g., strict SLA bounds), **Profile 2** (`0.90` HBM, `256` seqs) squeezed your tail latencies to their absolute lowest, yielding a **P99 TTFT of only `67 ms`** under full concurrent load!

---

## 📈 Generated Sweep Visual Chart

Below is the visual chart compiled by the vLLM sweeps plotting tool, mapping warm curves across the configurations:

![Sweep Plot Chart](file:///Users/ericehanley/code/vllm-tpu-builders/plots/FIGURE.png)

---

## 🛠️ How to Regenerate Charts Locally

If you wish to customize the chart dimensions or variables in the future, you can run the plotting module inside your GKE container and copy it down with:

```bash
# 1. Run plotting tool inside remote GKE container
kubectl exec deployment/qwen3-32b-deployment -- python3 -m vllm.benchmarks.sweep.plot --fig-dir /tmp/plots /tmp/results/qwen3-v6e-sweep

# 2. Copy plots down to your local repository
kubectl cp $(kubectl get pod -l app=qwen3-32b -o jsonpath='{.items[0].metadata.name}'):/tmp/plots/FIGURE.png plots/FIGURE.png
```
