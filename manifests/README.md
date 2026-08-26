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
| MaaS (postgres, RHCL, connectivity-link, gateway, serving-operators, observability-operators, observability-datasource, enable, model, subscription, telemetry) | `05-maas/` | Module 5 (TP) |
| llm-d + KEDA/WVA | `06-llmd/` | Module 6 (TP) |
| User Workload Monitoring | `07-observability/uwm` | Module 7 |

## Placeholders to fill

- `02-disconnected/` — `REGISTRY_URL`, `QUAY_PROXY_HOST/ORG` (your mirror/cache).
- `03-serving-platform/connection-s3.yaml` — S3 endpoint, bucket, and credentials (`CHANGE_ME`).
- `05-maas/gateway/{clusterip,loadbalancer}/` — `CLUSTER_DOMAIN` (cluster ingress domain), rendered
  via `envsubst`. Use `clusterip/` for RHDP/bare-metal (no LoadBalancer); `loadbalancer/` for cloud.

## Technology Preview

`05-maas/subscription/*` (MaaS CRs) and `06-llmd/autoscaling/variantautoscaling.yaml` (WVA) use
Technology Preview CRDs. Their API groups/fields may differ on your build — validate with
`oc explain <kind>` before applying.

`05-maas/observability-datasource/` is a workaround for a RHOAI 3.4.3 + Cluster Observability
Operator 1.5.1 version gap: the RHOAI Monitoring controller fails to create the default Perses
`cluster-prometheus-datasource` because its generated CR omits the `caCert.namespace` the newer
COO CRD requires, so dashboard panels error with `No datasource found ... name 'undefined'`. This
manifest recreates the datasource (+ SA, RBAC, token secret) with the required field. It (and the
matching `prometheus-web-tls-ca` ConfigMap→Secret mirror in Module 5, Exercise 3) can be dropped
once RHOAI ships a build aligned with COO 1.5.x. See Module 5 for the full explanation.

`05-maas/connectivity-link/authorino-service-ca-trust.yaml` is a workaround for the MaaS Tech
Preview: Authorino's RHEL9 image does not trust the OpenShift service-serving CA, so its HTTPS
auth callouts to `maas-api:8443` fail TLS verification and `GET /maas-api/v1/models` returns an
empty catalog. The manifest supplies two auto-injected ConfigMaps (trusted root bundle + service
CA) that Module 5 mounts into Authorino's cert directory. It can be dropped once MaaS switches its
subscription/API-key checks to TokenReview + SubjectAccessReview (no service-CA callout). See the
manifest header and Module 5 for the full explanation.
