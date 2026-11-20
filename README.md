# Vídeos de Vera · Academia Volvera

Programa de montaje de los vídeos de Vera para la Academia (volvera.io/academia). Rehecho el 20 nov 2026 por 🧠 Agentes (el anterior estaba en un ordenador temporal y se perdió). Método original: `claude/academia/estado-videos-academia-2026-10-22.md` en el proyecto Volvera.IO.

## Cómo se monta un vídeo

1. **Voz:** ElevenLabs, voz Gala (`Wi5NZQRxyOb3Jx4r0hrI`), modelo eleven_v4, una toma por capítulo. Las marcas de tono (`[warm, didactic]`…) no se dicen y el programa las quita de los subtítulos.
2. **Palabras con tiempo:** transcripción gratis con ElevenLabs Scribe (`eleven_scribe_v1`) → `cN.words.json`.
3. **Escena:** `<lección>/scenes/cN.json`: el rótulo del capítulo y lo que sale en pantalla. Cada elemento aparece cuando la voz dice su palabra (`at`) y puede irse cuando dice otra (`out_at`).
4. **Montaje:**
   ```
   python3 engine/build.py l7/scenes/c1.json l7/in/c1.mp3 l7/in/c1.words.json out/vera-7-c1
   ```
   Saca `vera-7-c1.mp4` (H.264 1280×720, crf 23, faststart), `vera-7-c1.webm` (VP9), `vera-7-c1-poster.jpg` (fotograma a 2,4 s) y `vera-7-c1.meta.json` (duración y transcripción para la web).

Necesita Python 3 con Playwright (Chromium) y ffmpeg con libx264, libvpx-vp9 y libopus.

## Reglas (las comprueba el programa)
- Subtítulos con los tiempos por palabra del audio final: lo dicho en oscuro y lo que falta en gris.
- Vera: el recorte oficial (`assets/vera.webp`), solo se mueve (flota, se ladea y responde a la voz). Sin lip-sync.
- Letras Urbanist y Onest (en `assets/fonts`); si no cargan, el montaje se para.
- **Nada encima de nada:** el programa mira cada 0,2 s que ningún elemento pise a otro, al bocadillo, a Vera ni al borde; si pasa, se para y dice cuándo.
- Menos de 9,5 MB. Audio normalizado a −16 LUFS.
- En la voz se dice «inteligencia artificial», nunca «IA». Sin rótulo de IA en pantalla (decisión de Jorge, 28-29 oct 2026).
- Estados nunca solo por color: icono + palabra (✓ ▲ ✕).
- Datos en pantalla solo si la voz los dice, con su fuente visible.

## Lecciones
- `l7/` · Lección 7 «Vuelve»: voces y palabras de los 5 capítulos (`in/`), escenas (`scenes/`) y vídeos montados (`final/`).
