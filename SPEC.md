# Enterprise Knowledge Format (EKF)

Version 0.1 - Draft

Enterprise Knowledge Format (EKF) is an opinionated enterprise implementation of the ideas behind Open Knowledge Format (OKF) and LLM wiki repositories. It keeps the durable core of OKF - markdown documents, YAML frontmatter, directory indexes, and permissive traversal - while adding the conventions an enterprise knowledge base needs to scale across many sources, teams, systems, APIs, repositories, and databases.

EKF is designed for knowledge bases maintained by people and agents together. A good EKF bundle should let an LLM quickly discover what exists, decide what to open next, trace claims back to source material, and traverse a typed knowledge graph without needing a proprietary catalog.

EKF is derived from OKF: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

---

## 1. Motivation

Enterprise knowledge bases fail when they become either too loose to trust or too rigid to maintain. EKF takes a middle path: authoring rules are opinionated, but consumption remains forgiving.

EKF assumes a large organization may have hundreds of source systems, including:

- API definitions such as OpenAPI, AsyncAPI, GraphQL schemas, and RPC contracts.
- Source code repositories cloned or mirrored into a source area.
- Database schemas, data models, migrations, lineage exports, and warehouse metadata.
- Operational runbooks, product documentation, decision records, policies, and glossaries.
- Generated representations such as HTML pages, diagrams, graph exports, and search indexes.

### Goals

1. Define an enterprise-friendly profile of OKF for large knowledge bases.
2. Make progressive discovery a required design principle, not an optional convenience.
3. Put a typed knowledge graph in YAML frontmatter so agents can traverse relationships cheaply.
4. Keep markdown as the canonical knowledge layer while preserving links to raw source material.
5. Support generated artifacts, especially HTML representations, without making them the source of truth.
6. Require enough ownership, lifecycle, and provenance metadata for enterprise use.
7. Stay portable across vendors, clouds, LLMs, storage systems, and indexing tools.

### Non-goals

- EKF does not replace domain-specific formats such as OpenAPI, Protobuf, Avro, SQL DDL, or source code. EKF references and explains them.
- EKF does not require a vector database, graph database, search engine, catalog product, or serving layer.
- EKF does not define a universal taxonomy for every enterprise. It defines a controlled core and extension rules.
- EKF does not make generated artifacts canonical unless a bundle explicitly says so.

---

## 2. Design Principles

### 2.1 Progressive discovery

Every navigational surface must help a human or LLM decide whether to go deeper. Bundle indexes, subbundle indexes, concept descriptions, relation descriptions, source manifests, and artifact listings must be short, specific, and useful.

### 2.2 Canonical markdown, typed metadata

The canonical knowledge unit is a markdown concept document with YAML frontmatter. The body explains the concept. The frontmatter makes it discoverable, governable, and graphable.

### 2.3 Graph-first relationships

Markdown links are useful for reading. The `related` frontmatter field is the preferred source for typed relationships. Consumers may build graph views from `related` without parsing prose.

### 2.4 Provenance over assertion

Enterprise knowledge needs traceability. Concepts should say where their knowledge came from, which source files support them, and whether they were reviewed.

### 2.5 Source and artifact separation

Raw or mirrored material belongs in `source/`. Generated views belong in `artifacts/`. Curated knowledge belongs in `knowledge/`. This separation prevents cloned repositories, generated HTML, and concept documentation from being confused with each other.

### 2.6 Strict writers, forgiving readers

EKF producers should follow the required schema. EKF consumers should tolerate unknown types, unknown fields, missing optional fields, and broken links when operating on partial or draft bundles.

---

## 3. Terminology

