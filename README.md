# vLLM TPU Builders: Qwen3-32B Serving & Sweeps on GKE TPU v6e (Trillium)

This repository provides automated scripts and Kubernetes manifests to provision a regional Google Kubernetes Engine (GKE) cluster, configure an on-demand TPU v6e (Trillium) single-host slice, serve the `Qwen/Qwen3-32B-Instruct` model using **vLLM**, and run automated performance tuning sweeps.

---

## 🚀 Architecture Overview

Google Cloud TPU v6e (Trillium) offers high-performance, cost-effective serving for large-scale generative AI workloads. This project implements two serving patterns on GKE:

1.  **Standard Serving**: Launches a single high-performance vLLM inference server sharded across the entire 8-core TPU v6e slice.
2.  **Hyperparameter Sweeps**: Runs the automated `vllm bench sweep` pipeline, sweeping combinations of HBM memory allocation boundaries, sequence scheduling queues, prefill token batching, and request rate workloads to pinpoint optimal serving throughput.

```
                         +-----------------------------+
                         |     GKE Regional Cluster    |
                         |   (tpu-builders-vllm-demo)  |
                         +--------------+--------------+
                                        |
                                        v
                         +-----------------------------+
                         |      tpu-v6e-pool Node      |
                         |    (ct6e-standard-8t VM)    |
                         +--------------+--------------+
                                        |
                  +---------------------+---------------------+
                  |                                           |
                  v                                           v
    +---------------------------+               +---------------------------+
    |  qwen3-32b-serving.yaml   |               |    qwen3-32b-sweep.yaml   |
    |                           |               |                           |
    |  Runs standard vLLM server|               |  Executes grid-search     |
    |  on 8 TPU cores sharded  |               |  sweeps over serve/bench  |
    |  via Tensor Parallelism.  |               |  JSON parameter spaces.   |
    +---------------------------+               +---------------------------+
```

---

## 📂 Repository Structure

*   `create_gke_tpu_cluster.sh`: Bash script to provision a custom VPC, subnet, firewall rules, regional GKE cluster, and the Trillium TPU v6e (`ct6e-standard-8t`) node pool.
*   `qwen3-32b-serving.yaml`: Standard production GKE manifest to serve `Qwen3-32B-Instruct` on 8 TPU cores.
*   `qwen3-32b-sweep.yaml`: Benchmark GKE manifest configured to execute `vllm bench sweep serve` parameter sweeps.
*   `serve_hparams.json`: Serving configuration search grid (sweeping HBM utilization, sequence queues, and prefill limits).
*   `bench_hparams.json`: Benchmark client workload rate and evaluation tokens configuration.

---

## 🛠️ Quickstart Guide

### 1. Infrastructure Provisioning
Verify your GCP project is set in `gcloud`, then execute the cluster creation script:
```bash
bash create_gke_tpu_cluster.sh
```
This provisions:
*   VPC: `vllm-tpu-vpc`
*   Regional Cluster: `tpu-builders-vllm-demo` (`us-central1`)
*   TPU Node Pool: `tpu-v6e-pool` containing 1 x on-demand `ct6e-standard-8t` (8 physical TPU cores).

### 2. Deploying the standard vLLM Inference Server
To start a standard production server sharded over 8 TPU cores with Tensor Parallelism (TP=8):
```bash
kubectl apply -f qwen3-32b-serving.yaml
```

### 3. Running Automated Parameter Sweeps
To launch the grid-search tuning pipeline to find optimal performance boundaries for your workload:
```bash
kubectl apply -f qwen3-32b-sweep.yaml
```

---

## ⚙️ Sweep Configurations

### Serving Sweeps (`serve_hparams.json`)
Sweeps across 8 combinations to explore optimal engine capacity:
*   **HBM Allocation (`gpu_memory_utilization`)**: `0.90` (safe baseline), `0.95` (optimized), `0.98` (extreme physical capacity).
*   **Sequence Concurrency (`max_num_seqs`)**: `128`, `256`, `512`.
*   **Prefill Batching (`max_num_batched_tokens`)**: `2048`, `4096`, `8192`.
*   **Model Limit (`max_model_len`)**: Enforced at `4096` across all sweeps.

### Workload Sweeps (`bench_hparams.json`)
Evaluates the serving grid against a dedicated target rate:
*   **Request Rate**: `16` requests/second.
*   **Input Prompt Length**: `100` tokens.
*   **Output Generation Length**: `100` tokens.
*   **Shared Prefix Length**: `100` tokens.
