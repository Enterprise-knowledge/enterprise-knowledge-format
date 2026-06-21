---
name: ekf-bootstrap
description: Use when creating, initializing, scaffolding, expanding, validating, linting, parsing, or graph-visualizing an Enterprise Knowledge Format knowledge base, EKF bundle, nested bundle, source area, or starter company knowledge repository.
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

Prefer `uv run python` when `uv` is available on the target host. For persistent Python requirements, prefer a local `pyproject.toml` managed by `uv`; create one with `uv init --bare` when needed, then add requirements with `uv add`. Fall back to `python3` when `uv` is unavailable. If any Python requirement is needed and `uv` is unavailable, create a local virtual environment and install requirements inside it before running the command. Do not rely on user-level or global Python package installs. In restricted environments, set `UV_CACHE_DIR` and `PYTHONPYCACHEPREFIX` to writable temporary paths.

Validate a bundle with the bundled linter:

```sh
uv run --with pyyaml python <ekf-bootstrap-skill-dir>/scripts/validate_ekf.py ./my-company-ekf
```

The validator prints every bad path with a short reason and exits non-zero when the bundle has format problems. Use `--paths-only` when a caller only needs the affected file or directory paths.

Parse a bundle into graph data for visualization:

```sh
uv run --with pyyaml python <ekf-bootstrap-skill-dir>/scripts/parse_ekf_graph.py ./my-company-ekf \
  --output ./my-company-ekf/artifacts/graph/graph.json
```

The parser discovers recursively nested bundles, emits JSON by default, and supports `--format jsonl` when a line-oriented representation is useful.

## Bootstrap Workflow

1. Identify the target directory, root title, owner, and EKF version.
2. Decide whether this is a root enterprise bundle or a nested bundle.
3. Create the required EKF paths: `index.md`, `knowledge/index.md`, and canonical folders.
4. Add recommended paths: `source/`, `artifacts/`, `schemas/`, and `meta/`.
5. Add nested bundles under `bundles/<bundle-id>/` only for independently owned scopes.
6. Write short descriptions everywhere: indexes, bundle listings, sources, artifacts, and relations.
7. Keep concept discovery possible with plain text tools such as `rg` and `grep`.
8. Run `scripts/validate_ekf.py` against the generated or modified EKF bundle before reporting results.

## Graph Visualization Workflow

When asked to visualize an EKF knowledge graph:

1. Validate the bundle with `scripts/validate_ekf.py`.
2. Parse graph data with `scripts/parse_ekf_graph.py`.
3. Start from `assets/graph-template.html` for consistent output. Copy it to one self-contained `.html` artifact under `artifacts/html/` or a nested bundle's `artifacts/html/`.
4. Replace the `__EKF_GRAPH_JSON__` marker with the parsed graph JSON. Do not require a CDN, generated search service, graph database, or separate runtime.
5. Preserve the template's corrected interaction patterns: floating panels over a full-screen canvas, pointer-down concept selection, degree-scaled node sizes, hidden relation labels until relation selection, panel-aware fit, delayed re-fit after force layout settles, pan and zoom, draggable nodes, search, type and bundle coloring, missing-target styling, and relation details.
6. Use `bundle_ancestry` and `bundle_depth` from the parser output to make recursive bundle structure visible. Customize copy, colors, or detail fields only when the user asks or the bundle audience clearly needs it.

Let the parser provide deterministic graph data only. Let the template provide the default graph UI. Let the agent adapt the HTML only where the user's audience or bundle size requires it.

Example template fill:

```sh
python3 - <<'PY'
from pathlib import Path
template = Path("<ekf-bootstrap-skill-dir>/assets/graph-template.html").read_text(encoding="utf-8")
graph = Path("<bundle>/artifacts/graph/graph.json").read_text(encoding="utf-8").replace("</", "<\\/")
out = Path("<bundle>/artifacts/html/knowledge-graph/index.html")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(template.replace("__EKF_GRAPH_JSON__", graph), encoding="utf-8")
PY
```

Graph JSON has this shape:

```json
{
  "nodes": [],
  "edges": [],
  "bundles": []
}
```

Node records include `id`, `path`, `title`, `type`, `description`, `status`, `owner`, `tags`, `bundle_id`, `bundle_path`, `bundle_depth`, and `bundle_ancestry`. Edge records include `source`, `target`, `relation`, `description`, `name`, and `target_missing`. Bundle records include `id`, `path`, `title`, `description`, `status`, `owner`, `depth`, and `ancestry`.

## Source-to-Knowledge Workflow

After the user adds source material, preserve the source/knowledge/artifact split:

1. Inventory source areas under `source/` and nested `bundles/*/source/`.
2. Add or update `ekf-source.yml` manifests for source areas intended for indexing.
3. For source files that are not already markdown, install and use `markitdown` to create markdown renderings before drafting concepts.
4. Store generated markdown renderings under `artifacts/markdown/` or an equivalent bundle-local artifact path, not under `knowledge/`.
5. Draft concepts only under `knowledge/` trees.
6. Put source provenance in `sources` frontmatter and claim-level citations in markdown.
7. Put typed graph edges in `related` frontmatter with short relation descriptions.
8. Keep generated markdown, HTML, diagrams, graph exports, and indexes under `artifacts/`.
9. Leave uncertain extracted knowledge as `status: draft` with honest `confidence` or review metadata when known.

## Source Conversion with MarkItDown

Use `markitdown` for non-markdown source formats that need text extraction before concept drafting. Keep the original source file unchanged under `source/`; the generated markdown rendering is an artifact and support material, not canonical EKF knowledge.

For durable local tooling when `uv` is available:

```sh
uv init --bare
uv add markitdown
uv run python - <<'PY'
from pathlib import Path
from markitdown import MarkItDown

source = Path("source/documents/example.pdf")
target = Path("artifacts/markdown/documents/example.md")
target.parent.mkdir(parents=True, exist_ok=True)
result = MarkItDown().convert(str(source))
target.write_text(result.text_content, encoding="utf-8")
PY
```

For one-off conversion when a persistent project environment is unnecessary, `uv run --with markitdown python` may be used instead. When `uv` is unavailable, create a local virtual environment and install `markitdown` inside it:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install markitdown
python - <<'PY'
from pathlib import Path
from markitdown import MarkItDown

source = Path("source/documents/example.pdf")
target = Path("artifacts/markdown/documents/example.md")
target.parent.mkdir(parents=True, exist_ok=True)
result = MarkItDown().convert(str(source))
target.write_text(result.text_content, encoding="utf-8")
PY
```

After conversion, cite the original source path in concept `sources` frontmatter. Add the markdown rendering to concept `artifacts` only when it helps readers or agents inspect the extracted text. Review generated markdown before using it for claims, especially for tables, diagrams, scanned pages, or files that may contain secrets.

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

For durable local tooling, use `uv` to create or update a `pyproject.toml` and run through that environment:

```sh
uv init --bare
uv add pyyaml
uv run python <ekf-bootstrap-skill-dir>/scripts/validate_ekf.py <bundle>
```

When `uv` is unavailable, create a local virtual environment, install the required Python packages inside it, then use that environment's Python:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install pyyaml
python <ekf-bootstrap-skill-dir>/scripts/validate_ekf.py <bundle>
```

Use the same project environment or virtual environment for `parse_ekf_graph.py` or other Python helper scripts with package requirements.

The validator checks the authoring-conformance rules that are practical to verify mechanically:

- Required bundle paths exist.
- Root and recursively nested bundle indexes have parseable frontmatter with required bundle metadata.
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