- **EKF bundle** - A directory tree that follows this specification. A repository may contain one root bundle and zero or more nested bundles.
- **Root bundle** - The top-level EKF bundle that coordinates enterprise-wide knowledge, shared conventions, and nested bundle discovery.
- **Nested bundle** - A full EKF bundle inside another EKF bundle, normally under `bundles/<bundle-id>/`, with its own `index.md`, `knowledge/`, ownership, sources, artifacts, and lifecycle.
- **Bundle ID** - A stable lowercase identifier for a nested bundle, normally matching its directory name under `bundles/`.
- **Knowledge tree** - The `knowledge/` directory inside an EKF bundle containing canonical concept documents and indexes for that bundle.
- **Concept** - A single markdown document that explains one enterprise knowledge unit.
- **Concept ID** - The repository-relative path of a concept without the `.md` suffix. For example, `knowledge/apis/customer-api.md` has concept ID `knowledge/apis/customer-api`, and `bundles/customer-platform/knowledge/apis/customer-api.md` has concept ID `bundles/customer-platform/knowledge/apis/customer-api`.
- **Index** - An `index.md` file that summarizes a bundle or subbundle for progressive discovery.
- **Subbundle** - A directory inside a bundle's `knowledge/` tree that has its own `index.md` and can be understood as a coherent scope. A subbundle is not a full EKF bundle unless it also declares the required bundle structure.
- **Source** - Raw, mirrored, extracted, or synchronized material stored under `source/`.
- **Source manifest** - A YAML file that describes a source area and how it should be indexed.
- **Artifact** - A generated representation stored under `artifacts/`, such as HTML, diagrams, graph exports, or rendered documents.
- **Relation** - A typed edge from one concept to another, usually declared in `related`.
- **Producer** - A person, agent, script, or system that writes EKF content.
- **Consumer** - A person, agent, script, or system that reads, indexes, validates, renders, or traverses EKF content.
- **Owner** - The team, person, or group accountable for the concept's correctness.

---

## 4. Bundle Structure

An EKF bundle should use this top-level layout:

```text
ekf-bundle/
|-- index.md
|-- log.md
|-- knowledge/
|   |-- index.md
|   |-- domains/
|   |-- systems/
|   |-- apis/
|   |-- data/
|   |-- code/
|   |-- processes/
|   `-- glossary/
|-- source/
|   |-- index.md
|   |-- apis/
|   |-- repositories/
|   |-- databases/
|   `-- documents/
|-- artifacts/
|   |-- index.md
|   |-- html/
|   |-- diagrams/
|   |-- graph/
|   `-- exports/
|-- bundles/
|   |-- customer-platform/
|   |   |-- index.md
|   |   |-- knowledge/
|   |   |-- source/
|   |   |-- artifacts/
|   |   `-- meta/
|   `-- billing-platform/
|       |-- index.md
|       |-- knowledge/
|       |-- source/
|       |-- artifacts/
|       `-- meta/
|-- schemas/
|   |-- types.yml
|   `-- relations.yml
`-- meta/
    |-- conventions.md
    |-- governance.md
    `-- ingestion.md
