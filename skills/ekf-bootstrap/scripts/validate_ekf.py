#!/usr/bin/env python3
"""Validate an Enterprise Knowledge Format bundle."""

from __future__ import annotations

import argparse
import re
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
        "<ekf-bootstrap-skill-dir>/scripts/validate_ekf.py <bundle>\n"
        "For durable local tooling, use uv init --bare and uv add pyyaml. "
        "Without uv, create a local venv and install requirements there:\n"
        "python3 -m venv .venv && . .venv/bin/activate && "
        "python -m pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)


CONCEPT_REQUIRED_FIELDS = {
    "type",
    "title",
    "description",
    "status",
    "owner",
    "updated",
    "sources",
    "related",
}
RELATION_REQUIRED_FIELDS = {"name", "path", "relation", "description"}
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


@dataclass(frozen=True)
class Issue:
    path: Path
    message: str


def relpath(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix() or "."
    except ValueError:
        return path.as_posix()


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (date, datetime)):
        return True
    if isinstance(value, dict):
        return bool(value)
    return True


def read_markdown(path: Path, issues: list[Issue]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        issues.append(Issue(path, "is not valid UTF-8 markdown"))
    except OSError as exc:
        issues.append(Issue(path, f"could not be read: {exc}"))
    return None


def split_frontmatter(path: Path, text: str, issues: list[Issue]) -> tuple[dict[str, Any] | None, str, bool]:
    if text.startswith("\ufeff"):
        text = text.removeprefix("\ufeff")

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return None, text, False

    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            raw_frontmatter = "".join(lines[1:index])
            body = "".join(lines[index + 1 :])
            try:
                parsed = yaml.safe_load(raw_frontmatter) or {}
            except yaml.YAMLError as exc:
                issues.append(Issue(path, f"has invalid YAML frontmatter: {exc}"))
                return None, body, True
            if not isinstance(parsed, dict):
                issues.append(Issue(path, "frontmatter must be a YAML mapping"))
                return None, body, True
            return parsed, body, True

    issues.append(Issue(path, "starts a YAML frontmatter block but never closes it"))
    return None, "", True


def markdown_has_h1(body: str) -> bool:
    return any(line.startswith("# ") and line[2:].strip() for line in body.splitlines())


def validate_markdown_file(
    path: Path, issues: list[Issue], require_h1: bool = False
) -> tuple[dict[str, Any] | None, str, bool]:
    text = read_markdown(path, issues)
    if text is None:
        return None, "", False

    frontmatter, body, had_frontmatter = split_frontmatter(path, text, issues)
    if require_h1 and not markdown_has_h1(body):
        issues.append(Issue(path, "should contain a top-level markdown heading"))
    return frontmatter, body, had_frontmatter


def validate_bundle_index(path: Path, frontmatter: dict[str, Any] | None, had_frontmatter: bool, root_bundle: bool, issues: list[Issue]) -> None:
    if not had_frontmatter or frontmatter is None:
        issues.append(Issue(path, "bundle index must start with YAML frontmatter"))
        return

    for key in ("type", "title", "description", "owner", "status", "updated"):
        if not has_value(frontmatter.get(key)):
            issues.append(Issue(path, f"bundle index is missing non-empty `{key}`"))

    if frontmatter.get("type") != "bundle":
        issues.append(Issue(path, "bundle index `type` must be `bundle`"))

    if root_bundle and not has_value(frontmatter.get("ekf_version")):
        issues.append(Issue(path, "root bundle index is missing non-empty `ekf_version`"))

    bundle = frontmatter.get("bundle")
    if not isinstance(bundle, dict):
        issues.append(Issue(path, "bundle index is missing `bundle` mapping"))
        return

    if not has_value(bundle.get("id")):
        issues.append(Issue(path, "bundle metadata is missing non-empty `bundle.id`"))
    if root_bundle:
        if bundle.get("kind") != "root":
            issues.append(Issue(path, "root bundle metadata `bundle.kind` must be `root`"))
    else:
        if bundle.get("kind") != "nested":
            issues.append(Issue(path, "nested bundle metadata `bundle.kind` must be `nested`"))
        if not has_value(bundle.get("parent")):
            issues.append(Issue(path, "nested bundle metadata is missing non-empty `bundle.parent`"))


def validate_concept(path: Path, frontmatter: dict[str, Any] | None, had_frontmatter: bool, issues: list[Issue]) -> None:
    if not had_frontmatter or frontmatter is None:
        issues.append(Issue(path, "concept must start with YAML frontmatter"))
        return

    missing = sorted(key for key in CONCEPT_REQUIRED_FIELDS if key not in frontmatter)
    for key in missing:
        issues.append(Issue(path, f"concept is missing required `{key}`"))

    for key in ("type", "title", "description", "status", "owner", "updated"):
        if key in frontmatter and not has_value(frontmatter.get(key)):
            issues.append(Issue(path, f"concept has empty `{key}`"))

    sources = frontmatter.get("sources")
    if "sources" in frontmatter and not isinstance(sources, list):
        issues.append(Issue(path, "`sources` must be a list"))

    related = frontmatter.get("related")
    if "related" in frontmatter and not isinstance(related, list):
        issues.append(Issue(path, "`related` must be a list"))
    elif isinstance(related, list):
        for index, item in enumerate(related):
            if not isinstance(item, dict):
                issues.append(Issue(path, f"`related[{index}]` must be a mapping"))
                continue
            for key in sorted(RELATION_REQUIRED_FIELDS):
                if not has_value(item.get(key)):
                    issues.append(Issue(path, f"`related[{index}]` is missing non-empty `{key}`"))

    tags = frontmatter.get("tags")
    if tags is not None:
        if not isinstance(tags, list):
            issues.append(Issue(path, "`tags` must be a list"))
        else:
            for index, tag in enumerate(tags):
                if not isinstance(tag, str) or not TAG_RE.fullmatch(tag):
                    issues.append(Issue(path, f"`tags[{index}]` must be a lowercase kebab-case or snake_case string"))


def bundle_roots(root: Path) -> list[tuple[Path, bool]]:
    roots: list[tuple[Path, bool]] = []

    def walk(bundle_root: Path, is_root: bool) -> None:
        roots.append((bundle_root, is_root))
        nested_root = bundle_root / "bundles"
        if not nested_root.is_dir() or nested_root.is_symlink():
            return
        for child in sorted(nested_root.iterdir(), key=lambda path: path.name):
            if child.is_dir() and not child.is_symlink():
                walk(child, False)

    walk(root, True)
    return roots


def validate_knowledge_tree(bundle: Path, issues: list[Issue]) -> None:
    knowledge = bundle / "knowledge"
    if not knowledge.is_dir():
        issues.append(Issue(knowledge, "required knowledge directory is missing"))
        return

    for directory in sorted(path for path in knowledge.rglob("*") if path.is_dir()):
        if not (directory / "index.md").is_file():
            issues.append(Issue(directory, "knowledge subbundle directory is missing index.md"))

    for markdown in sorted(knowledge.rglob("*.md")):
        frontmatter, _body, had_frontmatter = validate_markdown_file(markdown, issues, require_h1=True)
        if markdown.name not in {"index.md", "log.md"}:
            validate_concept(markdown, frontmatter, had_frontmatter, issues)


def validate_bundle(root: Path) -> list[Issue]:
    issues: list[Issue] = []

    if not root.exists():
        return [Issue(root, "bundle path does not exist")]
    if not root.is_dir():
        return [Issue(root, "bundle path is not a directory")]

    seen_knowledge_files: set[Path] = set()

    for bundle, is_root in bundle_roots(root):
        index = bundle / "index.md"
        if not index.is_file():
            issues.append(Issue(index, "required bundle index is missing"))
        else:
            frontmatter, _body, had_frontmatter = validate_markdown_file(index, issues, require_h1=True)
            validate_bundle_index(index, frontmatter, had_frontmatter, is_root, issues)

        knowledge_index = bundle / "knowledge" / "index.md"
        if not knowledge_index.is_file():
            issues.append(Issue(knowledge_index, "required knowledge index is missing"))

        validate_knowledge_tree(bundle, issues)
        knowledge = bundle / "knowledge"
        if knowledge.is_dir():
            seen_knowledge_files.update(path.resolve() for path in knowledge.rglob("*.md"))

    for markdown in sorted(root.rglob("*.md")):
        if markdown.resolve() in seen_knowledge_files:
            continue
        validate_markdown_file(markdown, issues)

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an EKF bundle and print bad paths.")
    parser.add_argument("bundle", help="Path to the EKF bundle root")
    parser.add_argument("--paths-only", action="store_true", help="Print only unique bad paths")
    args = parser.parse_args()

    root = Path(args.bundle).expanduser().resolve()
    issues = validate_bundle(root)

    if not issues:
        print(f"OK: {root} is EKF authoring-conformant for checked rules.")
        return 0

    if args.paths_only:
        for path in sorted({relpath(issue.path, root) for issue in issues}):
            print(path)
    else:
        print(f"EKF validation failed: {len(issues)} issue(s)")
        for issue in issues:
            print(f"{relpath(issue.path, root)}: {issue.message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
