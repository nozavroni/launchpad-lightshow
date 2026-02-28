# AGENTS.md

This file provides guidance to Codex agents when working with code in this repository.

## Intent

This is a quick utility project for a family use case.
Optimize for speed, usefulness, and iteration over formal architecture.

## Project Scope

Launchpad Lightshow Dashboard for Novation Launchpad X.
Current baseline: Python app with Tkinter editor, JSON scenes, and MIDI backends.

## Prototype-First Rules

- Prefer the fastest working solution.
- Keep diffs small and shippable.
- Avoid big refactors unless they unblock current work.
- Reuse existing code paths before introducing abstractions.
- If a feature works and is readable, do not over-polish it.

## Tech Stack

- Python 3.10+
- Tkinter
- `launchpad-py`, `mido`, `python-rtmidi`

## Run

```bash
cd /Users/luke/Work/launchpad-lightshow
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python app.py
```

## Validation (Lightweight)

Minimum for code changes:

```bash
python3 -m py_compile app.py
```

If hardware behavior cannot be tested locally, state that briefly and provide exact manual steps.

## Launchpad-Specific Guidance

- Keep pad mapping centralized (`xy_to_note`) so tweaks are quick.
- Keep backend fallback order simple (`launchpad.py` -> `mido` -> `dry-run`).
- Preserve dry-run mode for development without device access.

## Code Style

- Prioritize clarity over cleverness.
- Add types where they help maintainability, not everywhere by default.
- Add comments only when behavior is non-obvious.
- Avoid extra dependencies unless they significantly speed delivery.
- Do not use emdashes.

## Git

- Keep commits focused.
- Preferred commit prefixes: `feat:`, `fix:`, `chore:`, `docs:`.
- Do not force-push or rewrite history unless explicitly requested.

## Preferred Next Features

1. BPM-based step playback.
2. Scene bank hotkeys.
3. Optional Launchpad X programmer-mode init handling.