```

### 4.1 Required top-level paths

- `index.md` - Required. Describes the EKF bundle and points to major areas.
- `knowledge/` - Required. Contains canonical EKF concepts.
- `knowledge/index.md` - Required. Describes the top-level knowledge structure.

### 4.2 Recommended top-level paths

- `log.md` - Chronological bundle-level change log.
- `source/` - Source material for indexing, citation, and regeneration.
- `artifacts/` - Generated representations derived from concepts or sources.
- `bundles/` - Nested EKF bundles for independently owned enterprise scopes.
- `schemas/` - Machine-readable schemas and controlled vocabularies for this bundle.
- `meta/` - Bundle governance, conventions, ingestion notes, and maintenance documentation.

### 4.3 Root bundles, subbundles, and nested bundles

EKF distinguishes between three containment levels:

1. The **root bundle** is the enterprise coordination layer.
2. A **subbundle** is a folder inside a bundle's `knowledge/` tree.
3. A **nested bundle** is a full EKF bundle inside `bundles/<bundle-id>/`.

The root bundle should contain knowledge that is enterprise-wide, cross-domain, or structural:

- Shared concept types, relation vocabularies, and governance rules.
- Enterprise-wide glossary terms.
- Cross-domain architecture maps and integration concepts.
- Portfolio-level concepts such as domains, platforms, capabilities, and governance bodies.
- Indexes that describe and route readers to nested bundles.

The root bundle should not duplicate every API, table, repository, or operational detail from child bundles. It should point to canonical child concepts and explain cross-bundle relationships.

A concept belongs in a nested bundle when:

- One team, domain, platform, or system clearly owns it.
- Its source material belongs mostly to that scope.
- Its update lifecycle follows that scope.
- Most of its relations are inside that scope.
- The nested bundle could be exported, indexed, or reviewed on its own and still make sense.

Use this placement rule:

> Put knowledge in the lowest bundle that has clear ownership and enough context to maintain it. Put only shared, cross-bundle, or enterprise-coordinate knowledge in the root bundle.

### 4.4 Nested bundle structure

Nested bundles live under `bundles/<bundle-id>/` by default. Each nested bundle should follow the same structure as the root bundle:

```text
bundles/customer-platform/
|-- index.md
|-- log.md
|-- knowledge/
|   |-- index.md
|   |-- apis/
|   |-- data/
|   `-- operations/
|-- source/
|-- artifacts/
`-- meta/
```

The nested bundle's root `index.md` must declare bundle metadata in frontmatter:

```yaml
---
type: bundle
title: Customer Platform
description: Customer systems, APIs, data models, operations, and ownership.
ekf_version: "0.1"
bundle:
  id: customer-platform
  kind: nested
  parent: /
owner:
  name: Customer Platform Team
status: active
updated: 2026-06-19T00:00:00Z
---
```

The parent index must list each immediate nested bundle with a short description:

```markdown
## Nested Bundles

- [Customer Platform](bundles/customer-platform/) - Customer systems, APIs, profile data, and operations.
- [Billing Platform](bundles/billing-platform/) - Billing accounts, invoices, payments, and financial integrations.
```

Nested bundles may define local conventions in their own `meta/` directory, but they should not contradict the root bundle's schemas or governance rules unless the root explicitly allows that override.

### 4.5 Cross-bundle relationships

Concepts may relate to concepts in other bundles. Cross-bundle `related.path` values must use repository-absolute paths beginning at the repository root.

Example:

```yaml
related:
  - name: Customer API
    path: /bundles/customer-platform/knowledge/apis/customer-api.md
    relation: depends_on
    description: Billing onboarding uses Customer API to resolve account identity.
  - name: Billing Account Model
    path: /bundles/billing-platform/knowledge/data/billing-account.md
    relation: depends_on
    description: Customer identity is mapped into the billing account model.
```

A root concept may summarize a cross-bundle integration, dependency, or governance concern. The canonical details should remain in the child bundles that own them.

### 4.6 Concept parsing scope

By default, only markdown files under a bundle's `knowledge/` tree are concept documents. Markdown files under `source/`, `artifacts/`, `schemas/`, and `meta/` are not concepts unless a bundle explicitly declares otherwise.

This rule allows source repositories and generated artifacts to contain their own markdown without accidentally becoming EKF concepts.

In a repository with nested bundles, consumers should parse:

- Root concepts under `/knowledge/`.
- Nested bundle concepts under `/bundles/<bundle-id>/knowledge/`.

### 4.7 Reserved filenames

The following filenames have defined meaning at any level of a bundle's `knowledge/` tree:

| Filename | Purpose |
| --- | --- |
| `index.md` | Progressive discovery index for the current directory or subbundle. |
| `log.md` | Update history for the current bundle, directory, or subbundle. |

All other `.md` files under a bundle's `knowledge/` tree are concept documents.

---

## 5. Index Files

Indexes are required for progressive discovery.

Every EKF bundle, root or nested, must have:

- A bundle-root `index.md`.
- A `knowledge/index.md`.
- An `index.md` in every subbundle directory.

Every index must provide:

- A short title.
- A short description of the scope.
- Links to immediate child subbundles, each with a short description.
- Links to immediate nested bundles, each with a short description, when the index is responsible for nested bundle discovery.
- Links to important concepts in that scope, each with a short description.

Index files may include YAML frontmatter. Index frontmatter is an EKF extension intended to make bundles and subbundles self-describing.

Index files are not concept documents. Their `type` value may be `index` for ordinary indexes or `bundle` for root and nested bundle indexes.

```yaml
---
type: index
title: Customer Platform
description: Map of customer systems, APIs, data models, operations, and ownership.
owner:
  name: Customer Platform Team
