# Independent touch gesture machine and composed report closure

New [canonical offline source/header](../../components/touch/gesture_machine_offline/README.md) reconstructs `0x4070..0x43da` and attention rearm `0x3afc`. The standalone native module composes independently validated speed and software delay source and has **no borrowed executable firmware calls**. The prior sealed calibration module remains unchanged; selected source-defined guest sections replace its original gesture target for composition tests. No production firmware, shared state, index, device or commit changed.

## Recovered interface and state

Input: active 0/1, position byte, delivered SysTick callback counter. Nonnull output is a pointer to three event bytes at state +77. Each step clears those bytes, copies current sample +12 to previous +4, and installs the new sample. Null state returns null. Zero hold threshold becomes 1000.

`gesture.h` supplies the 80-byte layout with compile-time size/offset assertions: threshold +0; previous/current/press-start samples +4/+12/+20; elapsed +28; tap count/pending +32/+33; release/motion counters +36/+40; motion anchor +44; three speed samples +48; index/count/filter/direction +72..75; mode +76; output +77..79. Counter differences preserve unsigned modulo-32 arithmetic. Direction/position differences are signed arithmetic on bytes.

| Event flag | Actual trigger |
| --- | --- |
| `01` | New active press; speed history resets and press/motion anchors are installed |
| `02` | Release, including releases after hold or drag |
| `04` | Pending single tap after idle **>300** counts; payload byte is tap count |
| `08` | Added to the second short release, producing `0a 02 00` |
| `10` | Stationary hold when elapsed >= configured threshold and displacement <=24 |
| `20` / `40` | Negative / positive motion; payload distance and filtered speed |

A press joins the pending tap sequence if the release gap is **<=300** counts; count saturates at 255. A short release is elapsed **<300**, and marks a pending tap. Release at exactly 300 does not. After timeout, counts 2–4 emit no new flag; count 1 and synthetic counts >9 emit `04`. Counts 5–9 after idle >300 instead clear tap count and invoke attention rearm. Thus tap handling is not a general count-to-event mapping.

Initial movement enters drag mode at displacement **>24** from press position. It clears tap state even if rate limiting suppresses that first event. Motion emission requires **>99** counts since the last motion anchor. Later drag updates require displacement **>14** from that anchor and the same rate limit. A drag release can append motion to release (`22` or `42`) when final displacement >14, without the held-update rate check. Distance is absolute displacement; speed is the validated filtered byte.

Hold sets mode 2 and clears tap state. Later movement is ignored until release; hold release resets mode/tap state and emits only `02`. The mode byte is explicit; direct synthetic mode 3 matches stock fallthrough but is not claimed normally reachable.

Attention rearm writes GPIO offset +0x44 = 2, executes software-delay argument **200**, then writes offset +0x40 = 2. Both original and reconstructed delay loops execute with reset scale 24000; no physical duration, GPIO level or hardware effect is inferred.

## Validation

Standalone ELF SHA `7bb9c18a96194f0d180947fecab8f4471a538c09f3fcb876e1fc6fd47801fc04`.

| Suite | Result | Scope |
| --- | --- | --- |
| Machine original/native | **4,373 PASS** | All **874/874** original instruction bytes visited; no function-entry cuts |
| Sequential gestures | 10 sequences, 50 steps PASS | Single/double/late taps, hold, positive/negative drag, wrap, release299/300, five-tap rearm |
| Reset contract | 4 PASS | Zeroed state with parameters0/1/1000/65535; first press matches |
| Negative controls | 4 rejected | Motion at24, rate at99, tap window excluding300, hold after rather than at threshold |
| Composed report/calibration | **336 PASS** | Original versus independent gesture/speed/delay plus native report/storage code |
| Composed command/deferred/report | **8 sequences PASS** | Command7 parameters0/1/1000/65535, calibration pending during idle, hold and wrap |

Direct fixtures vary mode, prior/input activity, elapsed boundaries, position boundaries, pending tap, counts and PRIMASK. Unsupported input2, synthetic modes/count combinations and timestamps are explicit tests, not evidence of normal scheduling reachability. Complete state, return pointer, GPIO writes, SP and PRIMASK compare. Software rearm loops execute; SysTick/ADC/IRQ concurrency is not modeled. Original helper memory/division/logging instructions execute; native module is independently linked source.

Selected-section `fixture.ld` puts native step at `0x4070` with a size assertion and support at `0x110000`. The composed harness loads only selected sections, excluding ELF segment padding. This is isolated source substitution in guest memory, not a firmware patch or byte-identical image. SROM requests/storage writes and sensor structures remain synthetic external effects. No analog scan or hardware durability claim.

## What composition establishes for CFW interfaces

Command7 with parameter1 prepares `07 00 17` while the old gesture threshold remains1000. Actual deferred processing then clears/reinitializes state and installs threshold1; subsequent stationary hold emits at one callback count. Parameter0 prepares `07 ff 17` and does not restart state. Parameter65535 installs65535 without narrowing validation. This ACK/reset/persistence order is now compared through actual command and deferred instructions.

Calibration can remain pending during idle because report processing returns without an event. When the next press emits a report, baseline1000 is updated to1050, but that frame's saved-baseline field remains1000; a later frame carries1050. The same behavior survives independent gesture/speed composition.

No-event steps clear gesture output but do **not** replace TX. Sequential report traces retain the previous16-byte frame until a new report is emitted. Repeated polling of those bytes alone is not evidence of new events; application/CFW logic needs the established notification/consumption protocol. Electrical notification timing and transport delivery are not measured here.

Hold thresholds remain delivered SysTick callback counts. The prior counter setup proves `clk_lf`, reload40 and increment callback installation; it does not establish physical milliseconds or uninterrupted counter delivery. The 640 report countdown is likewise not a duration claim.

## Remaining actionable source leads

The gesture executable dependency is closed for this bounded state domain. The next concrete gap is upstream CapSense scan/post-processing that produces widget activity, position and sensor raw/baseline/difference values, plus LF-clock setup if a physical timing interpretation is required. Existing SDK evidence identifies query layouts but does not yet recover their analog producer or uniquely identify the producing revision. No external input blocks further bounded static/source-family analysis; physical sample, cadence, IRQ and SROM conclusions still require wider closure or actual captures. No global dependency exhaustion or whole-firmware source-completeness claim.
