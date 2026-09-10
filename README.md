# CourtVision
### Automated Basketball Highlight Editor

## ▶︎ [**See it live — cadenruan.github.io/CourtVision-showcase**](https://cadenruan.github.io/CourtVision-showcase/)

**It watches a half-hour basketball highlight video and edits it down to a half-minute
edit-styled vertical clip, picking the plays, following the players, and cutting it on beat
with the music.**

---

Editing a highlight reel by hand takes hours: picking out the good plays, trimming each one
so the basket lands where you want it, re-cropping every shot for a phone screen, then
lining the whole thing up with a song.

CourtVision does all of it on its own. It takes in a long highlight compilation, a player
and a song, and it hands back a finished short edit-styled clip.

Six edits are in [`reels/`](reels/), made through this project using six players, six songs
and footage spanning three decades. Every play, cut, crop and bit of timing was chosen by
the software.

## How it works

1. **Watch the whole thing** — the noise, the movement, and every camera cut.
2. **Find the plays** — who has the ball, when they shoot, and whether it drops.
3. **Pick the best ones** — no repeats, and nothing that crosses a camera cut.
4. **Cut to the music** — clips are whole beats, and the big basket lands on the drop.
5. **Reframe for a phone** — the crop follows the player down the court.

~40,000 lines of Python, running offline on one machine. Unless specified, the same video
and the same song always produce the same edit, frame for frame.

## What it sees

[`reels/rose-tracking.mp4`](reels/rose-tracking.mp4) is one reel with the software's view
drawn on top: everyone on court, the player the clip is about, the phone-shaped crop it
keeps, the ball, and the rim.

Four models do the looking, and all of them ran locally on my laptop. One finds the people
and the ball. One finds the rim. One watches for the moment the broadcast cuts to a
different camera, so a clip never exists between two shots. One reads the number on a
jersey, which is how a reel about one player stays on that player.