status: active
updated: 2026-06-19T00:00:00Z
---
```

The body should remain optimized for scanning:

```markdown
# Customer Platform

The customer platform subbundle covers customer identity, profile data, lifecycle events, and customer-facing APIs.

## Subbundles

- [APIs](apis/) - Customer API contracts, endpoints, and integration behavior.
- [Data](data/) - Customer tables, schemas, lineage, and data quality expectations.
- [Operations](operations/) - Runbooks, SLAs, incidents, and support procedures.

## Core Concepts

- [Customer API](apis/customer-api.md) - Public API used to create, update, and retrieve customer records.
- [Customer Profile](data/customer-profile.md) - Canonical data model for a customer profile.
```

Parent indexes must describe child subbundles and immediate nested bundles. A directory should not require opening child files just to learn what the child scope contains.

---

## 6. Concept Documents

Every concept is a UTF-8 markdown file under `knowledge/`. It has:

1. A YAML frontmatter block at the top of the file.
2. A markdown body after the frontmatter.

### 6.1 Required frontmatter

```yaml
---
type: api
title: Customer API
description: API for creating, updating, and retrieving customer records.
status: active
owner:
  name: Customer Platform Team
  contact: slack:#customer-platform
updated: 2026-06-19T00:00:00Z
sources:
  - name: customer-openapi
    path: /source/apis/customer/openapi.yaml
    kind: openapi
    description: Canonical OpenAPI contract for the Customer API.
related:
  - name: Customer Profile
    path: /knowledge/data/customer-profile.md
    relation: reads_from
    description: Customer API reads and returns fields from the customer profile model.
---
```

The following fields are required for concept documents:

| Field | Purpose |
| --- | --- |
| `type` | Short machine-friendly kind of concept. |
| `title` | Human-readable display name. |
| `description` | One-sentence summary used for progressive discovery. |
| `status` | Lifecycle state of the concept. |
| `owner` | Accountable person, team, or group. |
| `updated` | ISO 8601 timestamp of the last meaningful update. |
| `sources` | List of source references that support or generated the concept. May be empty only for early drafts or abstract concepts. |
| `related` | List of typed graph relations. May be empty only when no relationship is known yet. |

### 6.2 Recommended frontmatter

```yaml
domain: customer
system: customer-platform
tags: [customer, api, profile, onboarding, pii]
confidence: high
review:
  status: reviewed
  reviewed_by: Customer Architecture Board
  reviewed_at: 2026-06-19T00:00:00Z
artifacts:
  - name: Customer API HTML view
    path: /artifacts/html/apis/customer-api/index.html
    kind: html
    description: Browseable HTML rendering of the Customer API concept and endpoint graph.
