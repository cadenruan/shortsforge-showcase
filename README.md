# CourtVision

### Automated Basketball Highlight Editor

**It watches a half-hour basketball highlight video and edits it down to a half-minute
vertical clip — picking the plays, following the players, and cutting it in time with the
music.**

### ▶︎ [**cadenruan.github.io/CourtVision-showcase**](https://cadenruan.github.io/CourtVision-showcase/)

---

Editing a highlight reel by hand takes hours. You sit through the whole video, pick out the
good plays, trim each one so the basket lands where you want it, re-crop every shot for a
phone screen, then line the whole thing up with a song.

CourtVision does all of it on its own. Give it a long highlight compilation, a player and a
song, and it hands back a finished vertical clip.

Six reels are in [`reels/`](reels/) — six players, six songs, footage spanning three
decades. Nobody touched them. Every play, cut, crop and bit of timing was chosen by the
software.

## How it works

1. **Watch the whole thing** — the noise, the movement, and every camera cut.
2. **Find the plays** — who has the ball, when they shoot, and whether it drops.
3. **Pick the best ones** — no repeats, and nothing that crosses a camera cut.
4. **Cut to the music** — clips are whole beats, and the big basket lands on the drop.
5. **Reframe for a phone** — the crop follows the player down the court.

About 40,000 lines of Python, running offline on one machine. Nothing is guessed: the same
video and the same song always produce the same edit, frame for frame.

## What it sees

[`reels/rose-tracking.mp4`](reels/rose-tracking.mp4) is one of those reels with the
software's own view drawn on top: everyone on court, the player the clip is about, the
phone-shaped crop it keeps, the ball, and the rim.

Four models do the looking, all running on the laptop rather than a server. One finds the
people and the ball, one finds rims, one watches for the moment the broadcast cuts to a
different camera, and one reads the number on a jersey.

## Viewing it locally

```bash
python serve.py
```

Then open <http://localhost:8731>. Use that script rather than `python -m http.server`,
which does not answer byte-range requests — without them Safari will not start a video at
all, and Chrome cannot seek in one.

---

Technical detail: [ARCHITECTURE.md](ARCHITECTURE.md) · [METHOD.md](METHOD.md)

*The reels are highlight footage cut to commercial music, shown as examples of what the
software produces.*
