"""Build one reel.   python build.py specs/dayNN_topic.py [voice_audio_file]
Renders the silent video, synthesises the music, and muxes them. With a voice file, the music is
ducked under the voice. Output: out/<spec name>.mp4 (plus _silent.mp4 and _bgm.wav)."""
import sys, os, subprocess
here = os.path.dirname(os.path.abspath(__file__))
spec = sys.argv[1]
voice = sys.argv[2] if len(sys.argv) > 2 else None
name = os.path.splitext(os.path.basename(spec))[0]
out = os.path.join(here, "out"); os.makedirs(out, exist_ok=True)
silent, bgm, final = (os.path.join(out, name + s) for s in ("_silent.mp4", "_bgm.wav", ".mp4"))
run = lambda *a: subprocess.run(a, check=True)
py = sys.executable
run(py, os.path.join(here, "reel.py"), "music", spec, bgm)
run(py, os.path.join(here, "reel.py"), "render", spec, silent)
if voice:
    # voice at full level; music at ~25% and ducked further whenever the voice speaks
    fc = ("[1:a]volume=0.25[m];[2:a]apad,asplit=2[v][sc];[m][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=300[md];"
          "[v][md]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]")
    run("ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", bgm, "-i", voice, "-filter_complex", fc,
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final)
else:
    run("ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", bgm, "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final)
print("done:", final)
