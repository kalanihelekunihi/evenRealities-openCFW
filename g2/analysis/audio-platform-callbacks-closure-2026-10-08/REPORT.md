# Audio power callback closure and ITCM correction — 2026-10-08

The integrated callback reconstruction now passes **11,337 original-instruction comparisons against one exact ELF**, plus one complete OTA decompression-record comparison and one bounded original-only zero-count prefix trace. These are bounded offline behavioral comparisons, not firmware completeness, byte equality, live scheduling, or physical power/timing validation. [Exact build validation](exact-build-validation.json), [reproduction receipt](reproduction-receipt.json), and [reconstructed source](../../components/audio/platform_callbacks_offline/).

## Correction and stale receipt

The old 1,297-case `newer-results.json` receipt for ELF `ee89cc3ba58f21eb41b8beeb607926032f30f554d1bb8313128953ba71e6ddd6` was **invalid evidence for the subsequently integrated build**. It is superseded by the current 1,339-case result and exact-build validation. After the preparation helper was integrated, a comparison exposed RAM0x20074F6A=1 in C versus0 in stock. The original unsigned BHS at0x5A4B98 clears the flag outside profiles9..11; BEQ at0x5A4BA0 also clears it when the companion byte is7. The corrected predicate is:

```c
prepare_state(&request);
flag_20074F6A = ((current_profile - 9u) < 3u)
                && (companion_20004540 != 7);
```

The 42 new boundary cases cover profiles0,8,9,10,11,12,UINT32_MAX, companion bytes6/7/8 and both initial PRIMASK values, including wraparound under the original unsigned arithmetic. [Original branch disassembly](disassembly-evidence.txt) and `verify_newer.py` provide the evidence.

This report also explicitly supersedes the **mistaken missing-resident-ROM conclusion for addresses0x40 and0x48** in earlier sealed power/provider reports and the18:41 rescan. The sealed originals remain unchanged. OTA record0x75D3E4, callback0x43A11E, decompresses22bytes at0x79430E into24 executable bytes at0x40..0x58, SHA256 `0676154418085b0630f2a20cc50fbbe3967dd2d9b7794fe1aad3f6af14f2fb83`. Original decoder execution agrees with the independent decoder and guard checks, returning next record0x75D3F0. The previous unmapped-fetch observations were real, but caused by omitted runtime initialization. The consolidated memory map had already identified this record.

```c
/* Functional pseudocode; cycle-exact C is not claimed. */
ITCM_40(iterations) { do { --iterations; } while (iterations); }
ITCM_48(src, dst, words) {
    do { *dst++ = *src++; } while (--words);
    return src;
}
```

Positive count is the tested completing contract. A separate original-only zero-count trace demonstrates unsigned underflow and three copies before stopping; it does not execute a full wraparound or establish a hardware defect. Selected delay0..100 intended microseconds is exercised through actual initializedITCM40. Pinned HAL corroborates the intended unit; physical timing and extreme float-to-uint conversions remain outside validation.

## Recovered call flow and interfaces

| Original entry | Reconstructed behavior |
| --- | --- |
| 0x480434 | Reads chip revision4002000C, cached trim version200001E8, feature bit; computes variant flags; clears60-byte callback table20073270 and installs family entries; invokes actual selected initializer or returns0 |
| 0x59FD36 /0x5A0786 | Earlier-family action dispatch wrappers, with actual child-entry boundaries |
| 0x5A490C | PCM2.2 internal power update: SIMObuck gate40021108, signature1F01600D at2005665C, IRQ exclusion, request mutation, preparation/profile planning and apply handoff |
| 0x5A1E8C | Float Celsius classification: [-273,-20),[-20,0),[0,50),[50,1000); invalid including NaN/infinity |
| 0x5A45D0 /0x5A421C | Power profile/TON planning and CPU-state flag updates |
| 0x5A410C /0x48D620 | Deep-sleep activity preparation from temperature, peripheral/audio masks, auxiliary mode and16 enabled timer configurations |
| 0x5A4334 | Transition-table index selection, preserving one-byte enum output |
| 0x5A44BA /0x5A453C | Step/apply routing across profiles0..19; dispatches initialized table200002A8 |
| 0x4D3DDA /0x4D3F3C | INFO/OTP word-read address selection, limits/power checks and restricted wrapper |
| 0x5A4D48 /0x47EF38 | PCM2.2 calibration initialization and cached trim-version getter |
| 0x40 /0x48 /0x4807A0 | Runtime delay loop, word-copy helper, selected intended-microsecond delay conversion |
| 0x4801FC /0x480240 /0x48028A | Timer initialization/start/restart and common actual clock-request execution |

