#!/usr/bin/env python3
"""Monta un vídeo de Vera para la Academia Volvera.

Uso: python3 engine/build.py <escena.json> <voz.mp3> <palabras.json> <salida-sin-extension>

- escena.json: capítulo y elementos en pantalla; cada elemento aparece cuando la voz dice su palabra («at»)
  y puede irse cuando dice otra («out_at»).
- palabras.json: tiempos por palabra de ElevenLabs Scribe ({"words":[{text,start,end,type}]}).
Salida: <salida>.mp4 (H.264, 1280x720, crf 23, faststart), <salida>.webm (VP9) y <salida>-poster.jpg (fotograma a 2,4 s).
Reglas: claude/academia/estado-videos-academia-2026-10-22.md (voz Gala, subtítulos por palabra, Vera solo se mueve,
nada encima de nada, < 9,5 MB). Sin rótulo de IA (decisión de Jorge, 28-29 oct 2026).
"""
import json, os, re, subprocess, sys, tempfile, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FPS = 25
W, H = 1280, 720


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w]", "", s)


def load_words(path):
    raw = json.load(open(path))
    ws = raw["words"] if isinstance(raw, dict) else raw
    out = []
    for w in ws:
        if w.get("type", "word") != "word":
            continue
        t = w["text"].strip()
        if t.startswith("[") or t.endswith("]"):  # marcas de tono de eleven_v4: no se dicen
            continue
        out.append({"w": t, "s": round(w["start"], 3), "e": round(w["end"], 3)})
    return out


def phrases(words, max_words=12):
    """Frases para el bocadillo: cortan en . ? ! : » y, si ya llevan 5 palabras, en la coma; nunca más de max_words."""
    ph, i0 = [], 0
    for i, w in enumerate(words):
        n = i - i0 + 1
        nxt_left = len(words) - i - 1
        to_stop = next((k - i for k in range(i, len(words)) if re.search(r"[.?!:»]$", words[k]["w"])), 99)
        end = (re.search(r"[.?!:»]$", w["w"]) or (n >= 5 and w["w"].endswith(",") and nxt_left >= 3)
               or (n >= max_words and to_stop > 3))
        if end or i == len(words) - 1:
            ph.append({"s": words[i0]["s"], "e": w["e"], "i0": i0, "i1": i})
            i0 = i + 1
    for a, b in zip(ph, ph[1:]):
        a["e"] = max(a["e"], min(b["s"] - 0.05, a["e"] + 0.6))
    return ph


def find(words, key, start=0):
    k = norm(key)
    for i in range(start, len(words)):
        if norm(words[i]["w"]).startswith(k):
            return i
    raise SystemExit(f"⛔ no encuentro «{key}» en la voz (desde la palabra {start})")


def resolve(scene, words):
    items, cursor = [], 0
    for it in scene["items"]:
        it = dict(it)
        if "at" in it:
            i = find(words, it["at"], cursor if it.get("after_prev", True) else 0)
            cursor = i
            it["t"] = max(0.0, words[i]["s"] - it.get("lead", 0.1))
        it.setdefault("t", 0.0)
        if "out_at" in it:
            j = find(words, it.pop("out_at"), 0 if it.get("out_from_start") else cursor)
            it["out"] = words[j]["s"] - 0.25
        items.append({k: v for k, v in it.items() if k in ("t", "out", "x", "y", "w", "html", "cls")})
    return items


def envelope(mp3, n_frames):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    import array, math
    a = array.array("h", pcm)
    hop = 16000 // FPS
    env = []
    for f in range(n_frames):
        seg = a[f * hop:(f + 1) * hop]
        env.append(math.sqrt(sum(x * x for x in seg) / len(seg)) / 32768 if seg else 0.0)
    m = max(env) or 1
    sm, prev = [], 0.0
    for v in env:
        prev = prev * 0.6 + (v / m) * 0.4
        sm.append(round(prev, 3))
    return sm


