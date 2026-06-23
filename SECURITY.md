# Security Policy

EKF is a plain-text knowledge format and bootstrap toolchain. Please report security issues that could affect users of the tooling or expose sensitive source material.

## Reporting

Open a private security advisory on GitHub if available, or contact the maintainers through the repository owner.

Please include:

- the affected file or workflow,
- steps to reproduce,
- expected impact,
- any suggested mitigation.

Do not open public issues for vulnerabilities or accidental secret exposure.

## Sensitive Material

Do not contribute credentials, private keys, access tokens, customer data, confidential internal documents, or proprietary source material. EKF examples should use public or synthetic source material only.

## Scope

In scope:

- validator or parser behavior that can corrupt data or hide invalid content,
- generated artifacts that execute unsafe code unexpectedly,
- documentation paths that encourage unsafe handling of secrets or private data.

Out of scope:

- vulnerabilities in third-party tools used only during local experimentation,
- issues requiring access to private repositories or unpublished source material.