The internal19-byte request has little-endian uint32 masks at+0(dev),+4(audio),+8(memory),+12(SSRAM), then byte+16temperature range,+17CPU state,+18GPU request. Native C padding gives sizeof20. Action0CPU and1GPU use a byte; action2metadata is floatCelsius at+0 and hysteresis lower/upper float outputs at+4/+8. Action3device and4audio OR masks only when enabled;5memory assigns regardless of enable;6SSRAM assigns when enabled. Required missing metadata and actions>=7 return6. These are internalHAL actions, not BLE wire opcodes.

Temperature output overlaps use2°C hysteresis: [-273,-20],[-22,0],[-2,50],[48,1000], invalid[0,0]. The startup-data table has27 Thumb targets in the same ordered shape as the public PCM2.2 transition array; actual no-op entries24/25/26 execute. Nontrivial transitions and voltage control stop at actual child entry: successful returns are never fabricated. Their complete bodies are not validated by routing tests.

Timer setup writes CTRL0=0x110, auxiliary control0x100, both comparesFFFFFFFF, clearsC0000000 interrupt bits and enables40000000 interrupt mask. Start converts supplied duration by unsigned×6, enables timer15 global bit, toggles clear, enables NVIC bit40000 and timer enable. Restart disables, clears, updates compare, clears peripheral/NVICpending, then enables. Passive MMIO does not model peripheral side effects or IRQ delivery. Start discards the actual clock-request return; tests do not inject successful return stubs.

## Validation and dependency reuse

| Suite | Comparisons | Boundary |
| --- | ---: | --- |
| Registration/earlier control |456|168 registrations plus288 wrapper tests; selected original initializer/child entry |
| Integrated newer control |1,339|Independent classifier/planner/preparation/state setter; stop before apply |
| Classifier |41|Finite boundary/NaN/infinity float patterns |
| Planner/state setter |2,928|2,880 plans plus48 flag cases |
| Preparation/query |363|336 preparation plus27 auxiliary cases |
| Selector |400|All tested profile pairs0..19 |
| Routing |3,200|Actual initialized dispatch targets; selected no-ops complete |
| Read/init |2,376|Return or deliberately uninitializedITCM-entry boundary; negative fixture, not missing source |
| Trim getter |40|Cached/error or uninitializedITCM-entry boundary |
| InitializedITCM/provider |74|Includes completing calibration initialization and trim getter with explicit synthetic INFO/OTP words |
| Timer |120|Actual clock acquisition, passive timer/NVIC writes; no physical IRQ |

Every suite above was rerun after the flag fix and binds the current ELF hash. Main comparisons use a compatible M33 ARMv8-M subset/FPU where needed; they do not emulate the full M55 exception return. Calibration tests supply synthetic mapped words and execute actual read/copy/init instructions; no authentic device trim values are inferred.

[Official pinned source](https://github.com/AmbiqMicro/ambiqhal_ambiq/tree/5efc0228528a8adce5eae0d226fac85d2551eb3b/mcu/apollo510/hal) is materialized at the existing registered gitlink `third-party/upstream/ambiqhal-apollo510`, with no root index or.gitmodules change. [Source-reference hashes and bounded history search](source-reference.json). The earlier additional reference checkout remains untouched.

Two selected public leaf bodies—temperature classifier and transition selector—pass441 inputs in both default compact-enum and explicit-fshort-enums builds. Forced-fno-short-enums gives441 numeric agreements but400 selector-output footprint mismatches. This GCC default uses compact enums; this experiment does not establish historical compiler flags. License notice is retained in `public_leaf.c`. Public5.1.0 has extra stimuli7/8 and different temperature/trim initialization logic, so whole-module substitution is unsupported.

## Remaining useful work

The public PCM2.2 file supplies all27 registered transition functions and macro-expanded trim/cache/timer sequencing. The highest-value next bounded batch is an actual nontrivial transition plus its completion handler (sequence2/2b or7/7b), now that initializedITCM delays can run. Delayed timer completion and post-LP-to-HP sequence21b remain useful independently available source leads. Table correspondence is a candidate binding, not proof of27 body equivalences. The bounded fetched public history shows Apollo510 introduced at SDK5.1.0; no older Apollo510 source was found in that search. Dependency searching is not declared exhausted.

Authentic device INFO1/OTP calibration data is needed to establish the running hardware variant and trims. A coherent task/IRQ/timer trace is still needed to establish live quiescence and ownership ordering; no owned-buffer firmware patch is justified by these synthetic tests alone. Dirty filesystem I/O and full exception-return behavior remain separate prior boundaries. No production firmware, shared campaign, commits, index, or devices were changed.
