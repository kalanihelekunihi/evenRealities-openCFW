# PCM2.1 TON, delayed completion and lifecycle recovery

Nine additional native functions now have readable [TON/boost/ISR C](../../components/audio/pcm21_completion_offline/completion.c), [calibration/lifecycle C](../../components/audio/pcm21_completion_offline/lifecycle.c) and [interfaces](../../components/audio/pcm21_completion_offline/completion.h). Exact ELF `dc9b50dd77deccd294ff47907da4a3fcecd92cb633932e8836be4f7da8f56363` passes **7,520 comparisons**: 1,336 outer-control cases, 3,146 previous helper regressions and 3,038 new-function cases. [Exact-build validation](exact-build-validation.json), [reproduction](build_offline.py), [new tests/results](completion-results.json), [stock byte bindings/static callback chain](function-bindings.json), [annotated original instructions](disassembly-evidence.txt).

|New native function|Stock address|Direct cases|
|---|---|---:|
|TON|0x5A0D9C|2640|
|Timer publication/core boost|0x5A0AE8|75|
|Memory/core boost removal|0x5A0B54|225|
|Buck target completion|0x5A0B9C|20|
|Timer ISR|0x5A0BCC|48|
|Before override|0x5A1BBC|6|
|Before enable|0x5A1BCC|6|
|After enable|0x5A1BEC|6|
|Calibration initialize|0x5A1C18|12|

## What the functions do

TON temporarily increases core trim by14 and memory trim by6, capped at1023 and63. It delays20 through the shared microsecond API, sets two rail-switch controls, delays20 again, updates TON fields, clears those controls, then subtracts the exact temporary increases. Selector0/1 use packed STM fields,2/3/4/5 use GPU fields,6 uses default fields, and7 reads live fields. Other selector values fall back to selector5; no error return is exposed. Profiles8/12 replace VDDC TON with special packed fields; profiles14/15 add6/12 and saturate to31. Profiles1/5/17 select low-voltage TON4; others select6. Live selector7 reads VDDF from0x40020354 but writes the selected field to0x40020358; those addresses must not be conflated.

Timer publication narrows its argument to a byte. A nonzero argument enables two memory-LDO controls and installs boosted memory trim from calibration word0x200566C4 bits14..19. It always boosts core by7, capped at1023, recording the actual increment at0x200742C8. Boost removal always restores memory trim (bits2..7) and the two control bits from the calibration word. Core subtraction is conditional on its byte argument. Tests include arguments256/257 and modular subtraction; synthetic malformed states are not asserted naturally reachable.

Buck completion restores target VDDC/VDDF from0x200742CC/0x200742D0 only when flag0x20074F69 is zero. The timer ISR saves PRIMASK, invokes buck completion, conditionally sets CPU/AOR overrides when switching flag0x20074F6D is set and profile is neither8 nor12, clears that flag, calls real timer stop, removes memory/core boost, and restores PRIMASK. Direct tests verify mask0/1 and both exceptional profiles. The previously recovered apply cancellation calls boost removal with0 because core was already explicitly updated; ISR removal uses1. This is an important difference for offline patch reasoning.

Stock callback registration installs0x5A0BCD in slot11 at0x2007329C for the PCM2.1 silicon/revision branch. Existing authenticated vector/static wrapper evidence links IRQ82 through0x4D58A6 and0x48039A to that slot. This identifies the static route; direct ISR calls are not proof of real NVIC delivery, runtime VTOR or live timer scheduling.

## Calibration and SDK differences

Initialization reads16 INFO1 profile words, derives profiles16..19 by copying4..7 then replacing their low7 VDDC trim bits from12..15, reads four TON words and one memory-LDO word, adjusts selected profile8/9/12 fields, fixes the VDDF compensation field to31, stamps signature0x1F01600D and initializes the timer. If selected OTP is unpowered it returns7 before reads. Synthetic fixtures exercise both flash-shadow and powered OTP addressing plus that failure gate. The INFO1 reader and ITCM copy execute original instructions; no read-return stubs supply data.

Pinned public SDK5.1.0 additionally constructs profile20, reads L/E trim data, applies a minor-trim-version correction and updates analog-LDO controls. Those paths are absent from this stock initializer. Its stock special-profile low7 replacement also differs from the public VDDF-field replacement. Therefore upstream initialization cannot be copied wholesale. The previously documented stock planner rejects unknown-temperature combinations instead of choosing SDK profile20; preparation tests range3 only rather than the public additional invalid/unknown-temperature cases. One initial reconstructed profile9 source offset was caught by the full calibration comparison and corrected before all final suites were rerun.

Before-override installs low-voltage TON6. Before-enable installs profile7 core trim only with a valid signature. After-enable restores memory trim/control fields only with a valid signature and returns0; the public SDK's broader enable/wait/state-init behavior is not this stock callback.

## Continued concrete source lead

Stock reset0x5A1DA4 is still a source-backed native-recovery target. Its actual pseudocode is:

```c
if (device_power_status || audio_power_status) return 1;
if (peripheral_enable(29) != 0) return 1;
if (temperature_request(range_output, -40.0f) != 0) return 1;
if (wait_status(2500, TIMER_CTRL0, 1, 0) != 0) return 4;
return 0;
```

Wrapper0x480028 builds a12-byte temperature argument, calls generic control0x480312 with action2/enable0, and copies the two range bounds or zeros them on failure. This is instruction-backed static interpretation, not a native reset test. The SDK instead invokes BACK_TO_DEFAULT_STATE; stock outer control does not support that SDK stimulus. OTP enable, generic callback state and timer completion require explicit fixtures when testing reset.

Existing pinned PCM0.7 and PCM2.0 files remain useful for initialization, GPU/Ton, suspend/postpone and reset bodies; earlier outer wrappers do not close those families. [Source hashes and remaining leads](source-reference.json). No new source download was needed, and no source-search exhaustion is claimed.

## Limits and preservation

The final executable links13 native PCM2.1 helper/completion/lifecycle bodies plus the earlier native outer control and classifier. Common timer-stop/start/restart/init, cache, delay, IRQ-save and INFO1 providers still execute original code. Profiling NOPs' stack-only packing is omitted. Tests compare relevant calibration/global SRAM, ordered MMIO writes and common-provider arguments; they do not compare all scratch registers or every stack byte.

INFO1/OTP words are deterministic synthetic inputs, not authentic device calibration. Startup SRAM/ITCM are authenticated. Passive MMIO and the M33-compatible instruction/FPU model do not establish physical settling, full M55 behavior, live RTOS/task quiescence or architectural interrupt exception delivery. No safe hardware-patch or full-source/byte-identical claim follows.

All1,261 prior seals,110 audit inputs,four checkpoints and root Git index were verified before new sealing. No commits, staging, production changes or device writes.
