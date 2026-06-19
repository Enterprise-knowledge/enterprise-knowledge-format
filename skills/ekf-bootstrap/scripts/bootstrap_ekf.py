#!/usr/bin/env python3
"""Create a starter Enterprise Knowledge Format bundle."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_TYPES = [
    "domain",
    "system",
    "service",
    "api",
    "api_endpoint",
    "database",
    "schema",
    "table",
    "codebase",
    "module",
    "business_process",
    "decision",
    "policy",
    "glossary_term",
]

DEFAULT_RELATIONS = [
    "related_to",
    "contains",
    "part_of",
    "depends_on",
    "supports",
    "implements",
    "calls",
    "reads_from",
    "writes_to",
    "publishes",
    "subscribes_to",
    "derived_from",
    "owned_by",
    "governed_by",
]

DISPLAY_NAMES = {
    "apis": "APIs",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "enterprise"


def write_new(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def yaml_string(value: str) -> str:
    return json.dumps(value)


def nested_bundle_lines(bundle_ids: list[str]) -> str:
    if not bundle_ids:
        return "Add independently owned child bundles under `bundles/` and describe each one here.\n"
    return "\n".join(
        f"- [{bundle_id.replace('-', ' ').title()}](bundles/{bundle_id}/) - Starter nested bundle for {bundle_id.replace('-', ' ')}."
        for bundle_id in bundle_ids
    ) + "\n"


def root_index(
    title: str,
    owner: str,
    ekf_version: str,
    updated: str,
    kind: str,
    bundle_id: str,
    parent: str | None,
    nested_bundles: list[str],
) -> str:
    parent_line = f"  parent: {yaml_string(parent)}\n" if parent else ""
    nested_section = nested_bundle_lines(nested_bundles)
    return f"""---
type: bundle
title: {yaml_string(title)}
description: {yaml_string(f"Root discovery index for {title}.")}
ekf_version: {yaml_string(ekf_version)}
bundle:
  id: {yaml_string(bundle_id)}
  kind: {yaml_string(kind)}
{parent_line}status: draft
owner:
  name: {yaml_string(owner)}
updated: {updated}
---

# {title}

This EKF bundle is the discovery entrypoint for enterprise knowledge.

## Knowledge

- [Knowledge](knowledge/) - Canonical concepts, indexes, and graph-oriented markdown.

## Sources

- [Sources](source/) - Raw or mirrored material used to generate and support concepts.

## Artifacts

- [Artifacts](artifacts/) - Generated representations such as HTML, diagrams, graph exports, and indexes.

## Nested Bundles

{nested_section}
"""


def knowledge_index(title: str, owner: str, updated: str) -> str:
    return f"""---
type: index
title: {yaml_string(f"{title} Knowledge")}
description: "Top-level index for canonical EKF concepts in this bundle."
status: draft
owner:
  name: {yaml_string(owner)}
updated: {updated}
---

# {title} Knowledge

Use this index to decide which subbundle or concept to open next.

## Subbundles

- [Domains](domains/) - Business and technical domains.
- [Systems](systems/) - Systems, platforms, services, and applications.
- [APIs](apis/) - API contracts, endpoints, events, and integration behavior.
- [Data](data/) - Databases, schemas, tables, lineage, and data contracts.
- [Code](code/) - Codebases, modules, classes, and important implementation concepts.
- [Processes](processes/) - Business processes, operations, runbooks, and decisions.
- [Glossary](glossary/) - Shared enterprise terminology.

## Core Concepts

Add high-value concepts here with one-sentence descriptions.
"""


def simple_index(title: str, description: str, owner: str, updated: str) -> str:
    return f"""---
type: index
title: {yaml_string(title)}
description: {yaml_string(description)}
status: draft
owner:
  name: {yaml_string(owner)}
updated: {updated}
---

# {title}

{description}

## Core Concepts

Add concepts here with short descriptions.
"""


def source_index(title: str) -> str:
    return f"""# {title} Sources

