# Tech in a Bite: daily video pipeline
Code and instructions for the @techinabite page. A scheduled cloud run follows `RUN_DAILY.md` each morning and delivers a
30-60 second animated video, a voiceover script and a caption. The owner adds the voiceover and posts manually.

- `RUN_DAILY.md`: the daily procedure.
- `CLAUDE.md`: brand and writing rules.
- `reel.py`, `build.py`: video generator (Pillow + ffmpeg), original synthesised music, no copyright issues.
- `specs/`: one file per video. `_example_generic_scenes.py` is the template.
- `skills/`: three skills from [Jakeschincariol/instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill) (MIT, license in `THIRD_PARTY/`).
- `fonts/`: Inter (SIL Open Font License).
Local test: `pip install -r requirements.txt`, install ffmpeg, then `python build.py specs/day04_database_index.py`.

Repository: https://github.com/PiyushD17/ClaudeInsta
