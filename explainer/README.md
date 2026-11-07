# AI for small businesses: motion graphics explainer (Egyptian Arabic)

- `ai-small-business-explainer.mp4`: final video, 1920×1080, 30fps, 63s, with the voiceover.
- `index.html`: the whole animation as one deterministic timeline (`seek(t)`). Open it in a browser and call `seek(12.3)` in the console to scrub.
- `render.js`: renders every frame with Playwright and encodes it with ffmpeg (`node render.js`, then mux the chunks with the voiceover).
- `preview.js`: renders individual frames, for example `node preview.js 5 24.5 50`.

Scene timing comes from pause detection on the voiceover (37 speech segments, one per phrase of the script), listed in `SEG` at the top of the script.

## Sound design
- `sfx.py`: synthesizes every sound effect (no music) on the same timeline as the animation: whooshes, pops, impacts, risers, UI clicks, typing, chimes. It mixes them under the voiceover with ducking, stereo panning that follows on-screen position, and light reverb. Run `python3 sfx.py vo48.wav mix.wav` (48 kHz mono voiceover in, stereo mix out at about −14 LUFS).
- `sfx-only.wav`: the effects layer on its own, normalized, for use in another editor.
