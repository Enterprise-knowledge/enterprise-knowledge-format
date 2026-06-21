---
name: ekf-bootstrap
description: Use when creating, initializing, scaffolding, expanding, validating, or linting an Enterprise Knowledge Format knowledge base, EKF bundle, nested bundle, source area, or starter company knowledge repository.
---

# EKF Bootstrap

Use this skill to create or expand an Enterprise Knowledge Format (EKF) knowledge base that follows the bundled EKF specification.

## Source of Truth

Before creating or changing an EKF bundle, read `references/SPEC.md` from this skill directory. That bundled copy makes the skill self-contained after installation with `npx skills`.

When working inside the EKF standard repository itself, also check the repository root `SPEC.md`. If the repository root spec and bundled spec disagree, follow the root `SPEC.md` and update `references/SPEC.md` before finishing.

Treat this skill as an operational helper, not as a replacement for the specification.

## Quick Bootstrap

Resolve script paths relative to this skill directory. For example, in Codex global installs this directory is usually `~/.codex/skills/ekf-bootstrap`.

Use the bundled script for a new starter bundle:

```sh
uv run python <ekf-bootstrap-skill-dir>/scripts/bootstrap_ekf.py ./my-company-ekf \
  --title "Example Enterprise Knowledge Base" \
  --owner "Enterprise Architecture"
```

Add starter nested bundles when the user already knows major ownership scopes:

```sh
uv run python <ekf-bootstrap-skill-dir>/scripts/bootstrap_ekf.py ./my-company-ekf \
  --title "Example Enterprise Knowledge Base" \
  --owner "Enterprise Architecture" \
  --nested-bundle customer-platform \
  --nested-bundle billing-platform
```

The script creates only starter files. After it runs, customize names, descriptions, owners, tags, source manifests, and relations for the real organization.

Prefer `uv run python` when `uv` is available on the target host. Fall back to `python3` when `uv` is unavailable. In restricted environments, set `UV_CACHE_DIR` to a writable temporary path.

Validate a bundle with the bundled linter:

```sh
uv run --with pyyaml python <ekf-bootstrap-skill-dir>/scripts/validate_ekf.py ./my-company-ekf
```

The validator prints every bad path with a short reason and exits non-zero when the bundle has format problems. Use `--paths-only` when a caller only needs the affected file or directory paths.

## Bootstrap Workflow

1. Identify the target directory, root title, owner, and EKF version.
2. Decide whether this is a root enterprise bundle or a nested bundle.
3. Create the required EKF paths: `index.md`, `knowledge/index.md`, and canonical folders.
4. Add recommended paths: `source/`, `artifacts/`, `schemas/`, and `meta/`.
5. Add nested bundles under `bundles/<bundle-id>/` only for independently owned scopes.
6. Write short descriptions everywhere: indexes, bundle listings, sources, artifacts, and relations.
7. Keep concept discovery possible with plain text tools such as `rg` and `grep`.
8. Run `scripts/validate_ekf.py` against the generated or modified EKF bundle before reporting results.

## Source-to-Knowledge Workflow

After the user adds source material, preserve the source/knowledge/artifact split:

1. Inventory source areas under `source/` and nested `bundles/*/source/`.
2. Add or update `ekf-source.yml` manifests for source areas intended for indexing.
3. Draft concepts only under `knowledge/` trees.
4. Put source provenance in `sources` frontmatter and claim-level citations in markdown.
5. Put typed graph edges in `related` frontmatter with short relation descriptions.
6. Keep generated HTML, diagrams, graph exports, and indexes under `artifacts/`.
7. Leave uncertain extracted knowledge as `status: draft` with honest `confidence` or review metadata when known.

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

## Bundle Validation

For a generated or modified EKF bundle, run:

```sh
uv run --with pyyaml python <ekf-bootstrap-skill-dir>/scripts/validate_ekf.py <bundle>
```

When `uv` is unavailable, install PyYAML in the active Python environment, then use `python3`:

```sh
python3 -m pip install --user pyyaml
python3 <ekf-bootstrap-skill-dir>/scripts/validate_ekf.py <bundle>
```

If the host blocks user-level installs, create and activate a virtual environment first, then run `python -m pip install pyyaml`.

The validator checks the authoring-conformance rules that are practical to verify mechanically:

- Required bundle paths exist.
- Root and nested bundle indexes have parseable frontmatter with required bundle metadata.
- Every `knowledge/` directory has an `index.md`.
- Concept markdown under `knowledge/` has YAML frontmatter and required fields.
- `sources`, `related`, and `tags` have the expected list shapes.
- Every `related` entry has `name`, `path`, `relation`, and `description`.
- Markdown outside canonical concept trees is not treated as a concept, but invalid frontmatter is still reported.

Run optional text checks when useful:

```sh
rg -n "[T]ODO|[T]BD|[F]IXME" <bundle>
rg -n "^type:|^title:|^description:|^tags:|relation:" <bundle>/knowledge <bundle>/bundles
```

If `rg` is unavailable, use `grep -R --line-number`.
