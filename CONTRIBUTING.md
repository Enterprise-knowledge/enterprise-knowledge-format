# Contributing To EKF

Thanks for helping improve Enterprise Knowledge Format.

EKF is a standard, not an application codebase. Contributions should preserve the core direction: progressive discovery, markdown as the canonical knowledge layer, typed graph relationships in frontmatter, source and artifact separation, nested bundles for ownership boundaries, and enterprise governance without vendor lock-in.

## Good First Contributions

- Clarify confusing wording in `SPEC.md`.
- Add small, enterprise-generic examples.
- Improve validator messages in `skills/ekf-bootstrap/scripts/validate_ekf.py`.
- Improve graph parsing or graph artifact generation.
- Open issues describing where EKF is unclear for a real knowledge-base trial.

## Specification Changes

When changing `SPEC.md`:

1. Use normative words deliberately: `must`, `should`, and `may`.
2. Keep required fields few enough that humans and agents can maintain them.
3. Prefer lowercase snake_case for machine-readable values.
4. Avoid vendor-specific assumptions.
5. Update examples and conformance rules together.
6. If the change affects bundle creation, update `skills/ekf-bootstrap/SKILL.md` and `skills/ekf-bootstrap/scripts/bootstrap_ekf.py`.

## Testing

Run the launch checks before opening a pull request:

```sh
UV_CACHE_DIR=/tmp/uv-cache PYTHONPYCACHEPREFIX=/tmp/ekf-pycache \
  uv run python -m py_compile \
  skills/ekf-bootstrap/scripts/bootstrap_ekf.py \
  skills/ekf-bootstrap/scripts/validate_ekf.py \
  skills/ekf-bootstrap/scripts/parse_ekf_graph.py

rm -rf /tmp/ekf-smoke
UV_CACHE_DIR=/tmp/uv-cache uv run python skills/ekf-bootstrap/scripts/bootstrap_ekf.py \
  /tmp/ekf-smoke \
  --title "EKF Smoke Test" \
  --owner "Enterprise Architecture" \
  --nested-bundle customer-platform

UV_CACHE_DIR=/tmp/uv-cache uv run --with pyyaml python \
  skills/ekf-bootstrap/scripts/validate_ekf.py /tmp/ekf-smoke

UV_CACHE_DIR=/tmp/uv-cache uv run --with pyyaml python \
  skills/ekf-bootstrap/scripts/parse_ekf_graph.py /tmp/ekf-smoke \
  --output /tmp/ekf-smoke/artifacts/graph/graph.json
```

Optional text checks:

```sh
rg -n "[B]igQuery|[G]oogle Cloud|[G]CP|[A]WS|[A]zure|[S]nowflake|[D]atabricks" SPEC.md AGENTS.md README.md skills/ekf-bootstrap
rg -n "[T]ODO|[T]BD|[F]IXME" SPEC.md AGENTS.md README.md skills/ekf-bootstrap
```

Vendor names should appear only when discussing what EKF should avoid or when a future section explicitly compares formats.

## Source Material

Do not contribute source material containing secrets, credentials, private tokens, customer data, or confidential internal documentation.

When adding non-markdown source examples, keep the original file under `source/` and generated markdown renderings under `artifacts/markdown/`. Curated concepts still belong under `knowledge/`.

## License

By contributing, you agree that your contribution will be licensed under the Apache License 2.0.