Raw, mirrored, extracted, or synchronized material belongs here. Add an `ekf-source.yml` manifest to each source area intended for indexing.
"""


def artifacts_index(title: str) -> str:
    return f"""# {title} Artifacts

Generated representations belong here. Keep canonical knowledge in `knowledge/`.
"""


def yaml_list(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) + "\n"


def conventions(title: str) -> str:
    return f"""# {title} Conventions

## Tags

Use lowercase tags. Choose either kebab-case or snake_case for this bundle and keep it consistent.

## Search

Prefer `rg` for text discovery and fall back to `grep -R --line-number` when `rg` is unavailable.
"""


def governance(title: str, owner: str) -> str:
    return f"""# {title} Governance

Default owner: {owner}

Document review expectations, lifecycle rules, and allowed local extensions here.
"""


def ingestion(title: str) -> str:
    return f"""# {title} Ingestion

Document source sync, redaction, indexing, and artifact generation workflows here.
"""


def create_bundle(
    root: Path,
    title: str,
    owner: str,
    ekf_version: str,
    kind: str,
    parent: str | None,
    force: bool,
    nested_bundles: list[str] | None = None,
) -> None:
    updated = now_iso()
    bundle_id = slugify(title)

    write_new(
        root / "index.md",
        root_index(title, owner, ekf_version, updated, kind, bundle_id, parent, nested_bundles or []),
        force,
    )
    write_new(root / "log.md", f"# {title} Log\n\n## {updated[:10]}\n\n- Created EKF starter bundle.\n", force)

    knowledge = root / "knowledge"
    write_new(knowledge / "index.md", knowledge_index(title, owner, updated), force)
    for name, description in {
        "domains": "Business and technical domains in this bundle.",
        "systems": "Systems, platforms, services, and applications in this bundle.",
        "apis": "API contracts, endpoints, events, and integration behavior.",
        "data": "Databases, schemas, tables, lineage, and data contracts.",
        "code": "Codebases, modules, classes, and important implementation concepts.",
        "processes": "Business processes, operations, runbooks, and decisions.",
        "glossary": "Shared terminology for this bundle.",
    }.items():
        display_name = DISPLAY_NAMES.get(name, name.title())
        write_new(knowledge / name / "index.md", simple_index(display_name, description, owner, updated), force)

    write_new(root / "source" / "index.md", source_index(title), force)
    write_new(root / "artifacts" / "index.md", artifacts_index(title), force)
    write_new(root / "schemas" / "types.yml", yaml_list(DEFAULT_TYPES), force)
    write_new(root / "schemas" / "relations.yml", yaml_list(DEFAULT_RELATIONS), force)
    write_new(root / "meta" / "conventions.md", conventions(title), force)
    write_new(root / "meta" / "governance.md", governance(title, owner), force)
    write_new(root / "meta" / "ingestion.md", ingestion(title), force)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a starter EKF bundle.")
    parser.add_argument("target", help="Directory where the EKF bundle should be created")
    parser.add_argument("--title", default="Enterprise Knowledge Base", help="Root bundle title")
    parser.add_argument("--owner", default="Enterprise Architecture", help="Default owner name")
    parser.add_argument("--ekf-version", default="0.1", help="EKF version to declare")
    parser.add_argument("--nested-bundle", action="append", default=[], help="Nested bundle id to create under bundles/")
    parser.add_argument("--force", action="store_true", help="Overwrite existing starter files")
    args = parser.parse_args()

    target = Path(args.target).expanduser().resolve()
    nested_ids = [slugify(bundle_id) for bundle_id in args.nested_bundle]
    create_bundle(target, args.title, args.owner, args.ekf_version, "root", None, args.force, nested_ids)

    for nested_id in nested_ids:
        nested_title = nested_id.replace("-", " ").title()
        create_bundle(target / "bundles" / nested_id, nested_title, args.owner, args.ekf_version, "nested", "/", args.force)

    print(f"Created EKF starter at {target}")
    if args.nested_bundle:
        print(f"Created {len(args.nested_bundle)} nested bundle(s)")


if __name__ == "__main__":
    main()
