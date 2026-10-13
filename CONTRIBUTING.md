# Contributing to text-to-video-studio

Thanks for wanting to plug into the host. This repo is a **plugin host** for
text-to-video generation: the core ships a stable host + registry + contracts,
and everything model-specific (backends, motion schedulers, upscalers,
captioners, exporters) lives as an extension module under `plugins/`.

## Repo layout

```
text-to-video_studio/     core host package (registry, loader, contracts)
plugins/                  drop-in extension modules
services/                 long-lived services (queue, model cache)
models/                   dataclasses + typed schemas for shots/prompts
handlers/                 CLI + IPC entry handlers
utils/                    small shared helpers
config/                   default TOML config + plugin manifest
tests/                    pytest suite
```

## Adding a plugin

1. Create `plugins/<your_plugin>/` with `__init__.py` and `plugin.py`.
2. Subclass the right contract from `text-to-video_studio.contracts`.
3. Register via the `@register_plugin` decorator or declare entry points
   in `config/plugins.toml`.
4. `pytest -q` must stay green. Loader validates contract conformance at
   boot — a malformed plugin is quarantined, not fatal.

## Style

- Python 3.11+, `ruff` + `black`, line length 100.
- Types on public surfaces. `from __future__ import annotations` everywhere.
- New backend? Ship a fixture prompt + expected frame-count smoke test.

## PR checklist

- [ ] Runs `pytest -q` clean
- [ ] `ruff check .` clean
- [ ] Plugin has a `plugin.toml` manifest with `contract`, `version`, `entry`
- [ ] No weights committed — use the model cache service