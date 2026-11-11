# Am Hassan: a short film on cheating in trade (Surat Al-Mutaffifin 1–3)

- `am-hassan-short-film.mp4`: final video, 1920×1080, 30fps, 3:27.5, with the voiceover and film foley (no music), about −14 LUFS.

## Where to add the Qari's recitation
The Quran is never spoken by the TTS voice. Two slots are left completely silent (−91 dB measured in the final file) for a real recitation:

| Slot | On screen | Time in the video |
|---|---|---|
| 1 | Basmala appears | 1:08.75 |
| 1 | Verse 1 appears | 1:14.75 |
| 1 | Verse 2 appears | 1:21.25 |
| 1 | Verse 3 appears | 1:29.75 |
| 1 | Slot ends, narration resumes | 1:38.25 |
| 2 (end card) | Basmala appears | 2:51.8 |
| 2 | Verse 1 appears | 2:58.0 |
| 2 | Verse 2 appears | 3:04.0 |
| 2 | Verse 3 appears | 3:12.0 |
| 2 | "صدق الله العظيم" appears | 3:21.4 |
| 2 | Video ends | 3:27.5 |

If the recitation is longer or shorter than these slots, the slot lengths are set near the top of `tpl.html` and `mut_sfx.py` and the video can be re-timed and re-rendered.

## Quranic text
The verses come directly from the King Fahd Glorious Qur'an Printing Complex text (UthmanicHafs v3.0, `quran.json`) and are shown in the Complex's official font. The text is injected by script (`build.py`: `tpl.html` → `index.html`), never typed by hand.

## Sources shown on screen
| On screen | Source |
|---|---|
| «﴿وَيْلٌ﴾ كلمة عذاب ووعيد» | Al-Sa'di, Taysir al-Karim al-Rahman |
| «والمراد بالتطفيف هاهنا: البخس في المكيال والميزان، إما بالازدياد إن اقتضى من الناس، وإما بالنقصان إن قضاهم» | Ibn Kathir, Tafsir al-Qur'an al-'Azim |
| «للذين ينقصون الناس، ويبخسونهم حقوقهم» | Al-Tabari, Jami' al-Bayan |
| «فهذا سرقة لأموال الناس، وعدم إنصاف لهم منهم» | Al-Sa'di |
| The heap of food and «من غشّ فليس مني» | Sahih Muslim (102), from Abu Hurayrah |
| Cheating in buying and selling is forbidden | Dar Al-Ifta Al-Misriyyah (general ruling; exact fatwa reference not yet added) |

The scholars' quotes and the hadith wording were written from memory and not checked against the printed books here. Have someone with knowledge review them before publishing.

## Files
- `tpl.html`, `build.py`, `index.html`: the whole film as one deterministic timeline (`seek(t)`): sets, three rigged characters with lip-sync, inserts, the freeze, and the Islamic section.
- `words.json`, `words_b.json`: word timestamps of the two voiceover clips.
- `env.js`: per-frame voice loudness used for lip-sync.
- `mut_sfx.py`, `sfxlib.py`: the foley and mix. `sfx-only.wav` is the effects layer on its own.
- `render.js`, `preview.js`: render the whole video, or individual frames.
