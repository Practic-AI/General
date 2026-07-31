"""
WhatsApp system-audio clipper
-----------------------------
Records Windows playback (WASAPI loopback) → lean mono WAV
or HD stereo WAV (device sample rate) → optional M4A for WhatsApp
→ Copy path / Open folder / Play / M4A for WhatsApp.

Deps: pyaudiowpatch + pynput + imageio-ffmpeg (for AAC/M4A export).
"""

from __future__ import annotations

import audioop
import os
import shutil
import subprocess
import threading
import time
import wave
from datetime import datetime
from pathlib import Path
from tkinter import Tk, Frame, Label, Button, messagebox, font as tkfont, Toplevel, filedialog
from typing import Literal

APP_TITLE = "Clip for WhatsApp"
# Clips live next to the app (portable), not under Documents
APP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = APP_DIR / "clips"
# Previous default — one-time migrate copies files into OUTPUT_DIR
LEGACY_OUTPUT_DIR = Path.home() / "Documents" / "WhatsAppClips"
BLOCKSIZE = 1024
# Light enough for WhatsApp, fine for speech / short clips
TARGET_RATE = 22050
HOTKEY_LABEL = "Ctrl+Alt+R"
HOTKEY_COMBO = "<ctrl>+<alt>+r"
# AAC bitrates for M4A export (WhatsApp-friendly)
M4A_BITRATE_LEAN = "96k"
M4A_BITRATE_HD = "192k"

Quality = Literal["lean", "hd"]