```

Recommended fields:

| Field | Purpose |
| --- | --- |
| `domain` | Business or technical domain. |
| `system` | Owning or primary system. |
| `tags` | Cross-cutting labels for search, browsing, and text-tool discovery. |
| `confidence` | Producer confidence: `low`, `medium`, or `high`. |
| `review` | Human or process review state. |
| `artifacts` | Generated outputs derived from this concept. |
| `classification` | Data sensitivity or handling classification when relevant. |
| `aliases` | Alternative names used in source systems or teams. |
| `deprecated_by` | Replacement concept when `status` is `deprecated`. |

### 6.3 Tags

Tags are lightweight discovery labels. They help humans, LLMs, and simple text tools find concepts across bundle boundaries without needing a graph database, vector index, or catalog service.

Tags should complement structured fields:

- Use `type` for the kind of concept.
- Use `domain` for the business or technical domain.
- Use `system` for the owning or primary system.
- Use `related` for typed graph relationships.
- Use `tags` for cross-cutting concerns, capabilities, workflows, risks, technologies, or search terms.

Tag values should be:

- Lowercase.
- Stable over time.
- Short enough to scan.
- Specific enough to be useful.
- Written consistently within a bundle.

Recommended tag styles are `kebab-case` or `snake_case`. A bundle should choose one style and document it in `meta/conventions.md`.

Examples:

```yaml
tags: [customer, api, onboarding, pii, internal]
```

```yaml
tags: [billing, invoice, revenue_reporting, finance_control]
```

Tags should not become a substitute for the knowledge graph. If a relationship can be stated as a typed edge, use `related`. If a label is mainly useful for search, filtering, or discovery, use `tags`.

### 6.4 Status values

Recommended `status` values are:

- `draft` - Useful but incomplete or not yet reviewed.
- `active` - Current and intended for normal use.
- `deprecated` - Still available but should no longer be used as primary guidance.
- `archived` - Preserved for history.

Bundles may add status values, but consumers must tolerate unknown values.

### 6.5 Type values

`type` describes the kind of concept being documented. EKF recommends lowercase snake_case values because they are easy to filter and validate.

Recommended concept types include:

- `domain`
- `system`
- `service`
- `api`
- `api_endpoint`
- `database`
- `schema`
- `table`
- `column`
- `event`
- `message_topic`
- `codebase`
- `module`
- `class`
- `function`
- `metric`
- `report`
- `business_process`
- `playbook`
- `decision`
- `policy`
- `glossary_term`
- `source`
- `artifact`

The type list is not closed. Enterprise bundles may define additional types in `schemas/types.yml`.

### 6.6 Body conventions

The markdown body should begin with useful substance, not boilerplate. The first paragraph should let a reader decide whether to continue.

Recommended headings:

| Heading | Purpose |
| --- | --- |
| `# Summary` | Compact explanation of the concept. |
| `# Scope` | What is included and excluded. |
| `# Interface` | API, contract, method, endpoint, or integration details. |
| `# Schema` | Fields, columns, entities, or data model. |
| `# Behavior` | Rules, workflows, invariants, or edge cases. |
| `# Operations` | SLAs, ownership, runbooks, alerts, and support notes. |
| `# Examples` | Concrete examples, snippets, requests, queries, or workflows. |
| `# Source Notes` | How source material was interpreted. |
| `# Open Questions` | Known gaps or unresolved ambiguities. |
| `# Citations` | Specific evidence for claims in the body. |

Concept bodies should prefer structured markdown: headings, tables, lists, and fenced code blocks.

---

## 7. Text Discoverability and Standard Tools

EKF bundles should remain useful with standard text tools. A person or agent should be able to discover useful concepts with `ripgrep`, `grep`, `find`, and a markdown reader before any specialized index exists.

`ripgrep` (`rg`) is the preferred search tool when available because it is fast, recursive by default, respects common ignore files, and works well on large repositories. `grep -R` is the recommended fallback.

### 7.1 Searchable conventions

Producers should keep these strings stable and predictable because they form a simple discovery interface:

- Frontmatter keys: `type`, `title`, `description`, `domain`, `system`, `tags`, `status`, `owner`, `sources`, `related`, `relation`, and `path`.
- Standard headings: `# Summary`, `# Scope`, `# Interface`, `# Schema`, `# Behavior`, `# Operations`, `# Examples`, `# Source Notes`, `# Open Questions`, and `# Citations`.
- Reserved paths: `knowledge/`, `bundles/`, `source/`, `artifacts/`, `schemas/`, and `meta/`.

Concept descriptions, relation descriptions, source descriptions, artifact descriptions, and index descriptions should be written for text search as well as reading. Prefer explicit nouns over vague phrasing.

### 7.2 Recommended ripgrep patterns

Examples:

