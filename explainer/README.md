# AI for small businesses: motion graphics explainer (Egyptian Arabic)

- `ai-small-business-explainer.mp4`: final video, 1920×1080, 30fps, 63s, with the voiceover.
- `index.html`: the whole animation as one deterministic timeline (`seek(t)`). Open it in a browser and call `seek(12.3)` in the console to scrub.
- `render.js`: renders every frame with Playwright and encodes it with ffmpeg (`node render.js`, then mux the chunks with the voiceover).
- `preview.js`: renders individual frames, for example `node preview.js 5 24.5 50`.

Scene timing comes from pause detection on the voiceover (37 speech segments, one per phrase of the script), listed in `SEG` at the top of the script.
