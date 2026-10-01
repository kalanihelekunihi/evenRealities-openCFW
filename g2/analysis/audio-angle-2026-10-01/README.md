# PCM lag to app-visible angle

The stock angle field is a quantized cross-correlation estimate, **not a
validity or sound-presence flag**. In the tested stock instructions,800 zero
samples per channel produce **-90 degrees**. This batch replaces the correlation
stub in the recent metadata analysis with original correlation/clamp/conversion
instructions; only the final `asin` provider uses host mathematical evaluation.

## Scope selection and prior work

The historical display-port and display-driver-manager audits at commit
`832137ec` (`g2/docs/research/lvgl-ambiq-display-port-closure-audit.md` and
`g2-displaydrv-manager-recovery.md`) already describe complete recovered
implementations and behavioral tests. Repeating them would add little knowledge.
The requested fallback was therefore used: audio DSP metadata production.

`g2-service-algo-recovery.md` at that same commit also already describes this
algorithm. This is **not a claim of discovering a previously unknown DSP library**.
The bounded new deliverable is original-instruction validation of the specific
PCM-to-angle boundary that our recent audio/ESS tests stubbed, including its
app-visible silence ambiguity, exact constants and lag sign. Historical source
closure claims do not imply the current whole-image source/equality gates pass.

## Provenance, ABI and behavior

Official `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, SHA256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`;
runtime address=file offset+`0x437fe0`. Seven body hashes and disassembly are
saved with13 passing cases in `validation.json` and `disassembly.txt`.

Call chain: preprocessing splits stereo PCM → `service_algo_source_angle`
`0x591ba4` → cross-correlation `0x5918cc` → delay-to-angle `0x5918b0` → clamp
`0x59188e` → `asin` `0x43c260` → wrapper truncates signed degrees.
The prior metadata batch establishes export as signed16LE at value offsets202–203.
This batch does not re-run the packet queue or codec.

General correlation ABI recovered from instructions (Ghidra's prototype loses
the floating arguments): r0/r1=two int16 arrays, r2=sample count, r3=max lag;
d0=sample rate, d1=spacing, d2=speed, d3=RMS threshold, d4=quality threshold;
stack pointers+0/+4/+8/+12 receive angle radians, delay, quality, maximum RMS.
Optional output pointers may be null. Main wrapper uses:

| Input | Stock value / evidence |
| --- | --- |
| First/second arrays | `0x20375400` / `0x20375a40`, pointers at `0x591cf4` / `0x591cf0` |
| Sample count |800, set at `0x591bce` |
| Lag search | -10…+10, set at `0x591bb8` |
| Sample rate |16000.0, literal `0x591ce8` |
| Spacing parameter |0.14, literal `0x591ce0` |
| Speed parameter |343.0, literal `0x591cd8` |
| RMS / quality thresholds |0.0 /0.0, loads `0x591bbe` / `0x591bba` |

343 and0.14 are consistent with sound speed and microphone spacing in SI units;
these are **algorithm constants**, not measured microphone separation or acoustic
calibration. At16000 samples/s,800 samples represent50ms; no scheduler cadence
is established here. Physical left/right orientation and polarity remain unknown.

For positive lag k, correlation is `sum(left[i]*right[i+k])`; negative lag
uses `sum(right[i]*left[i-k])`. It is an unnormalized signed dot product over the
overlap, accumulated in signed64-bit integers. Scanning starts at -limit, and
only a strictly greater result replaces the best lag. Ties select the earliest
lag. A nonpositive supplied limit defaults to8; the stock wrapper supplies10.

Maximum RMS is `max(sqrt(sum(left²)/n),sqrt(sum(right²)/n))`.
Quality is `best_correlation / (mean(abs(correlation_per_lag))+1e-12)`, or0 if
the mean is zero. This is not a probability: the isolated-impulse tests produce21.
Neither quality nor maximum RMS is exported by the angle wrapper.

Delay is `best_lag/16000`; angle is
`asin(clamp(delay*343/0.14,-1,1))`. The wrapper multiplies by180/pi, truncates
toward zero using VFP `VCVT.S32.F64`, and narrows with `SXTH`.
Tested lag→degree pairs: -10→-90, -3→-27, -1→-8,0→0,+1→8,+3→27,+10→90.
The formula saturates from absolute lag7 onward, since one lag step multiplies
by0.153125 before arcsine. Boundary lag7 is inferred from the formula, not a
separate executed test. The estimate has integer-lag quantization.

## Silence, rejection and app implications

Silence yields RMS0, all correlations0, quality0. Zero thresholds accept both
metrics; tie-breaking selects -10, giving clamped angle -pi/2 and exported -90.
This was tested through the original wrapper as well as the general helper.
Thus -90 may represent silence or a saturated negative lag. It is not an invalid
sentinel;0 degrees is also a legitimate estimate and cannot serve as a sentinel.

General helper tests with positive thresholds show rejection: insufficient RMS
sets angle/delay NaN and quality0; insufficient quality sets angle/delay NaN and
retains the measured quality. n<=0 sets angle/delay NaN and quality/RMS0.
These branches are original instructions, but the normal wrapper's zero
thresholds do not reject silence. NaN-to-int behavior for exceptional wrapper
inputs is not established by these cases.

Applications should treat the angle as advisory metadata, not an independent
speaker-presence detector or confidence score. The separate exported energy
ratio is also not this RMS/quality value (see the prior ESS metadata batch).
A future protocol extension could expose validity and confidence explicitly;
this batch proposes no firmware patch or wire-format change.

## Validation limits and reusable artifacts

`verify.py` executes original quiet-NaN, clamp, delay, correlation, wrapper,
signed64-to-double and nonnegative-sqrt instructions. `asin` is an explicit
`math.asin` stub: numerical equivalence of the firmware's full transcendental
implementation is not claimed. All inputs are synthetic, not golden microphone
captures. Unicorn uses Thumb mode without MCLASS because its MCLASS model rejects
double-VFP execution. No radio, DMA, scheduler, acoustic scene or hardware timing
is simulated. The negative-sqrt errno path is outside the tested input domain.

`angle.pseudocode.c` and `angle_model.h` are a manually reconstructed offline
model with fixed stock constants, not firmware replacement code. C11 compilation
with `-Wall -Wextra -Werror` and `test_model.c` passed. Model handling of finite,
bounded normal inputs is intended; it does not reproduce arbitrary integer
overflow, invalid pointers or every IEEE exceptional behavior.

No new physical understanding should be claimed without paired microphone
vectors with known source direction and channel orientation. Those vectors are
the precise next input for acoustic validation; no additional bookkeeping or
firmware flashing was performed. See [the cumulative index](../README.md).