```sh
rg '^type: api$' knowledge/ bundles/
rg '^type: table$' knowledge/ bundles/
rg '^domain: customer$' knowledge/ bundles/
rg '^system: customer-platform$' knowledge/ bundles/
rg 'tags:.*customer' knowledge/ bundles/
rg 'tags:.*pii' knowledge/ bundles/
rg 'relation: depends_on' knowledge/ bundles/
rg 'relation: writes_to' knowledge/ bundles/
rg 'path: /bundles/customer-platform/' knowledge/ bundles/
rg '# Summary|# Interface|# Citations' knowledge/ bundles/
```

Search only the canonical concept trees when looking for concepts:

```sh
rg '^type:' knowledge/ bundles/*/knowledge/
```

Search source material separately when looking for raw evidence:

```sh
rg 'customer_id' source/ bundles/*/source/
```

Search artifacts separately when looking for generated representations:

```sh
rg 'dependency map' artifacts/ bundles/*/artifacts/
```

### 7.3 Grep fallback

When `rg` is unavailable, use `grep -R`:

```sh
grep -R --line-number '^type: api$' knowledge/ bundles/
grep -R --line-number 'tags:.*customer' knowledge/ bundles/
grep -R --line-number 'relation: depends_on' knowledge/ bundles/
```

### 7.4 Tooling rules

- Tools should prefer `rg` when available and fall back to `grep -R`.
- Tools should search `knowledge/` and `bundles/*/knowledge/` for canonical concepts.
- Tools should not search `source/` and `artifacts/` as concepts unless explicitly configured to do so.
- Tools should treat frontmatter as the primary structured search surface and markdown headings as the primary body search surface.
- Tools should not require a generated index before basic discovery works.

---

## 8. Knowledge Graph

EKF concepts declare graph edges in the `related` frontmatter field.

### 8.1 Relation object

Each relation object must include:

```yaml
related:
  - name: Customer Database
    path: /knowledge/data/customer-database.md
    relation: depends_on
    description: Customer API persists profile data in the customer database.
```

Required relation fields:

| Field | Purpose |
| --- | --- |
| `name` | Human-readable target name. |
| `path` | Repository-absolute path to the target concept when known. |
| `relation` | Typed edge from the current concept to the target. |
| `description` | Short explanation of why the relation exists. |

Optional relation fields:

| Field | Purpose |
| --- | --- |
| `confidence` | Confidence in the relationship. |
| `source` | Source path or citation supporting the relationship. |
| `external_uri` | External target when no EKF concept exists yet. |
| `status` | Relation state, such as `inferred`, `reviewed`, or `deprecated`. |

### 8.2 Relation direction

Relation direction is from the current concept to the related target.

For example, if `Customer API` has:

```yaml
relation: depends_on
path: /knowledge/data/customer-database.md
```

then the assertion is: `Customer API` depends on `Customer Database`.

Relations do not need to be duplicated in the reverse direction, but producers may generate inverse relations when that improves traversal.

### 8.3 Recommended relation types

Recommended relation types include:

- `related_to`
- `contains`
- `part_of`
- `depends_on`
- `supports`
- `implements`
- `implemented_by`
- `calls`
- `called_by`
- `reads_from`
- `writes_to`
- `publishes`
- `subscribes_to`
- `defines`
- `derived_from`
- `supersedes`
- `replaces`
- `owned_by`
- `governed_by`

The relation list is not closed. Enterprise bundles may define additional relation types in `schemas/relations.yml`.

### 8.4 Markdown links

Markdown links remain useful for human reading and local navigation. Consumers may treat markdown links as weak, untyped graph edges. The `related` field is preferred for typed graph construction.

---

## 9. Sources

The `source/` directory stores material that agents and scripts index, summarize, cite, or use to regenerate concepts.

Common source areas:

```text
source/
|-- apis/
|   `-- customer/
|       |-- ekf-source.yml
|       `-- openapi.yaml
|-- repositories/
|   `-- customer-service/
|       |-- ekf-source.yml
|       `-- repo/
|-- databases/
|   `-- customer-db/
|       |-- ekf-source.yml
|       |-- schema.sql
|       `-- introspection.json
`-- documents/
    `-- support-playbooks/
        |-- ekf-source.yml
        `-- raw/
