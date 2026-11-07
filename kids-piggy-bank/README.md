# Youssef's magic piggy bank (حصّالة يوسف السحرية): kids' motion graphics story

- `youssef-magic-piggy-bank.mp4`: final video, 1920×1080, 30fps, 92s, with the voiceover and sound effects (no music), about −13 LUFS.
- `index.html`: the whole animation as one deterministic timeline (`seek(t)`). It has 13 scenes, 4 characters with expressions and lip-sync, a coin counter, and dialogue shown in speech bubbles and storybook narration.
- `words.json`: word-level timestamps from transcribing the voiceover (Whisper small). Every line and beat is timed from these.
- `env.js`: per-frame loudness of the voice, used to drive the mouths.
- `kids_sfx.py` and `sfxlib.py`: the synthesized cartoon sound design (coin clinks, boings, poofs, alarm ring, gong, sizzle, zaps, birds and crickets), mixed under the voice with ducking, stereo panning and reverb. Run `python3 kids_sfx.py vo48.wav mix.wav`.
- `sfx-only.wav`: the effects layer on its own, for use in another editor.
- `render.js` and `preview.js`: render all frames, or individual frames, with Playwright and ffmpeg.
