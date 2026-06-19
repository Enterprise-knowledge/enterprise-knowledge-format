# Enterprise Knowledge Format

Enterprise Knowledge Format (EKF) is an opinionated enterprise implementation of Open Knowledge Format and LLM wiki ideas.

EKF is designed for large company knowledge bases maintained by humans and agents together. It keeps markdown as the canonical knowledge layer, uses YAML frontmatter for ownership, provenance, tags, and graph relationships, and separates curated knowledge from indexed source material and generated artifacts.

## Start Here

- [SPEC.md](SPEC.md) defines the EKF standard.
- [AGENTS.md](AGENTS.md) defines maintenance guidance for future agents.
- [skills/ekf-bootstrap](skills/ekf-bootstrap/SKILL.md) contains a bootstrap skill and script for creating starter EKF bundles.

## Core Ideas

- Progressive discovery through short descriptions on indexes, concepts, sources, artifacts, and relations.
- Typed knowledge graph edges in `related` frontmatter.
- Nested bundles under `bundles/` for independently owned domains, platforms, and systems.
- Canonical concepts under `knowledge/`.
- Raw or mirrored material under `source/`.
- Generated representations under `artifacts/`.
- Plain text discoverability with `rg`, `grep`, and stable markdown/frontmatter conventions.

## Bootstrap A Knowledge Base

Prefer `uv` when available:

```sh
uv run python skills/ekf-bootstrap/scripts/bootstrap_ekf.py ./my-company-ekf \
  --title "Example Enterprise Knowledge Base" \
  --owner "Enterprise Architecture" \
  --nested-bundle customer-platform
```

Fallback:

```sh
python3 skills/ekf-bootstrap/scripts/bootstrap_ekf.py ./my-company-ekf \
  --title "Example Enterprise Knowledge Base" \
  --owner "Enterprise Architecture" \
  --nested-bundle customer-platform
```

## Status

Draft v0.1.

