# zt-rhoai-deploy-configure-showroom

Antora/AsciiDoc showroom content for the **RHOAI Deploy & Configure** workshop.

A single, verifiable, **CPU-completable** path to install, configure, serve, govern, scale, and
observe Red Hat OpenShift AI on OpenShift Container Platform 4.19+. Supports **RHOAI 3.4 and 3.5**
from one codebase — version-specific content is gated by `ifeval` blocks on the `rhoai_version`
Antora attribute.

## Modules

1. Install (Connected)
2. Install (Disconnected / air-gapped)
3. Configure the Model-Serving Platform
4. Serving with vLLM (CPU)
5. Governing Access with Models-as-a-Service — *Technology Preview*
5a. External Models with MaaS (llm-katan simulator)
6. Scaling with Distributed Inference (llm-d + KEDA) — *Technology Preview*
7. Observability

## Repo layout

```
content/modules/ROOT/pages/   # AsciiDoc pages (one per module + index/connect/conclusion/cleanup)
content/modules/ROOT/nav.adoc # navigation
content/antora.yml            # component + attribute inventory (rhoai_version: "3.4" default)
manifests/                    # Kustomize per phase — version-specific files use -35 suffix
site.yml                      # Antora playbook — 3.4 build (output ./www)
site-35.yml                   # Antora playbook — 3.5 build (overrides rhoai_version + MaaS attrs)
```

## Version strategy

Content that differs between 3.4 and 3.5 uses `ifeval` blocks keyed on `{rhoai_version}`:

```asciidoc
ifeval::["{rhoai_version}" == "3.5"]
... 3.5-specific step ...
endif::[]
```

Participants never pick a tab — the correct version is pre-selected by the build. Manifest files
that differ between versions use a `-35` suffix (e.g. `dsc-maas-patch-35.yaml`,
`datasciencecluster-34.yaml` beside `datasciencecluster.yaml`).

Key 3.4 → 3.5 differences:
| Area | 3.4 | 3.5 |
|------|-----|-----|
| MaaS in DSC | `kserve.modelsAsService` | `aigateway.modelsAsAService` |
| maas-api namespace | `redhat-ods-applications` | `redhat-ai-gateway-infra` |
| DSC ready condition | `ModelsAsServiceReady` | `AIGatewayReady` |
| Observability datasource | `PersesDatasource` workaround | `PersesGlobalDatasource` |
| Authorino CA trust | manual step required | pre-configured |
| External models | single `ExternalModel` CR | `ExternalProvider` + `ExternalModel` |

## Build locally

```bash
# 3.4 build (default)
make build      # antora site.yml -> ./www
make serve      # build + serve at http://localhost:8887

# 3.5 build
make build-35   # antora site-35.yml -> ./www-35
make serve-35   # build-35 + serve at http://localhost:8887
```

## Deploy to a cluster

Deployment is via the sibling **`zt-rhoai-deploy-configure-automation`** repo (thin Helm wrapper
around `zt-showroom-deployer`).

```bash
cd ~/git/zt-rhoai-deploy-configure-automation

# Deploy 3.4 (namespace: showroom-rhoai-deploy-34)
export KUBECONFIG=~/.kube/config.fde
make deploy-34 CHART=~/git/zt-showroom-deployer

# Deploy 3.5 (namespace: showroom-rhoai-deploy-35)
make deploy-35 CHART=~/git/zt-showroom-deployer

# Status / uninstall
make status-34 && make status-35
make uninstall-34   # or uninstall-35
```

Side-by-side values files for prelude1 (`cluster-5cr5g`):
- `values-rhoai-deploy-configure-34-prelude1.yaml` — uses `site.yml`
- `values-rhoai-deploy-configure-35-prelude1.yaml` — uses `site-35.yml`

**Important:** `site-35.yml` must be pushed to GitHub before deploying 3.5 — the showroom
antora builder clones from the git remote, not the local filesystem.

## Notes

- All environment-specific values are Antora attributes in `content/antora.yml` — never hard-coded
  in prose. Cluster coordinates (`openshift_api_url`, `rhoai_dashboard_url`, etc.) are injected at
  deploy time via the `showroom-userdata` ConfigMap.
- Modules 5, 5a, and 6 exercise **Technology Preview** features and are flagged as such.
- Manifests under `manifests/` are opinionated templates. Technology Preview CRDs (`MaaSSubscription`,
  `ExternalModel`, `LLMInferenceService`) should be validated against your cluster's installed CRDs.
- `manifests/05-maas/llm-katan-simulator/` contains a vendored copy of the llm-katan Helm chart
  from `ai-gateway-payload-processing`. Update it when the upstream chart changes.
