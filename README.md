# Enterprise Knowledge Format

Enterprise Knowledge Format (EKF) is a plain-text standard for organizing company knowledge so humans and agents can discover it, trust it, and keep it current.

EKF treats the enterprise knowledge base as a repository, not a product silo. Canonical knowledge lives in markdown. YAML frontmatter carries ownership, status, provenance, tags, and typed graph relationships. Raw source material and generated artifacts stay close to the knowledge they support, but they do not replace it.

The goal is simple: make enterprise knowledge scalable without making basic discovery depend on a search appliance, graph database, vector database, or vendor-specific catalog.

## Core Idea

EKF separates the knowledge system into three layers:

- `knowledge/` - Curated markdown concepts with governance metadata and typed relationships.
- `source/` - Raw, mirrored, extracted, or synchronized material that supports those concepts.
- `artifacts/` - Generated HTML, diagrams, graph exports, indexes, and other renderings.

Every index, concept, source, artifact, and relation should include a short description. That progressive discovery layer lets an LLM or a human decide what to open next without loading the whole repository.

## Relation To OKF And LLM Wikis

EKF builds on the ideas behind Open Knowledge Format (OKF): markdown documents, YAML frontmatter, directory indexes, and permissive traversal. It keeps that durable base and adds enterprise conventions for ownership, lifecycle, provenance, nested bundles, source separation, generated artifacts, and typed graph edges.

It also follows the spirit of LLM wiki repositories: a knowledge base should be legible to agents using ordinary file reads, links, `rg`, and stable metadata. EKF makes that wiki pattern governable enough for large organizations, where many teams own different systems, APIs, repositories, policies, and data models.

## Why EKF

- Progressive discovery first, so agents can navigate before they ingest.
- Markdown as the canonical knowledge layer, so the base remains portable and reviewable.
- Typed graph relationships in frontmatter, so graph traversal does not require prose parsing.
- Clear separation between curated knowledge, raw source, and generated artifacts.
- Nested bundles for team, platform, system, and domain ownership boundaries.
- Enterprise governance without locking the format to a specific cloud, catalog, model, or database.

## Get Started

Read the standard:

- [SPEC.md](SPEC.md) - The EKF specification.
- [AGENTS.md](AGENTS.md) - Maintenance guidance for future agents.
- [skills/ekf-bootstrap](skills/ekf-bootstrap/SKILL.md) - Installable bootstrap skill for creating and growing EKF repositories.

Install the bootstrap skill with `npx skills`:

```sh
npx skills add Enterprise-knowledge/enterprise-knowledge-format --skill ekf-bootstrap
```

For a global Codex install:

```sh
npx skills add Enterprise-knowledge/enterprise-knowledge-format --skill ekf-bootstrap -g -a codex
```

Or ask your coding agent:

```text
Install the `ekf-bootstrap` skill from `Enterprise-knowledge/enterprise-knowledge-format` with `npx skills`, then use it to create an Enterprise Knowledge Format repository.
```

The installed skill includes its own copy of the EKF specification in `references/SPEC.md`, so it can scaffold and expand EKF repositories without depending on this repository being checked out locally.

## Bootstrap Prompts

After installing the skill, try one of these prompts:

```text
Use $ekf-bootstrap to create a new EKF repository in `./enterprise-knowledge` titled "Acme Enterprise Knowledge Base", owned by "Enterprise Architecture". Create nested bundles for `customer-platform`, `billing-platform`, and `data-platform`.
```

```text
Use $ekf-bootstrap to inspect the source material I added under `source/` and `bundles/*/source/`. Add or update `ekf-source.yml` manifests, then draft initial EKF concepts under `knowledge/` with descriptions, provenance in `sources`, and typed relationships in `related`.
```

```text
Use $ekf-bootstrap to grow the `customer-platform` nested bundle from the source I added. Keep raw files in `source/`, generated diagrams or HTML in `artifacts/`, and canonical explanations in `knowledge/`.
```

## Status

Draft v0.1.