def migrate_legacy_clips() -> int:
    """Copy clips from Documents\\WhatsAppClips → app clips folder. Returns count copied."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not LEGACY_OUTPUT_DIR.is_dir():
        return 0
    copied = 0
    for src in LEGACY_OUTPUT_DIR.iterdir():
        if not src.is_file():
            continue
        if src.suffix.lower() not in {".wav", ".m4a", ".mp3", ".aac"}:
            continue
        dest = OUTPUT_DIR / src.name
        if dest.exists():
            continue
        try:
            shutil.copy2(src, dest)
            copied += 1
        except OSError:
            pass
    return copied


def quality_from_wav(path: Path) -> Quality:
    """Guess lean vs HD from filename / WAV headers for bitrate choice."""
    name = path.name.lower()
    if name.startswith("clip_hd_") or "_hd_" in name or name.endswith("_hd.wav"):
        return "hd"
    try:
        with wave.open(str(path), "rb") as wf:
            if wf.getnchannels() >= 2 or wf.getframerate() >= 44100:
                return "hd"
    except Exception:
        pass
    return "lean"


def find_ffmpeg() -> str | None:
    """Prefer imageio-ffmpeg binary, then PATH / local ffmpeg.exe."""
    try:
        import imageio_ffmpeg

        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and Path(exe).is_file():
            return exe
    except Exception:
        pass

    which = shutil.which("ffmpeg")
    if which:
        return which

    # Next to app (dev or portable drop-in)
    here = Path(__file__).resolve().parent
    for candidate in (here / "ffmpeg.exe", here / "bin" / "ffmpeg.exe"):
        if candidate.is_file():
            return str(candidate)
    return None


def wav_to_m4a(wav_path: Path, quality: Quality = "lean") -> Path:
    """Convert WAV → M4A (AAC). Output beside the WAV with .m4a suffix."""
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError(
            "M4A export needs ffmpeg.\n"
            "Re-run INSTALL_ONCE.bat (installs imageio-ffmpeg),\n"
            "or put ffmpeg.exe next to the app."
        )

    out = wav_path.with_suffix(".m4a")
    bitrate = M4A_BITRATE_HD if quality == "hd" else M4A_BITRATE_LEAN
    cmd = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(wav_path),
        "-c:a",
        "aac",
        "-b:a",
        bitrate,
        "-movflags",
        "+faststart",
        str(out),
    ]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=300,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("M4A conversion timed out.") from exc
    except OSError as exc:
        raise RuntimeError(f"Could not run ffmpeg:\n{exc}") from exc

    if proc.returncode != 0 or not out.is_file():
        detail = (proc.stderr or proc.stdout or "").strip() or "unknown error"
        raise RuntimeError(f"M4A conversion failed:\n{detail}")

    return out


def find_loopback_device(p, pyaudio_mod) -> dict:
    wasapi_info = p.get_host_api_info_by_type(pyaudio_mod.paWASAPI)
    default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

    if default_speakers.get("isLoopbackDevice"):
        return default_speakers

    speaker_name = default_speakers.get("name") or ""
    for loopback in p.get_loopback_device_info_generator():
        if speaker_name and speaker_name in loopback.get("name", ""):
            return loopback

    for loopback in p.get_loopback_device_info_generator():
        return loopback

    raise RuntimeError(
        "No WASAPI loopback device found.\n"
        "Windows needs a working playback device (speakers/headphones)."
    )


class Recorder:
    def __init__(self) -> None:
        self._pa = None
        self._stream = None
        self._chunks: list[bytes] = []
        self._lock = threading.Lock()
        self.device_info: dict | None = None
        self.device_name: str = ""
        self.sample_rate: int = 48000
        self.channels: int = 2
        self.recording = False
        self.started_at: float | None = None
        self._pyaudio = None

    def prepare(self) -> str | None:
        try:
            import pyaudiowpatch as pyaudio

            self._pyaudio = pyaudio
            self._pa = pyaudio.PyAudio()
            info = find_loopback_device(self._pa, pyaudio)
            self.device_info = info
            self.device_name = info.get("name") or "Loopback"
            self.sample_rate = int(info.get("defaultSampleRate") or 48000)
            self.channels = max(1, int(info.get("maxInputChannels") or 2))
            return None
        except Exception as exc:
            return str(exc)

    def _callback(self, in_data, frame_count, time_info, status):  # noqa: ANN001
        if self.recording and in_data:
            with self._lock:
                self._chunks.append(in_data)
        return (None, self._pyaudio.paContinue)

    def start(self) -> None:
        if self.recording:
            return
        if self._pa is None or self.device_info is None:
            err = self.prepare()
            if err:
                raise RuntimeError(err)

        with self._lock:
            self._chunks = []

        assert self._pa is not None and self.device_info is not None and self._pyaudio is not None
        self._stream = self._pa.open(
            format=self._pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            frames_per_buffer=BLOCKSIZE,
            input=True,
            input_device_index=self.device_info["index"],
            stream_callback=self._callback,
        )
        self._stream.start_stream()
        self.recording = True
        self.started_at = time.monotonic()

    def stop(self) -> tuple[bytes, int, int]:
        """Return (pcm_int16_bytes, sample_rate, channels)."""
        self.recording = False
        if self._stream is not None:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        with self._lock:
            raw = b"".join(self._chunks)
            self._chunks = []

        return raw, self.sample_rate, self.channels

    def elapsed(self) -> float:
        if self.started_at is None:
            return 0.0
        return time.monotonic() - self.started_at

    def close(self) -> None:
        try:
            if self.recording:
                self.stop()
        except Exception:
            pass
        if self._pa is not None:
            try:
                self._pa.terminate()
            except Exception:
                pass
            self._pa = None


def _normalize_pcm(pcm: bytes, width: int = 2) -> bytes:
    peak = audioop.max(pcm, width)
    if peak < 8:
        raise RuntimeError(
            "Recording was basically silent.\nPlay something while recording."
        )

    # Normalize toward ~90% full scale, but don't blast quiet room noise too hard
    target = 29490  # ~0.9 * 32767
    gain = min(target / peak, 6.0)
    if abs(gain - 1.0) > 0.05:
        pcm = audioop.mul(pcm, width, gain)
    return pcm


def process_pcm(raw: bytes, sample_rate: int, channels: int) -> tuple[bytes, int, int]:
    """
    Mono + downsample + light peak normalize → compact PCM for WhatsApp.
    Uses stdlib audioop only (no numpy).
    Returns (pcm, sample_rate, channels).
    """
    if not raw:
        raise RuntimeError(
            "No audio captured.\nPlay something (YouTube etc.) while recording."
        )

    width = 2  # int16
    pcm = raw

    if channels >= 2:
        # Average L/R → mono
        pcm = audioop.tomono(pcm, width, 0.5, 0.5)
        channels = 1
    else:
        channels = 1

    if sample_rate != TARGET_RATE:
        pcm, _ = audioop.ratecv(pcm, width, 1, sample_rate, TARGET_RATE, None)
        sample_rate = TARGET_RATE

    pcm = _normalize_pcm(pcm, width)
    return pcm, sample_rate, channels


def process_pcm_hd(raw: bytes, sample_rate: int, channels: int) -> tuple[bytes, int, int]:
    """
    Keep stereo + device sample rate; light peak normalize only.
    Returns (pcm, sample_rate, channels).
    """
    if not raw:
        raise RuntimeError(
            "No audio captured.\nPlay something (YouTube etc.) while recording."
        )

    width = 2  # int16
    channels = max(1, channels)
    pcm = _normalize_pcm(raw, width)
    return pcm, sample_rate, channels


def save_clip(
    raw: bytes,
    sample_rate: int,
    channels: int,
    out_dir: Path,
    quality: Quality = "lean",
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if quality == "hd":
        pcm, rate, ch = process_pcm_hd(raw, sample_rate, channels)
        path = out_dir / f"clip_hd_{stamp}.wav"
    else:
        pcm, rate, ch = process_pcm(raw, sample_rate, channels)
        path = out_dir / f"clip_{stamp}.wav"

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(ch)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(pcm)
    return path


class App(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.resizable(True, True)
        self.minsize(380, 480)
        self.configure(bg="#1a1b1e")
        self.geometry("400x520")

        self.recorder = Recorder()
        self._tick_job: str | None = None
        self._busy = False
        self._hotkeys = None
        self._quality: Quality = "lean"

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()
        # UI first, then audio/hotkey in background → snappier open
        self.after(50, self._init_device)
        self.after(100, self._start_global_hotkey)
        self.after(150, self._migrate_clips_background)

    def _build_ui(self) -> None:
        title_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        body_font = tkfont.Font(family="Segoe UI", size=9)
        timer_font = tkfont.Font(family="Segoe UI", size=32, weight="bold")
        btn_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")

        root = Frame(self, bg="#1a1b1e")
        root.pack(fill="both", expand=True, padx=16, pady=14)

        footer = Label(
            root,
            text=f"Saves to: {OUTPUT_DIR}",
            font=tkfont.Font(family="Segoe UI", size=8),
            fg="#5f6368",
            bg="#1a1b1e",
            wraplength=360,
            justify="left",
        )
        footer.pack(side="bottom", fill="x", pady=(8, 0))

        Label(
            root,
            text="System audio → clip",
            font=title_font,
            fg="#f2f2f2",
            bg="#1a1b1e",
        ).pack(anchor="w")

        self.device_label = Label(
            root,
            text="Starting…",
            font=body_font,
            fg="#9aa0a6",
            bg="#1a1b1e",
            wraplength=360,
            justify="left",
        )
        self.device_label.pack(anchor="w", pady=(4, 8))

        self.timer_label = Label(
            root,
            text="0:00",
            font=timer_font,
            fg="#e8eaed",
            bg="#1a1b1e",
        )
        self.timer_label.pack(pady=(4, 2))

        self.status_label = Label(
            root,
            text="Ready",
            font=body_font,
            fg="#9aa0a6",
            bg="#1a1b1e",
        )
        self.status_label.pack(pady=(0, 10))

        self.record_btn = Button(
            root,
            text="●  RECORD",
            font=btn_font,
            bg="#c5221f",
            fg="white",
            activebackground="#a50e0e",
            activeforeground="white",
            disabledforeground="#cccccc",
            relief="flat",
            bd=0,
            padx=28,
            pady=12,
            cursor="hand2",
            command=lambda: self.toggle_record("lean"),
            width=16,
            height=1,
        )
        self.record_btn.pack(pady=(4, 6))

        self.record_hd_btn = Button(
            root,
            text="●  RECORD HD",
            font=btn_font,
            bg="#1a73e8",
            fg="white",
            activebackground="#1557b0",
            activeforeground="white",
            disabledforeground="#cccccc",
            relief="flat",
            bd=0,
            padx=28,
            pady=12,
            cursor="hand2",
            command=lambda: self.toggle_record("hd"),
            width=16,
            height=1,
        )
        self.record_hd_btn.pack(pady=(0, 6))

        self.convert_btn = Button(
            root,
            text="Convert WAV → M4A…",
            font=tkfont.Font(family="Segoe UI", size=10, weight="bold"),
            bg="#3c4043",
            fg="white",
            activebackground="#5f6368",
            activeforeground="white",
            disabledforeground="#cccccc",
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.convert_existing_wav,
            width=18,
        )
        self.convert_btn.pack(pady=(8, 4))

        Label(
            root,
            text=f"Hotkey: {HOTKEY_LABEL}  ·  lean mono 22 kHz\n"
            "RECORD HD  ·  stereo @ device rate\n"
            "Convert  ·  pick an existing .wav for WhatsApp",
            font=body_font,
            fg="#8ab4f8",
            bg="#1a1b1e",
            justify="center",
        ).pack(pady=(4, 0))

    def _start_global_hotkey(self) -> None:
        try:
            from pynput import keyboard
        except ImportError:
            return

        def on_activate() -> None:
            try:
                # Lean only; no-op while HD is recording (handled in toggle_record)
                self.after(0, lambda: self.toggle_record("lean"))
            except Exception:
                pass

        try:
            self._hotkeys = keyboard.GlobalHotKeys({HOTKEY_COMBO: on_activate})
            self._hotkeys.daemon = True  # type: ignore[attr-defined]
            self._hotkeys.start()
        except Exception:
            pass

    def _short_device_name(self, name: str) -> str:
        for junk in (" [Loopback]", " (Loopback)", " [Bucle invertido]"):
            name = name.replace(junk, "")
        if len(name) > 48:
            name = name[:45] + "…"
        return name

    def _init_device(self) -> None:
        def work() -> None:
            err = self.recorder.prepare()

            def done() -> None:
                if err:
                    self.device_label.config(text=err, fg="#f28b82")
                    self.record_btn.config(state="disabled")
                    self.record_hd_btn.config(state="disabled")
                    self.status_label.config(text="Audio setup failed", fg="#f28b82")
                    return
                short = self._short_device_name(self.recorder.device_name)
                self.device_label.config(
                    text=f"Listening to: {short}",
                    fg="#9aa0a6",
                )

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _migrate_clips_background(self) -> None:
        def work() -> None:
            try:
                n = migrate_legacy_clips()
            except Exception:
                n = 0

            def done() -> None:
                if n > 0:
                    self.status_label.config(
                        text=f"Moved {n} old clip(s) into clips folder",
                        fg="#81c995",
                    )

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def convert_existing_wav(self) -> None:
        """Pick a .wav (default: clips folder) and convert to M4A for WhatsApp."""
        if self._busy or self.recorder.recording:
            messagebox.showinfo(APP_TITLE, "Finish the current recording first.")
            return

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        initial = OUTPUT_DIR if OUTPUT_DIR.is_dir() else APP_DIR
        chosen = filedialog.askopenfilename(
            parent=self,
            title="Choose a WAV to convert for WhatsApp",
            initialdir=str(initial),
            filetypes=[
                ("WAV audio", "*.wav"),
                ("All files", "*.*"),
            ],
        )
        if not chosen:
            return

        wav_path = Path(chosen)
        if wav_path.suffix.lower() != ".wav":
            messagebox.showerror(APP_TITLE, "Please pick a .wav file.")
            return

        quality = quality_from_wav(wav_path)
        self._busy = True
        self.convert_btn.config(state="disabled", text="Converting…")
        self.status_label.config(text=f"Converting {wav_path.name}…", fg="#9aa0a6")

        def work() -> None:
            err: str | None = None
            out: Path | None = None
            try:
                out = wav_to_m4a(wav_path, quality=quality)
            except Exception as exc:
                err = str(exc)

            def done() -> None:
                self._busy = False
                self.convert_btn.config(state="normal", text="Convert WAV → M4A…")
                if err or out is None:
                    self.status_label.config(text="Convert failed", fg="#f28b82")
                    messagebox.showerror(APP_TITLE, err or "Unknown error")
                    return

                kb = out.stat().st_size / 1024
                self.status_label.config(
                    text=f"Saved {out.name} ({kb:.0f} KB)",
                    fg="#81c995",
                )
                try:
                    self.clipboard_clear()
                    self.clipboard_append(str(out))
                    self.update()
                except Exception:
                    pass
                messagebox.showinfo(
                    APP_TITLE,
                    f"M4A ready for WhatsApp:\n{out.name}\n\n"
                    f"({kb:.0f} KB)  ·  path copied to clipboard",
                )

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def toggle_record(self, quality: Quality = "lean") -> None:
        if self._busy:
            return
        if self.recorder.recording:
            # Hotkey (lean) must not stop an HD session
            if quality != self._quality:
                return
            self._stop_and_save()
        else:
            self._start(quality)

    def _start(self, quality: Quality) -> None:
        try:
            self.recorder.start()
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Could not start recording:\n{exc}")
            return

        self._quality = quality
        stop_style = {
            "text": "■  STOP",
            "bg": "#5f6368",
            "activebackground": "#3c4043",
            "state": "normal",
        }
        if quality == "hd":
            self.record_hd_btn.config(**stop_style)
            self.record_btn.config(state="disabled")
            self.status_label.config(
                text="Recording HD… play your audio now",
                fg="#8ab4f8",
            )
        else:
            self.record_btn.config(**stop_style)
            self.record_hd_btn.config(state="disabled")
            self.status_label.config(
                text="Recording… play your video now",
                fg="#f28b82",
            )
        self._tick()

    def _tick(self) -> None:
        if not self.recorder.recording:
            return
        secs = int(self.recorder.elapsed())
        self.timer_label.config(text=f"{secs // 60}:{secs % 60:02d}")
        self._tick_job = self.after(200, self._tick)

    def _reset_record_buttons(self) -> None:
        self.record_btn.config(
            state="normal",
            text="●  RECORD",
            bg="#c5221f",
            activebackground="#a50e0e",
        )
        self.record_hd_btn.config(
            state="normal",
            text="●  RECORD HD",
            bg="#1a73e8",
            activebackground="#1557b0",
        )

    def _stop_and_save(self) -> None:
        self._busy = True
        quality = self._quality
        self.status_label.config(text="Saving…", fg="#9aa0a6")
        self.record_btn.config(state="disabled")
        self.record_hd_btn.config(state="disabled")
        self.update_idletasks()

        def work() -> None:
            err: str | None = None
            path: Path | None = None
            try:
                raw, rate, ch = self.recorder.stop()
                path = save_clip(raw, rate, ch, OUTPUT_DIR, quality=quality)
            except Exception as exc:
                err = str(exc)

            def done() -> None:
                self._busy = False
                self._reset_record_buttons()
                self.timer_label.config(text="0:00")
                if self._tick_job:
                    try:
                        self.after_cancel(self._tick_job)
                    except Exception:
                        pass
                    self._tick_job = None

                if err or path is None:
                    self.status_label.config(text="Save failed", fg="#f28b82")
                    messagebox.showerror(APP_TITLE, err or "Unknown error")
                    return

                kb = path.stat().st_size / 1024
                self.status_label.config(
                    text=f"Saved {path.name} ({kb:.0f} KB)",
                    fg="#81c995",
                )
                self._after_save_popup(path, quality)

            self.after(0, done)

        threading.Thread(target=work, daemon=True).start()

    def _after_save_popup(self, path: Path, quality: Quality) -> None:
        popup = Toplevel(self)
        popup.title("Clip ready")
        popup.configure(bg="#1a1b1e")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        self.update_idletasks()
        px = self.winfo_rootx() + 20
        py = self.winfo_rooty() + 40
        popup.geometry(f"360x230+{px}+{py}")

        # Shared so Convert can retarget Copy / Play / folder select
        current: dict[str, Path] = {"path": path}

        name_label = Label(
            popup,
            text=path.name,
            font=tkfont.Font(family="Segoe UI", size=11, weight="bold"),
            fg="#e8eaed",
            bg="#1a1b1e",
            wraplength=320,
        )
        name_label.pack(pady=(16, 4), padx=12)

        size_kb = path.stat().st_size / 1024
        if quality == "hd":
            try:
                with wave.open(str(path), "rb") as wf:
                    ch = wf.getnchannels()
                    rate = wf.getframerate()
                ch_label = "stereo" if ch >= 2 else "mono"
                subtitle = f"{size_kb:.0f} KB  ·  {ch_label} {rate // 1000} kHz HD WAV"
            except Exception:
                subtitle = f"{size_kb:.0f} KB  ·  HD WAV"
        else:
            subtitle = f"{size_kb:.0f} KB  ·  lean WAV (convert for WhatsApp)"

        detail_label = Label(
            popup,
            text=subtitle,
            font=tkfont.Font(family="Segoe UI", size=9),
            fg="#9aa0a6",
            bg="#1a1b1e",
        )
        detail_label.pack()

        row = Frame(popup, bg="#1a1b1e")
        row.pack(pady=(12, 6))

        row2 = Frame(popup, bg="#1a1b1e")
        row2.pack(pady=(0, 8))

        def style_btn(b: Button) -> None:
            b.configure(
                relief="flat",
                padx=12,
                pady=6,
                cursor="hand2",
                font=tkfont.Font(family="Segoe UI", size=9, weight="bold"),
            )

        def copy_path() -> None:
            p = current["path"]
            self.clipboard_clear()
            self.clipboard_append(str(p))
            self.update()
            self.status_label.config(
                text="Path copied — attach in WhatsApp",
                fg="#81c995",
            )

        def open_folder() -> None:
            subprocess.Popen(["explorer", "/select,", str(current["path"])])

        def play() -> None:
            try:
                os.startfile(str(current["path"]))  # type: ignore[attr-defined]
            except Exception as exc:
                messagebox.showerror(APP_TITLE, f"Could not play:\n{exc}")

        def export_m4a() -> None:
            m4a_btn.config(state="disabled", text="Converting…")
            detail_label.config(text="Making M4A for WhatsApp…", fg="#9aa0a6")
            self.status_label.config(text="Converting to M4A…", fg="#9aa0a6")

            def work() -> None:
                err: str | None = None
                out: Path | None = None
                try:
                    out = wav_to_m4a(path, quality=quality)
                except Exception as exc:
                    err = str(exc)

                def done() -> None:
                    if err or out is None:
                        m4a_btn.config(state="normal", text="M4A for WhatsApp")
                        detail_label.config(text="M4A failed", fg="#f28b82")
                        self.status_label.config(text="M4A convert failed", fg="#f28b82")
                        messagebox.showerror(APP_TITLE, err or "Unknown error")
                        return

                    current["path"] = out
                    kb = out.stat().st_size / 1024
                    name_label.config(text=out.name)
                    detail_label.config(
                        text=f"{kb:.0f} KB  ·  M4A ready for WhatsApp",
                        fg="#81c995",
                    )
                    m4a_btn.config(state="disabled", text="M4A done ✓")
                    self.status_label.config(
                        text=f"Saved {out.name} ({kb:.0f} KB)",
                        fg="#81c995",
                    )
                    # Auto-copy path so attach is one step
                    try:
                        self.clipboard_clear()
                        self.clipboard_append(str(out))
                        self.update()
                    except Exception:
                        pass

                self.after(0, done)

            threading.Thread(target=work, daemon=True).start()

        b1 = Button(row, text="Copy path", command=copy_path, bg="#8ab4f8", fg="#202124")
        b2 = Button(row, text="Open folder", command=open_folder, bg="#3c4043", fg="white")
        b3 = Button(row, text="Play", command=play, bg="#3c4043", fg="white")
        for b in (b1, b2, b3):
            style_btn(b)
            b.pack(side="left", padx=4)

        m4a_btn = Button(
            row2,
            text="M4A for WhatsApp",
            command=export_m4a,
            bg="#34a853",
            fg="white",
            activebackground="#2d8e47",
            activeforeground="white",
            disabledforeground="#cccccc",
        )
        style_btn(m4a_btn)
        m4a_btn.configure(padx=20)
        m4a_btn.pack()

        Button(
            popup,
            text="Close",
            command=popup.destroy,
            bg="#1a1b1e",
            fg="#9aa0a6",
            relief="flat",
            cursor="hand2",
        ).pack(pady=(0, 10))

    def _on_close(self) -> None:
        if self._hotkeys is not None:
            try:
                self._hotkeys.stop()
            except Exception:
                pass
            self._hotkeys = None
        try:
            self.recorder.close()
        except Exception:
            pass
        self.destroy()


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
