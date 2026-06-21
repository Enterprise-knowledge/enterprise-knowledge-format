#!/usr/bin/env python3
"""Parse an Enterprise Knowledge Format bundle into graph data."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only on hosts without PyYAML.
    print(
        "PyYAML is required. Run with: uv run --with pyyaml python "
        "<ekf-bootstrap-skill-dir>/scripts/parse_ekf_graph.py <bundle>\n"
        "For durable local tooling, use uv init --bare and uv add pyyaml. "
        "Without uv, create a local venv and install requirements there:\n"
        "python3 -m venv .venv && . .venv/bin/activate && "
        "python -m pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)


RESERVED_KNOWLEDGE_FILES = {"index.md", "log.md"}


@dataclass(frozen=True)
class BundleInfo:
    root: Path
    path: str
    bundle_id: str
    title: str
    description: str
    status: str
    owner: Any
    depth: int
    ancestry: list[str]


def relpath(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def read_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("\ufeff"):
        text = text.removeprefix("\ufeff")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            raw_frontmatter = "".join(lines[1:index])
            parsed = yaml.safe_load(raw_frontmatter) or {}
            if not isinstance(parsed, dict):
                raise ValueError(f"{path}: frontmatter must be a YAML mapping")
            return parsed
    raise ValueError(f"{path}: starts a YAML frontmatter block but never closes it")


def text_value(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return str(value)


def owner_value(value: Any) -> Any:
    if isinstance(value, dict):
        return json_safe(value)
    if isinstance(value, str):
        return value
    return json_safe(value) if value is not None else None


def bundle_from_index(root: Path, bundle_root: Path, depth: int, ancestry: list[str]) -> BundleInfo:
    index = bundle_root / "index.md"
    frontmatter = read_frontmatter(index) if index.is_file() else {}
    bundle_meta = frontmatter.get("bundle") if isinstance(frontmatter.get("bundle"), dict) else {}
    fallback_id = bundle_root.name if depth else text_value(frontmatter.get("title"), root.name)
    bundle_id = text_value(bundle_meta.get("id"), fallback_id)
    bundle_path = "." if bundle_root == root else relpath(bundle_root, root)
    current_ancestry = ancestry if depth == 0 else [*ancestry, bundle_id]
    return BundleInfo(
        root=bundle_root,
        path=bundle_path,
        bundle_id=bundle_id,
        title=text_value(frontmatter.get("title"), bundle_id),
        description=text_value(frontmatter.get("description")),
        status=text_value(frontmatter.get("status")),
        owner=owner_value(frontmatter.get("owner")),
        depth=depth,
        ancestry=current_ancestry,
    )


def discover_bundles(root: Path) -> list[BundleInfo]:
    bundles: list[BundleInfo] = []

    def walk(bundle_root: Path, depth: int, ancestry: list[str]) -> None:
        info = bundle_from_index(root, bundle_root, depth, ancestry)
        bundles.append(info)
        nested_root = bundle_root / "bundles"
        if not nested_root.is_dir() or nested_root.is_symlink():
            return
        for child in sorted(nested_root.iterdir(), key=lambda path: path.name):
            if child.is_dir() and not child.is_symlink():
                walk(child, depth + 1, info.ancestry)

    walk(root, 0, [])
    return bundles


def normalize_tags(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [tag for tag in value if isinstance(tag, str)]


def concept_node(path: Path, bundle: BundleInfo, root: Path) -> dict[str, Any]:
    frontmatter = read_frontmatter(path)
    repo_path = relpath(path, root)
    return {
        "id": repo_path,
        "path": repo_path,
        "title": text_value(frontmatter.get("title"), path.stem),
        "type": text_value(frontmatter.get("type")),
        "description": text_value(frontmatter.get("description")),
        "status": text_value(frontmatter.get("status")),
        "owner": owner_value(frontmatter.get("owner")),
        "tags": normalize_tags(frontmatter.get("tags")),
        "bundle_id": bundle.bundle_id,
        "bundle_path": bundle.path,
        "bundle_depth": bundle.depth,
        "bundle_ancestry": bundle.ancestry,
    }


def normalize_related_path(value: Any, source_path: Path, root: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    raw_path = value.strip()
    if raw_path.startswith("/"):
        candidate = root / raw_path.lstrip("/")
    else:
        candidate = source_path.parent / raw_path
    try:
        return candidate.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return raw_path.lstrip("/")


def concept_edges(path: Path, root: Path, known_nodes: set[str]) -> list[dict[str, Any]]:
    frontmatter = read_frontmatter(path)
    related = frontmatter.get("related")
    if not isinstance(related, list):
        return []

    edges: list[dict[str, Any]] = []
    source = relpath(path, root)
    for item in related:
        if not isinstance(item, dict):
            continue
        target = normalize_related_path(item.get("path"), path, root)
        edges.append(
            {
                "source": source,
                "target": target,
                "relation": text_value(item.get("relation")),
                "description": text_value(item.get("description")),
                "name": text_value(item.get("name")),
                "target_missing": target not in known_nodes,
            }
        )
    return edges


def graph_from_bundle(root: Path) -> dict[str, Any]:
    if not root.exists():
        raise ValueError(f"{root}: bundle path does not exist")
    if not root.is_dir():
        raise ValueError(f"{root}: bundle path is not a directory")

    bundles = discover_bundles(root)
    concept_paths: list[tuple[Path, BundleInfo]] = []
    for bundle in bundles:
        knowledge = bundle.root / "knowledge"
        if not knowledge.is_dir() or knowledge.is_symlink():
            continue
        for path in sorted(knowledge.rglob("*.md")):
            if path.is_symlink() or path.name in RESERVED_KNOWLEDGE_FILES:
                continue
            concept_paths.append((path, bundle))

    nodes = [concept_node(path, bundle, root) for path, bundle in concept_paths]
    known_nodes = {node["id"] for node in nodes}
    edges: list[dict[str, Any]] = []
    for path, _bundle in concept_paths:
        edges.extend(concept_edges(path, root, known_nodes))

    bundle_records = [
        {
            "id": bundle.bundle_id,
            "path": bundle.path,
            "title": bundle.title,
            "description": bundle.description,
            "status": bundle.status,
            "owner": bundle.owner,
            "depth": bundle.depth,
            "ancestry": bundle.ancestry,
        }
        for bundle in bundles
    ]

    return {
        "nodes": json_safe(nodes),
        "edges": json_safe(edges),
        "bundles": json_safe(bundle_records),
    }


def write_jsonl(graph: dict[str, Any], output: Any) -> None:
    for bundle in graph["bundles"]:
        print(json.dumps({"record_type": "bundle", **bundle}, sort_keys=True), file=output)
    for node in graph["nodes"]:
        print(json.dumps({"record_type": "node", **node}, sort_keys=True), file=output)
    for edge in graph["edges"]:
        print(json.dumps({"record_type": "edge", **edge}, sort_keys=True), file=output)


def main() -> int:
    parser = argparse.ArgumentParser(description="Parse an EKF bundle into graph data.")
    parser.add_argument("bundle", help="Path to the EKF bundle root")
    parser.add_argument("--output", help="Write graph data to this path instead of stdout")
    parser.add_argument("--format", choices=("json", "jsonl"), default="json", help="Output format")
    args = parser.parse_args()

    root = Path(args.bundle).expanduser().resolve()
    try:
        graph = graph_from_bundle(root)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"EKF graph parse failed: {exc}", file=sys.stderr)
        return 1

    output_handle = None
    try:
        if args.output:
            output_path = Path(args.output).expanduser()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_handle = output_path.open("w", encoding="utf-8")
            output = output_handle
        else:
            output = sys.stdout

        if args.format == "json":
            json.dump(graph, output, indent=2, sort_keys=True)
            print(file=output)
        else:
            write_jsonl(graph, output)
    finally:
        if output_handle is not None:
            output_handle.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