def overlaps(page, times):
    js = """t => { render(t); const vis = [...document.querySelectorAll('.el')].filter(e => +e.style.opacity > .5).map(e => e.getBoundingClientRect());
      const b = document.getElementById('bubble'); if (+b.style.opacity > .5) vis.push(b.getBoundingClientRect());
      const bad = []; for (let i = 0; i < vis.length; i++) for (let j = i + 1; j < vis.length; j++) { const a = vis[i], c = vis[j];
        if (a.left < c.right - 2 && c.left < a.right - 2 && a.top < c.bottom - 2 && c.top < a.bottom - 2) bad.push([i, j]); }
      const v = document.getElementById('vera').getBoundingClientRect();
      vis.forEach((a, i) => { if (a.right > v.left + 40 && a.bottom > v.top + 60) bad.push([i, 'vera']); if (a.right > 1270 || a.bottom > 715) bad.push([i, 'borde']); });
      return bad; }"""
    probs = []
    for t in times:
        bad = page.evaluate(js, t)
        if bad:
            probs.append((round(t, 2), bad))
    return probs


def main(scene_path, mp3, words_path, out):
    from playwright.sync_api import sync_playwright
    scene = json.load(open(scene_path))
    words = load_words(words_path)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3],
                               capture_output=True, text=True, check=True).stdout) + 0.6
    n = int(dur * FPS)
    data = {"chap": scene["chap"], "duration": dur, "words": words, "phrases": phrases(words),
            "items": resolve(scene, words), "env": envelope(mp3, n)}
    html = (ROOT / "engine/base.html").read_text().replace("<script>", "<script>window.DATA=" + json.dumps(data, ensure_ascii=False) + ";</script><script>", 1)
    tmp = ROOT / "engine" / f".{Path(out).name}.html"
    tmp.write_text(html)
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    raw = tempfile.mktemp(suffix=".mp4")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(tmp.as_uri()); pg.wait_for_timeout(400)
        assert pg.evaluate("document.fonts.check('600 40px Urbanist') && document.fonts.check('16px Onest')"), "⛔ no cargan Urbanist/Onest"
        probs = overlaps(pg, [i / 5 for i in range(int(dur * 5))])
        if probs and not os.environ.get("ALLOW_OVERLAP"):
            raise SystemExit(f"⛔ solapes: {probs[:8]}")
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                                "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", raw], stdin=subprocess.PIPE)
        for f in range(n):
            pg.evaluate("t => render(t)", f / FPS)
            enc.stdin.write(pg.screenshot(type="jpeg", quality=92))
        enc.stdin.close(); enc.wait(); b.close()
    tmp.unlink()
    af = "loudnorm=I=-16:TP=-1.5:LRA=11,apad"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-i", mp3, "-filter_complex", f"[1:a]{af}[a]", "-map", "0:v", "-map", "[a]",
                    "-shortest", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "128k", f"{out}.mp4"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-i", mp3, "-filter_complex", f"[1:a]{af}[a]", "-map", "0:v", "-map", "[a]",
                    "-shortest", "-c:v", "libvpx-vp9", "-crf", "36", "-b:v", "0", "-deadline", "good", "-cpu-used", "4", "-row-mt", "1",
                    "-c:a", "libopus", "-b:a", "96k", f"{out}.webm"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "2.4", "-i", f"{out}.mp4", "-frames:v", "1", "-q:v", "3", f"{out}-poster.jpg"], check=True)
    os.unlink(raw)
    size = os.path.getsize(f"{out}.mp4") / 1e6
    print(f"✅ {out.name}: {dur:.1f} s · mp4 {size:.1f} MB · webm {os.path.getsize(f'{out}.webm')/1e6:.1f} MB")
    if size > 9.5:
        raise SystemExit("⛔ más de 9,5 MB")
    json.dump({"duration": round(dur - 0.6, 2), "transcript": " ".join(w["w"] for w in words)},
              open(f"{out}.meta.json", "w"), ensure_ascii=False)


if __name__ == "__main__":
    main(*sys.argv[1:5])
