# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security-only |
| < 0.5   | no        |

## Threat model

`text-to-video-studio` runs **third-party plugin code in-process**. Treat
every plugin as untrusted-by-default at the boundary:

- Plugin loader sandboxes imports to the declared module path.
- Plugins may NOT open raw sockets; use `services.model_cache` for fetches.
- Subprocess export backends run with a scrubbed env and a wall-clock cap.

## Reporting a vulnerability

Email `security@text-to-video-studio.dev` (PGP in `docs/keys/`) or open a
private advisory. Do not file public issues for RCE, path traversal in the
asset resolver, or arbitrary-write in an exporter backend.

We aim to acknowledge within 72h and patch within 14 days for criticals.

## Out of scope

- Prompt-injection in generated output.
- NSFW classifier false negatives.
- Model quality / artifacts — that's a model bug, not a security bug.