```

### 9.1 Source manifest

Each source area should include an `ekf-source.yml` manifest.

```yaml
id: customer-openapi
name: Customer OpenAPI
kind: openapi
description: Canonical API contract for customer profile operations.
owner:
  name: Customer Platform Team
location: /source/apis/customer/openapi.yaml
upstream:
  uri: git@example.com:customer/customer-api.git
  ref: main
sync:
  mode: manual
  last_synced: 2026-06-19T00:00:00Z
indexing:
  include:
    - openapi.yaml
  exclude: []
trust:
  level: authoritative
```

Recommended `kind` values include:

- `openapi`
- `asyncapi`
- `graphql`
- `protobuf`
- `repository`
- `database_schema`
- `sql`
- `document`
- `wiki_export`
- `ticket_export`
- `dashboard_export`
- `manual`

### 9.2 Source rules

- Source material should be treated as input, not curated knowledge.
- Source material may contain any file type, including markdown.
- Consumers should not parse source markdown as EKF concepts by default.
- Secrets and credentials must not be committed to `source/`.
- Source manifests should document redaction, sync, and trust level when relevant.

---

## 10. Artifacts

The `artifacts/` directory stores generated representations derived from concepts, sources, or both.

Examples:

- HTML renderings of concepts, subbundles, and nested bundles.
- Interactive dependency maps.
- Graph exports such as JSON, GraphML, or RDF.
- Generated diagrams.
- Search indexes.
- PDF or document exports.

Artifacts are valuable because HTML and other rich formats can become excellent knowledge interfaces for both humans and agents. EKF therefore gives artifacts a first-class place without making them canonical.

### 10.1 Artifact listing

Artifacts should be listed from the concept or index that they represent:

```yaml
artifacts:
  - name: Customer dependency map
    path: /artifacts/html/customer/dependency-map/index.html
    kind: html
    description: Interactive map of customer systems, APIs, databases, and dependencies.
    generated_from:
      - /knowledge/apis/customer-api.md
      - /knowledge/data/customer-database.md
    generated_at: 2026-06-19T00:00:00Z
```

### 10.2 Artifact rules

- Artifacts should be reproducible when possible.
- Artifacts should include enough metadata to trace what generated them.
- Artifacts should not silently override canonical markdown concepts.
- Manually edited artifacts should say so in their metadata or nearby documentation.

---

## 11. Citations and Provenance

The `sources` frontmatter field describes concept-level provenance. Citations in the body support specific claims.

Use both when needed:

- Use `sources` to say which files, systems, exports, or repositories informed the concept.
- Use `# Citations` to support specific facts, constraints, or decisions.

Example:

```markdown
# Citations

[1] [Customer OpenAPI](/source/apis/customer/openapi.yaml)
[2] [Customer Service repository](/source/repositories/customer-service/repo/)
```

Claims that affect architecture, compliance, customer behavior, financial reporting, operational response, or security should cite source material whenever possible.

---

## 12. Logs

A `log.md` file may appear at the root, inside any subbundle, or inside any nested bundle.

Logs should use newest-first date sections:

```markdown
# Customer Platform Log

## 2026-06-19

- Added Customer API concept from the OpenAPI source.
- Linked Customer API to Customer Profile and Customer Database.
```

Date headings must use `YYYY-MM-DD`.

---

## 13. Conformance

EKF separates authoring conformance from consumption conformance.

### 13.1 Authoring conformance

An EKF v0.1 bundle is authoring-conformant when:

