# Surat Al-Asr: the formula for success (motion graphics explainer)

- `surat-al-asr-formula.mp4`: final video, 1920×1080, 30fps, 2:47, with the voiceover and sound effects (no music), about −13 LUFS.

## Quranic text
- The verses are taken directly from the King Fahd Glorious Qur'an Printing Complex text (UthmanicHafs v3.0), stored in `asr_kfgqpc.json`, and displayed in the Complex's official font `fonts/UthmanicHafs-v-3.0.ttf`. The font's checksum matches the one published by the Complex.
- The text is injected into the page by script (`tpl.html` → `index.html`), never typed by hand.
- Every verse appears on screen in complete silence (−91 dB measured in the final file): no voice, no effects.

## Tafsir sources shown on screen
| On screen | Source |
|---|---|
| «لو تدبّر الناس هذه السورة لوسعتهم» | Al-Shafi'i, quoted by Ibn Kathir in his tafsir |
| «والعصر اسم للدهر» | Al-Tabari, Jami' al-Bayan |
| «أقسم تعالى بالعصر، الذي هو الليل والنهار، محل أفعال العباد وأعمالهم» | Al-Sa'di, Taysir al-Karim al-Rahman |
| «والخسار مراتب متعددة متفاوتة» | Al-Sa'di |
| «نعمتان مغبون فيهما كثير من الناس: الصحة والفراغ» | Sahih al-Bukhari (6412), from Ibn Abbas |
| «ولا يكون الإيمان بدون العلم» | Al-Sa'di |
| «وهذا شامل لأفعال الخير كلها، الظاهرة والباطنة» | Al-Sa'di |
| «أي: يوصي بعضهم بعضًا بذلك، ويحثّه عليه، ويرغّبه فيه» | Al-Sa'di |
| «على طاعة الله، وعن معصية الله، وعلى أقدار الله المؤلمة» | Al-Sa'di |
| «فالأمران الأولان يكمّل بهما الإنسان نفسه، والأمران الأخيران يكمّل بهما غيره» | Al-Sa'di |
| «وبتكميل الأمور الأربعة، يكون الإنسان قد سلم من الخسار، وفاز بالربح العظيم» | Al-Sa'di |

Have someone with knowledge review the scholars' quotes against the printed books before publishing.

## Files
- `asr_sfx.py`: sound design using natural sounds only (no music, bells or melodic tones), with silence enforced during the verses.
- `words.json`: word timestamps from the voiceover, used to sync every line.
- `render.js` and `preview.js`: render the whole video, or individual frames.
