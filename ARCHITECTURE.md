# Architecture — what runs, in order

Every stage below is deterministic Python. There are no model calls in the decision
path except the vision models, and those are used as *evidence*, never as authority.

## 1 · Inputs

| | |
|---|---|
| **source reel** | one 10–30 minute highlight compilation, mixed aspect ratios, mixed decades, roughly 29% of clips already vertical |
| **track** | an authored music bed, analysed for BPM, beat grid and drop |
| **player** | jersey number, height, season — the jersey number is the only identity signal that has ever generalised |

## 2 · Evidence gathering

**`highlight_finder.analyze`** — audio and motion features over the whole reel: crowd
roar, rise, impact, motion energy, spread, sharpness. ⚠️ The reel's audio is
*contaminated* (the compiler mixed a music bed over the broadcast), so roar is a weak
signal on some sources and no signal at all on others — which nothing knew until it
was measured per reel.

**`cuts`** — TransNetV2 shot boundaries. Two heads: a single-frame head and an
all-frames head built for gradual transitions. The *clamp* takes the elementwise max
of both, deliberately: a false boundary shortens a window, a missed one ships a cut
inside a scene. (That asymmetry is currently the largest known open defect — see the
README.)

**`source_units`** — boundaries a **human** confirmed from the frames. A candidate may
not span one. This is proof, not a statistic, and it is the only cut evidence allowed
to act as a hard gate.

**`continuity`** — ORB features and one homography per frame step. A third, independent
family of evidence: *a pan is a homography and keeps its inliers however violently it
moves; a cut is not.* At `match_frac < 0.03` it finds 6 of 13 labelled cuts with **zero**
false positives across 65 shipped windows — a precision instrument, used as such.

## 3 · Candidate generation — `plays.highlights_from_plays`

Most of the selection logic lives here. For each candidate window:

```
vision.ball_track            YOLOX, sparse sampling
  vision.shot_window         release / arrival / make
    _rim_run                 WHICH ball flight is the finish
                             (records its own decision: rim | nearest | longest)
      _ball_high             which ruler admits a sample
        _rim_admit           a sample the RIM measures at a hoop is rim-height
                             whatever the frame fraction says — PROMOTION only
      rim.rim_at             the rim BETWEEN two detections, interpolated:
                             never extrapolated, never across a gap wider than
                             0.75s, never across a jump larger than the rim's
                             OWN WIDTH
    flight_clearance         carry vs shot
carrier_evidence             a player is at the ball                    GATE
all_carries                  nobody ever shot                           GATE
min_setup                    the anchor is outside its own shot         GATE
```

The gates are asked in a specific order for a measured reason: `min_setup` asked first
was credited with ten drops that `carrier_evidence` actually makes.

## 4 · Selection and ordering

`HF.select` takes roughly thirteen candidates subject to a minimum gap between picks
and a per-kind cap, then orders them. Candidates carrying a known defect are demoted by
a **debt** — an amount that exceeds every score in the pool by construction, so the
demotion is an *order*, not a weight:

| debt | fires when | ships anyway if |
|---|---|---|
| `CROP_DEBT` | the crop failed on this play in a previous render | nothing else can fill the slot |
| `DUP_DEBT` | this play is already in the reel from another angle | nothing else can fill the slot |
| `SPANS_CUT_DEBT` | the window still passes through a camera change | nothing else can fill the slot |

The third one used to be a **deletion**, inherited from an operator ruling about a
single reel. Measured across the corpus it was refusing **35 of one reel's 54 action
candidates — 65% of its supply** — for a defect the release gate does not even score.
Converting it to a debt at half the duplicate's weight is derived from the gate's own
verdicts: a repeat is a hard reel-level failure, a camera change inside a scene is not
a gate item at all, therefore `clean > two-angle > the same play twice`.

## 5 · Beat-fit allocation

Scene lengths are whole beats. The hero scene's start is solved **backwards** from the
requirement that the make lands on the drop, and the run-in pays for it. A clip whose
ceiling is under the shortest legal window can never be placed, so it is dropped before
score and gap caps are spent — not slowed down to fit.

A clip is never squeezed to reach a slot. Where extra time is needed, the pipeline uses
the clip's **own footage after the basket, inside the same shot, at 1.0×** — which is
what lets a short finish fill a bar without a speed ramp that reads as a mistake.

## 6 · Gate swap

Before rendering, any scene whose window is known-defective may be swapped for a spare.

⭐ **"Last resort" means something different in a swap.** In allocation, an unfilled slot
means no reel at all, so a debted candidate has a genuine last resort and should be
taken. In a swap the slot is *already filled* — so there is none, and the honest move is
to decline and keep the incumbent with its known defect. Debted spares are therefore
withheld from the swap **before** the candidate pool is built, not filtered inside the
comparison, and a test pins the order of those two statements because putting it in the
wrong place left the rule in a branch nothing reaches.

## 7 · Render

9:16 with a subject-tracked crop, retimed to the beat grid, mixed against the authored
track with a fixed audio chain. The crop's subject prior fades scene-wide as ball
identification weakens, rather than snapping between players mid-scene.

## 8 · Grade

The release gate — see [METHOD.md](METHOD.md), section 1.
