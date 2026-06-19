# Agent Guidance for EKF

This repository defines Enterprise Knowledge Format (EKF). Treat it as a standard, not as an application codebase.

EKF is an opinionated enterprise implementation of OKF and LLM wiki ideas. The long-term direction is to make enterprise knowledge bases scalable for humans and agents through progressive discovery, typed graph frontmatter, source provenance, and generated artifacts.

## Core Direction

When maintaining this repository, preserve these priorities:

1. **Progressive discovery first** - Every bundle index, subbundle index, concept, source, artifact, and relation should have a short description that helps an LLM decide whether to go deeper.
2. **Markdown is canonical** - EKF concepts live in markdown with YAML frontmatter. Source files and generated artifacts support the concepts but do not replace them.
3. **Graph in frontmatter** - Typed relationships belong in the `related` field. Markdown links are useful, but `related` is the primary graph surface.
4. **Enterprise governance without vendor lock-in** - Require ownership, status, timestamps, provenance, and lifecycle metadata. Avoid cloud-specific or tool-specific assumptions in the standard.
5. **Separate knowledge, source, and artifacts** - Curated knowledge goes in `knowledge/`; raw indexed material goes in `source/`; generated renderings go in `artifacts/`.
6. **Use nested bundles for ownership boundaries** - The root bundle coordinates enterprise-wide knowledge. Independently owned domains, platforms, or systems belong in nested bundles under `bundles/`.
7. **Keep EKF searchable with plain text tools** - Frontmatter keys, tags, headings, and paths should remain discoverable with `rg`, `grep`, and a markdown reader.
8. **Keep bootstrap tooling aligned** - When `SPEC.md` changes, review and update `skills/ekf-bootstrap/` so new EKF bundles start from the current standard.
9. **Strict writers, forgiving readers** - Keep authoring expectations clear, but require consumers to tolerate partial, unknown, or draft content.

## Style for SPEC.md Changes

- Use normative words deliberately: `must`, `should`, and `may`.
- Keep required fields few enough that humans and agents can realistically maintain them.
- Prefer lowercase snake_case for machine-readable values such as concept types and relation types.
- Keep tags lowercase and stable. Prefer one documented style per bundle, either kebab-case or snake_case.
- Preserve grep-friendly frontmatter keys and standard headings when changing examples.
- Use examples that are enterprise-generic. Do not anchor the standard to any cloud, database, warehouse, source-control, catalog, or LLM vendor.
- When adding a field, state whether it is required, recommended, or optional.
- When adding a required field, update the conformance section and at least one example.
- When adding a concept type or relation type, keep the core list broad and let enterprises extend it through `schemas/`.
- When changing bundle layout, required fields, recommended folders, concept examples, tags, relation rules, or conformance, update `skills/ekf-bootstrap/SKILL.md` and `skills/ekf-bootstrap/scripts/bootstrap_ekf.py`.
- Keep examples small but realistic enough to guide future generators.

## What Future Agents Should Avoid

- Do not turn EKF into a product-specific catalog schema.
- Do not make generated HTML, diagrams, or graph exports the canonical knowledge layer.
- Do not parse every markdown file in the repository as an EKF concept; only `knowledge/` is the default concept tree.
- Do not turn the root bundle into a dumping ground for child-owned APIs, tables, repositories, or operational details.
- Do not treat a `knowledge/` subbundle as equivalent to a nested bundle with independent ownership, sources, artifacts, and lifecycle.
- Do not remove progressive discovery requirements to make generation easier.
- Do not make basic concept discovery depend on a generated search index, vector database, graph database, or catalog service.
- Do not add heavyweight infrastructure requirements such as a graph database, vector database, workflow engine, or registry.
- Do not introduce source material that contains secrets, credentials, private tokens, or customer data.

## Maintenance Workflow

Prefer `uv` and `uvx` for Python execution and tool-based testing when they are available on the target host. Fall back to `python3` only when `uv` or `uvx` is unavailable. In restricted environments, set `UV_CACHE_DIR` and `UV_TOOL_DIR` to writable temporary paths.

Before editing the standard:

1. Read `SPEC.md`.
2. Identify whether the change affects authoring conformance, consumption conformance, examples, or all three.
3. Keep compatibility with OKF where practical, but prefer EKF clarity when enterprise scale requires an opinionated extension.
4. Update examples and conformance rules together.
5. Update the EKF bootstrap skill when the spec change affects bundle creation.
6. Search for vendor-specific language before finishing.

Suggested verification commands:

```sh
rg -n "[B]igQuery|[G]oogle Cloud|[G]CP|[A]WS|[A]zure|[S]nowflake|[D]atabricks" SPEC.md AGENTS.md
rg -n "[T]ODO|[T]BD|[F]IXME" SPEC.md AGENTS.md skills/ekf-bootstrap
UV_CACHE_DIR=/tmp/uv-cache uv run --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ekf-bootstrap
UV_CACHE_DIR=/tmp/uv-cache PYTHONPYCACHEPREFIX=/tmp/ekf-pycache uv run python -m py_compile skills/ekf-bootstrap/scripts/bootstrap_ekf.py
UV_CACHE_DIR=/tmp/uv-cache UV_TOOL_DIR=/tmp/uv-tools uvx --with pyyaml python -c "import yaml"
```

Vendor names may appear only when discussing what EKF should avoid or when a future section explicitly compares formats. Unresolved placeholders should not remain in the standard.
