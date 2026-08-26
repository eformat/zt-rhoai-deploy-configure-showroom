# Workshop manifests

Kustomize manifests applied by the learner, module by module, with a status gate (a `Verify` step)
after each. Paths are referenced from the AsciiDoc pages and are relative to the repo root.

| Phase | Path | Applied in |
|-------|------|-----------|
| Install operator | `01-install/operator` | Module 1 & 2 |
| DataScienceCluster | `01-install/dsc` | Module 1 & 2 |
| Disconnected mirror | `02-disconnected/` | Module 2 |
| vLLM runtime + connection | `03-serving-platform/` | Module 3 |
| vLLM model (qwen25-05b) | `04-vllm/` | Module 4 |
| MaaS (postgres, RHCL, gateway, enable, subscription) | `05-maas/` | Module 5 (TP) |
| llm-d + WVA | `06-llmd/` | Module 6 (TP) |
| User Workload Monitoring | `07-observability/uwm` | Module 7 |

## Placeholders to fill

- `02-disconnected/` — `REGISTRY_URL`, `QUAY_PROXY_HOST/ORG` (your mirror/cache).
- `03-serving-platform/connection-s3.yaml` — S3 endpoint, bucket, and credentials (`CHANGE_ME`).
- `05-maas/gateway/gateway.yaml` — the gateway hostname (cluster ingress domain).

## Technology Preview

`05-maas/subscription/*` (MaaS CRs) and `06-llmd/autoscaling/variantautoscaling.yaml` (WVA) use
Technology Preview CRDs. Their API groups/fields may differ on your build — validate with
`oc explain <kind>` before applying.
