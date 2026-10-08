# PCM2.1 reset recovery

Stock **0x5A1DA4..0x5A1DF4** now has [native C](../../components/audio/pcm21_reset_offline/reset.c) and [interface](../../components/audio/pcm21_reset_offline/reset.h). Exact ELF `105035edc6bd3e1019ad54d21e7b3932c350a02d59023e6b16c66570280fce01` passes **7,720 comparisons**:200 reset cases plus7,520 earlier-family regressions rerun against this build. [Validation](exact-build-validation.json), [reset results](reset-results.json), [build](build_offline.py), [original instructions](disassembly-evidence.txt), [byte/OTP bindings](function-bindings.json).

Reset requires both device/audio power-status words to be zero, enables OTP peripheral29, requests **temperature−40.0** via0x480028/generic control0x480312 (action2,enable0), then waits for0x400083E0 bit0 to clear through the2500-unit microsecond wait API. Prerequisite/enable/temperature errors return1, wait failure returns4 and clear timer returns0. This differs from SDK5.1.0's BACK_TO_DEFAULT_STATE stimulus. Returned temperature bounds are discarded.

The OTP descriptor0x6BECB0+29×16 binds enable0x40021004 and status0x40021008 to mask0x08000000. Tests supply an explicit synthetic ready response to the enable write or leave it unready. Final wait fixtures clear the timer on wait-read1/3 or never release it. The real enable/wait/delay functions execute; no external-call return stubs are used. These events are deterministic simulation, not hardware traces or physical elapsed-time measurements.

Native reset registers reconstructed PCM2.1 control; stock reset registers original control. Both traverse actual temperature/generic wrappers and their corresponding power-control families. Cases cover missing callbacks, invalid signature, inactive buck, masks0/1 and pending timers. Status distribution: `{"0": 68, "1": 116, "4": 16}`.

Generic control returns0 with an absent callback. The temperature wrapper then copies stack bounds no callback populated; reset ignores them. Success therefore does not prove a registered handler ran or meaningful bounds exist. An error can follow operations that already changed power state; reset is not atomic rollback.

## Continuing source-backed leads

Existing pinned source inspection identifies PCM0.7 GPU on/off0x59FBAC/0x59FCA2 and PCM2.0 GPU on/off0x5A0328/0x5A05E0 via public functions and sealed outer bindings. PCM2.0 sleep/temperature0x5A0204/0x5A00FC remain actionable. [Pinned paths/hashes and new lead mapping](source-reference.json). No new download was necessary; these files are already materialized. Source-exhaustion has not been reached. Stock planner/preparation/initializer SDK differences remain explicit in prior reports.

## Navigation and limits

- [Outer control](../audio-pcm21-control-closure-2026-10-08/REPORT.md): actions, temperature, inactive gate and deferred CPU state.
- [Four children](../audio-pcm21-children-closure-2026-10-08/REPORT.md): preparation/state-change/planner/apply.
- [Nine completion/lifecycle functions](../audio-pcm21-completion-closure-2026-10-08/REPORT.md): TON, boost, ISR and calibration.

Common hardware/wrapper providers still execute original bytes; this is not a fully source-built subsystem. Calibration/OTP/timer events are synthetic, startup SRAM/ITCM authenticated. Passive MMIO and M33-compatible function execution do not establish fullM55, hardware settling, real exception delivery or live task/IRQ quiescence. Earlier whole-system trace/calibration limits remain.

All1,279 prior seals (including the requested1,261),110 audit inputs,four checkpoints and root index were verified before new sealing. No commits, staging, production changes or device writes.