1. It has a bundle-root `index.md`.
2. The root `index.md` declares `ekf_version`.
3. It has a `knowledge/index.md`.
4. If it has a `bundles/` directory, every immediate child directory under `bundles/` is a nested bundle with `index.md`, `knowledge/index.md`, and `bundle.id` metadata.
5. Every parent index that owns immediate nested bundle discovery lists those nested bundles with short descriptions.
6. Every subbundle under each bundle's `knowledge/` tree has an `index.md`.
7. Every concept under each bundle's `knowledge/` tree has parseable YAML frontmatter.
8. Every concept has required frontmatter fields: `type`, `title`, `description`, `status`, `owner`, `updated`, `sources`, and `related`.
9. `type`, `title`, `description`, `status`, `owner`, and `updated` are non-empty.
10. `sources` and `related` are lists. They should be non-empty unless the concept is an early draft, abstract concept, or isolated seed concept.
11. If `tags` is present, it is a list of stable lowercase strings.
12. Every `related` entry has `name`, `path`, `relation`, and `description`.
13. Every index entry for a concept, subbundle, or nested bundle includes a short description.
14. Source areas under any bundle's `source/` directory include an `ekf-source.yml` manifest when they are intended to be indexed.

### 13.2 Consumption conformance

An EKF consumer should:

1. Parse concept frontmatter under root `knowledge/` and nested bundle `bundles/<bundle-id>/knowledge/` trees.
2. Preserve unknown frontmatter fields when round-tripping.
3. Tolerate unknown `type`, `status`, and `relation` values.
4. Tolerate missing optional fields.
5. Tolerate broken concept links in draft or partially generated bundles.
6. Resolve leading-slash EKF paths from the repository root.
7. Avoid treating `source/` or `artifacts/` markdown files as concepts unless explicitly configured.
8. Support basic concept discovery from plain text frontmatter and headings without requiring generated indexes.

This permissive consumption model allows EKF bundles to grow incrementally.

---

## 14. Versioning

EKF versions use `major.minor`.

- A minor version adds backward-compatible fields, recommendations, examples, or conventions.
- A major version may change required fields, reserved paths, or conformance rules.

The root `index.md` should declare the EKF version:

```yaml
---
type: bundle
title: Example Enterprise Knowledge Base
description: Root index for an EKF bundle.
ekf_version: "0.1"
bundle:
  id: enterprise
  kind: root
status: active
owner:
  name: Enterprise Architecture
updated: 2026-06-19T00:00:00Z
---
```

Consumers that do not understand a declared version should attempt best-effort reading rather than refusing the bundle.

---

## Appendix A. Minimal Example

```text
example-ekf/
|-- index.md
|-- knowledge/
|   |-- index.md
|   |-- apis/
|   |   |-- index.md
|   |   `-- customer-api.md
|   `-- data/
|       |-- index.md
|       `-- customer-profile.md
|-- source/
|   `-- apis/
|       `-- customer/
|           |-- ekf-source.yml
|           `-- openapi.yaml
`-- artifacts/
    `-- html/
        `-- apis/
            `-- customer-api/
                `-- index.html
```

`knowledge/apis/customer-api.md`:

```markdown
---
type: api
title: Customer API
description: API for creating, updating, and retrieving customer records.
status: active
owner:
  name: Customer Platform Team
  contact: slack:#customer-platform
updated: 2026-06-19T00:00:00Z
domain: customer
system: customer-platform
tags: [customer, api]
confidence: high
sources:
  - name: customer-openapi
    path: /source/apis/customer/openapi.yaml
    kind: openapi
    description: Canonical OpenAPI contract for customer operations.
related:
  - name: Customer Profile
    path: /knowledge/data/customer-profile.md
    relation: reads_from
    description: Customer API returns data shaped by the customer profile model.
artifacts:
  - name: Customer API HTML view
    path: /artifacts/html/apis/customer-api/index.html
    kind: html
    description: Browseable HTML rendering of the Customer API concept.
---

# Summary

Customer API exposes customer profile operations to internal applications.

# Interface

The canonical contract is stored in `/source/apis/customer/openapi.yaml`.

# Citations

[1] [Customer OpenAPI](/source/apis/customer/openapi.yaml)
```

`source/apis/customer/ekf-source.yml`:

```yaml
id: customer-openapi
name: Customer OpenAPI
kind: openapi
description: Canonical OpenAPI contract for customer profile operations.
owner:
  name: Customer Platform Team
location: /source/apis/customer/openapi.yaml
sync:
  mode: manual
  last_synced: 2026-06-19T00:00:00Z
trust:
  level: authoritative
```
