# Clip for WhatsApp (system audio)

**Practic-AI** micro-tool: record what Windows is **playing** (browser, games, apps) and save a clip you can attach in WhatsApp.

| | |
|---|---|
| **Platform** | Windows 10 / 11 |
| **Capture** | WASAPI loopback (system playback) — **not** the microphone |
| **Outputs** | Lean WAV (mono 22 kHz), HD WAV (stereo @ device rate), optional **M4A** for WhatsApp |
| **Public repo** | Source only — **no** sample recordings, **no** prebuilt `.exe` |

---

## Quick start

```text
1. Double-click INSTALL_ONCE.bat
2. Double-click RECORD.bat
3. Press RECORD (or RECORD HD) → play the audio → STOP
4. Click "M4A for WhatsApp" (WAV is often rejected by WhatsApp)
5. Attach the .m4a
```

Hotkey: **Ctrl+Alt+R** toggles **lean** recording (works while the app is open, even in another window).

Clips are saved next to the app in `clips\` (created on first run). That folder is gitignored for audio files.

---

## Modes

| Button | What you get |
|--------|----------------|
| **RECORD** | Mono ~22 kHz WAV — small, good base for WhatsApp after M4A convert |
| **RECORD HD** | Stereo at device sample rate — larger, higher fidelity |
| **Convert WAV → M4A…** | Pick an existing WAV and export AAC/M4A |

---

## Dependencies

See `requirements.txt`:

- `pyaudiowpatch` — WASAPI loopback
- `pynput` — global hotkey
- `imageio-ffmpeg` — M4A export (no separate ffmpeg install required)

---

## Optional: build a portable EXE

For friends without Python (local build only; binary not shipped in this repo):

```powershell
py -3 -m pip install pyinstaller
py -3 -m PyInstaller ClipForWhatsApp.spec
```

Output lands under `dist\` (gitignored).

---

## Privacy

- Does **not** record the microphone.
- Does **not** upload anything; everything stays on disk under `clips\`.
- Public package contains **no** user voice clips or media samples.

---

## License

MIT — see repository root `LICENSE`.
