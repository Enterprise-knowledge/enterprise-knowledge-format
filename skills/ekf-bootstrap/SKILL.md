---
name: ekf-bootstrap
description: Use when creating, initializing, scaffolding, or expanding an Enterprise Knowledge Format knowledge base, EKF bundle, nested bundle, source area, or starter company knowledge repository.
---

# EKF Bootstrap

Use this skill to create an Enterprise Knowledge Format (EKF) starter knowledge base that follows the repository's `SPEC.md`.

## Source of Truth

Before creating or changing an EKF bundle, read the local `SPEC.md` from the EKF standard repository when it is available. Treat this skill as an operational helper, not as a replacement for the specification.

If `SPEC.md` and this skill disagree, follow `SPEC.md` and update this skill afterward.

## Quick Bootstrap

Use the bundled script for a new starter bundle:

```sh
uv run python skills/ekf-bootstrap/scripts/bootstrap_ekf.py ./my-company-ekf \
  --title "Example Enterprise Knowledge Base" \
  --owner "Enterprise Architecture"
```

Add starter nested bundles when the user already knows major ownership scopes:

```sh
uv run python skills/ekf-bootstrap/scripts/bootstrap_ekf.py ./my-company-ekf \
  --title "Example Enterprise Knowledge Base" \
  --owner "Enterprise Architecture" \
  --nested-bundle customer-platform \
  --nested-bundle billing-platform
```

The script creates only starter files. After it runs, customize names, descriptions, owners, tags, source manifests, and relations for the real organization.

Prefer `uv run python` when `uv` is available on the target host. Fall back to `python3` when `uv` is unavailable. In restricted environments, set `UV_CACHE_DIR` to a writable temporary path.

## Bootstrap Workflow

1. Identify the target directory, root title, owner, and EKF version.
2. Decide whether this is a root enterprise bundle or a nested bundle.
3. Create the required EKF paths: `index.md`, `knowledge/index.md`, and canonical folders.
4. Add recommended paths: `source/`, `artifacts/`, `schemas/`, and `meta/`.
5. Add nested bundles under `bundles/<bundle-id>/` only for independently owned scopes.
6. Write short descriptions everywhere: indexes, bundle listings, sources, artifacts, and relations.
7. Keep concept discovery possible with plain text tools such as `rg` and `grep`.
8. Run a quick validation pass before reporting results.

## Placement Rules

Put knowledge in the lowest bundle that has clear ownership and enough context to maintain it.

Use the root bundle for:

- Enterprise-wide indexes and maps.
- Shared governance, schemas, and conventions.
- Cross-domain architecture and integration concepts.
- Glossary terms used across multiple child bundles.

Use nested bundles for:

- Team-owned domains, platforms, systems, or products.
- Source material and artifacts that belong mostly to that scope.
- Concepts whose lifecycle follows a specific owner.

Do not dump child-owned APIs, database tables, repositories, or runbooks into the root bundle.

## Required Starter Shape

A root EKF starter should include:

```text
index.md
knowledge/index.md
source/index.md
artifacts/index.md
schemas/types.yml
schemas/relations.yml
meta/conventions.md
meta/governance.md
meta/ingestion.md
```

A nested bundle starter should include the same local shape under `bundles/<bundle-id>/`, with `bundle.kind: nested` and `bundle.parent: /`.

## Concept Starters

When adding a concept, include at minimum:

```yaml
---
type: service
title: Example Service
description: Short description for progressive discovery.
status: draft
owner:
  name: Example Team
updated: 2026-06-19T00:00:00Z
sources: []
related: []
---
```

Prefer adding `domain`, `system`, `tags`, `confidence`, `review`, and `artifacts` when known.

## Verification

For a generated or modified EKF bundle, run text checks like:

```sh
rg -n "[T]ODO|[T]BD|[F]IXME" <bundle>
rg -n "^type:|^title:|^description:|^tags:|relation:" <bundle>/knowledge <bundle>/bundles
```

If `rg` is unavailable, use `grep -R --line-number`.

For skill validation in this repository, prefer:

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ekf-bootstrap
UV_CACHE_DIR=/tmp/uv-cache PYTHONPYCACHEPREFIX=/tmp/ekf-pycache uv run python -m py_compile skills/ekf-bootstrap/scripts/bootstrap_ekf.py
UV_CACHE_DIR=/tmp/uv-cache UV_TOOL_DIR=/tmp/uv-tools uvx --with pyyaml python -c "import yaml"
```

Check that:

- Required root paths exist.
- Every nested bundle has `index.md` and `knowledge/index.md`.
- Indexes contain short descriptions.
- Concepts live only under `knowledge/` trees unless explicitly configured.
- Source and artifact markdown are not treated as concepts.
