# Launchpad Lightshow Dashboard (MVP)

A practical starter dashboard for Novation Launchpad X:

- 8x8 clickable grid editor
- color palette + brush size
- scene save/load (`.json`)
- clear + full-frame push to device
- backend selection:
  - `launchpad.py` (recommended if it works for your unit)
  - `mido` (raw MIDI fallback)
  - dry-run (no hardware, for UI iteration)

## Why this setup

You asked for the fastest path without weeks of MIDI plumbing. This gives you:

- immediate local UI for building patterns
- reusable scene format
- backend abstraction so you can swap transport later

## Quick start

```bash
cd /Users/luke/Work/launchpad-lightshow
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python app.py
```

The app will try `launchpad.py` first, then `mido`, then dry-run.

## Notes about Launchpad X

- In `mido` backend, this project uses Programmer mode-style note mapping:
  - `note = (8 - y) * 10 + (x + 1)` for `x,y` in `0..7`
- Velocity is used as a simple color index for fast iteration.
- Depending on firmware/config, you may need to adjust:
  - MIDI port name matching
  - note mapping
  - SysEx for explicit programmer mode enable

If the grid does not light correctly, use this order:

1. Confirm app is opening the expected MIDI port (shown in status line).
2. Switch to `mido` backend and test.
3. Tune `xy_to_note()` and/or add a Launchpad X programmer-mode SysEx init message.

## File format

Scenes are saved as:

```json
{
  "name": "My Scene",
  "rows": [
    [0, 0, 0, 0, 0, 0, 0, 0],
    ...
  ]
}
```

Each cell is a color index `0..127`.

## Next practical upgrades

- timeline/chase playback
- BPM sync + step duration
- MIDI clock in/out
- scene bank and key-triggered scene launch
- optional web UI (FastAPI + websocket) while keeping this Python device layer
