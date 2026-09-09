# Method — how a pipeline with no ground truth is kept honest

> A generative pipeline that grades itself converges on whatever its own metrics
> reward. Everything here exists to stop that.

## 1. The release gate

`check_scenes` grades a finished render against nine checks. It is deliberately built
so that it **cannot consume the pipeline's own reasoning** — the planner's
`make_seen`, its palette shot list and its release estimate are exactly the numbers
under test, so their agreement is not evidence.

| check | asks | sourced from |
|---|---|---|
| `semantic` | is this window a scoring play at all, or a huddle? | truth |
| `continuity` | does a human-confirmed camera change lie inside it? | pixels |
| `phase` | are load-up, decisive act and result all present? | truth |
| `crop` | does the 9:16 crop hold the featured player through each phase? | truth |
| `handoff` | is the featured player in a valid role — not a defender, not a bystander? | truth |
| `payoff` | is the result legible on screen? | truth |
| `repeat` | are two scenes the same play from different angles? | pixels |
| `density` | at most one non-action scene, never two adjacent | truth |
| `duration` | does the cut actually cover the authored track? | music |

**`UNKNOWN` is not a pass.** A window nobody has looked at is `UNKNOWN` by
construction, and the gate refuses the reel until someone looks. This single rule is
what stops the truth set from being quietly gamed by selecting footage that has never
been judged.

## 2. Ground truth as a regression fixture, not a report

The ground-truth file holds 220 adjudicated scene records — a human's
reading of specific frames, keyed by **reel and source window** so that any future
render which re-selects overlapping footage inherits the judgement automatically.

It is not a report. It is *load-bearing at plan time*: a window judged defective is
screened out of selection, and a crop defect becomes a debt. One bad predicate over
this file once made 23 of 56 adjudicated real plays permanently unselectable. That
blast radius is why the file has an audit of its own:

* **Every record must carry a provenance stamp** — `by`, `evidence`, `at`. A judgement
  with no answer to *"what was actually in front of the judge's eyes?"* cannot be
  overturned honestly later, and three records already have been.
* **`truth_audit --boundaries` catches the AI adjudicator's one systematic failure.**
  Every wrong record so far made the identical mistake: describing footage that lies
  across a shot boundary the judge did not notice, so the "finish" being described is
  in the next take — a different game. The audit takes the union of the judged window
  and every source timestamp the record's prose cites, and refuses any record where a
  verified boundary sits inside that span *undeclared*. It ships with a fixture that
  proves it still fires on the known-bad record.
* **A truth record may screen a WINDOW; it may never excuse a RENDER's mistake.** Those
  are two different predicates — "is there anything here worth cutting again?" versus
  "did this render ship a defect?" — and collapsing them into one deleted 41% of the
  adjudicated real plays.

## 3. Declared control arms

Every render batch is written down **before it runs**, with a prediction per arm, and at
least one arm is a control that should come back byte-identical.

This is not ceremony. On one change, three declared controls failed in a row, and each
failure found a *different* real defect — none of them the one the change was aimed at:

1. The gate swap read `score` as its **third** sort key, so every "debt" in the system
   was silently behaving as a weight. A demoted candidate at −494.767 was still being
   seated over a clean one, because it fit 0.1s better.
2. The debt-counting helper used a **floor**: `−494.767 // 500 == 0`, so the ordering
   fix was inert on exactly the candidates it was written for. That one was caught by a
   *test*, not a render.
3. The new rule sat in a branch nothing reaches — the swap is decided at a pure score
   argmax above everything that had been patched.

A byte-identical render on a *declared control* is a pass. A byte-identical render on a
change is a failed session.

## 4. The three traps

Most rejected ideas in this project are one of three mistakes wearing a different hat.

**1. The frame is not a ruler.** Every threshold expressed as a fraction of the frame
has failed to generalise; every one expressed against an object *in the scene* — a
body, a rim, a bounding box — has held. Broadcast footage changes zoom constantly, so
"the ball is above 0.42 of the frame height" means something different every shot.
"The ball is within 1.5 rim-widths of the rim" does not.

**2. A dunk's ball is invisible exactly when it matters.** It is occluded in the
hands from gather to flush — precisely the interval you want to measure. So **rim and
ball evidence may PROMOTE a candidate, never GATE one.** "No ball was seen" is
ignorance, not evidence. The one legitimate gate of this family is "every flight in
this window was a carry", because that *is* a positive observation.

**3. Never verify against a list this codebase derived.** Pull the frames and look.
When a document disagrees with the footage, the footage wins — and that includes the
ground-truth file itself, which has been overturned three times by its own project.

**And the corollary that cost two sessions:** *pull the frames at the rate the thing
you are asking about moves.* A ball passes a 24fps rim in 3–5 frames. A contact sheet
sampling every 0.25s sees it zero or one times, and a session then writes "the result
is not establishable" about the **footage** when the true statement is about the
**contact sheet**.

## 5. Put the number in a script

Three claims made in a chat message did not survive being counted — *"finish evidence
of type X is 97% bad"*, *"ten windows end before the ball resolves"*, *"twelve failures
became two"*. A number in prose cannot be re-checked; a number in a script can be
re-run against a changed pipeline a month later.

There are 27 `probe_*.py` scripts in the repo for that reason. Each one was written
the moment a claim needed to survive being wrong.

## 6. What "done" means here

The standing rule for a working session:

1. End with **rendered reels someone can watch** and a stated BEFORE → AFTER on
   numbers the operator recognises — green scenes, body widths, output seconds. Not
   AUC, not byte hashes, not candidate counts.
2. A byte-identical render is a **failed** session unless it was declared a control
   before the batch ran.
3. **Refuting an idea is not a deliverable.** It buys the next candidate in the same
   session; it does not end the session.
4. Do not close with the defect register longer than you opened it unless you also
   shipped a measurable improvement.
