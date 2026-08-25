# zt-rhoai-deploy-configure-showroom

Antora/AsciiDoc showroom content for the **RHOAI 3.4 — Deploy & Configure** workshop.

A single, verifiable, **CPU-completable** path to install, configure, serve, govern, scale, and
observe Red Hat OpenShift AI 3.4 on OpenShift Container Platform 4.19–4.21.

## Modules

1. Install (Connected)
2. Install (Disconnected / air-gapped)
3. Configure the Model-Serving Platform
4. Serving with vLLM (CPU)
5. Governing Access with Models-as-a-Service — *Technology Preview*
6. Scaling with Distributed Inference (llm-d + WVA) — *Technology Preview*
7. Observability

## Repo layout

```
content/modules/ROOT/pages/   # AsciiDoc pages (one per module + index/connect/conclusion/cleanup)
content/modules/ROOT/nav.adoc # navigation
content/antora.yml            # component + attribute inventory
manifests/                    # Kustomize per phase, with status gates
site.yml                      # Antora playbook (RHDP theme, output ./www)
```

## Build locally

```bash
make build     # antora -> ./www
make serve     # build + serve at http://localhost:8887
```

## Deploy

Deployment is handled by the sibling **`zt-rhoai-deploy-configure-automation`** repo, a thin
Helm wrapper around the `zt-showroom-deployer` chart. See that repo's README.

## Notes

- All environment-specific values are Antora attributes in `content/antora.yml` — never hard-coded
  in prose.
- Modules 5 and 6 exercise **Technology Preview** features and are flagged as such.
- Manifests under `manifests/` are opinionated templates; several carry `CHANGE_ME` / `REGISTRY_URL`
  placeholders to fill for your environment. Technology Preview CRDs (MaaS, WVA) should be validated
  against your cluster's installed CRDs.
