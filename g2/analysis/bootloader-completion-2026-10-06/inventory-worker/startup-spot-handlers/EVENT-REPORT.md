# Startup event callback branch

This follow-up covers the nearby stored event hooks that were not among the four initial callbacks in [REPORT.md](REPORT.md). The locked image is unchanged: SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, Thumb load address `0x410000`.

The `native_events.c` fixed-address C models were compiled as an isolated Cortex-M33 ELF and compared with the stock callbacks in Unicorn. The 55-case suite passes while recording return values, ordered MMIO writes and final MMIO/RAM state. The event/state handlers, `42cea4` critical wrapper, `42cdf8` state adjustment, `41f3f0` power predicate, critical-save assembly, and delay-math assembly execute natively in both runs.

| Entry | Bound | Direct calls | Observed contract |
|---|---:|---|---|
| `0x42d562` | 96 B `[d562,d5c2)` | `42cfe0`, `42ced8`, `42d104`, `42d3bc` | Selector 0 invokes `42cfe0` only for non-null state with first byte 2. Selector 2 dispatches the state pointer to float-range update `42ced8` and returns its status. Selector 1 chooses `42d3bc` for state byte 0 and `42d104` otherwise. Other low-byte selectors return 0. |
| `0x42ced8` | 264 B `[ced8,cfe0)` | `42cea4` | Classifies the input float into range buckets around −273, 35, 50 and 1000, writes the selected range endpoints into words 1 and 2, and requests critical state update for valid buckets. Invalid values zero both endpoints and return 1. |
| `0x42cfe0` | 274 B `[cfe0,d0f2)` | `41f3f0` | When enabled, handles event kind 2 directly; otherwise queries the power predicate and scans 16 channel words with the active bitmap. It sets the result byte based on the observed encoded channel classes or power state. |
| `0x42d104` | 696 B `[d104,d3bc)` | `41d1c0` | Updates timer/state and SPOT control registers. Mode 3 performs delay calls of 5 and 10 units and selects settings from the state byte and BL009 flags; other modes take the alternate register/delay path. |
| `0x42d3bc` | 422 B `[d3bc,d562)` | `41d1c0` | Initializes the same register families. Mode 3 delays 5 and 10 units and configures the baseline values; other modes restore saved values. |
| `0x42d5c2` | 10 B `[d5c2,d5cc)` | none | Sets byte `0x200271b6` to 1 and returns 0. |
| `0x42d5cc` | 44 B `[d5cc,d5f8)` | `41b8ec`, `42cdf8` | Saves interrupt state, conditionally adjusts state from byte `0x200271b9`, clears bytes `0x200271b7` and `0x200271b6`, restores PRIMASK, returns 0. |
| `0x42d63a` | 88 B `[d63a,d692)` | none | Initializes autoswitch timer registers: clears control bits 8–12 and sets 16–31 to 1000 at `0x400211a0`; writes 0, 800, 450, 600 and 250 to `0x400211a8`, `a4`, `ac`, `b4` and `bc`; clears control bits 0 and 1; returns 0. |

These three table entries were not recorded as function entries by the Ghidra function index. Their ranges above are separately bounded from the entry instructions through the return instruction and authenticated against bytes in the locked image. `evidence.json` includes their exact hashes and bounded instruction listings in `stock-disassembly.txt`.

The current 72-case suite exercises dispatcher selectors, event-state branches, direct and dispatched range handling, exact float32 neighbors around −273, 35, 50 and 1000, signed zero, NaN, infinities, power predicate, channel scan classes, both mode branches in the register handlers, state-adjustment correction/no-correction cases, and the three stored callback entries. The receipt records stock entry addresses reached per case. `42ced8` has complete instruction-byte visitation (264/264); `42d104` (612/696) and `42d3bc` (310/422) remain partial. Complete byte visitation is not proof every possible input was tested. In `42cdf8`, the correction gate is bit 18 of `0x40021004` (as shown by the stock `UBFX` instruction), plus a nonzero byte at `0x200271b4`.

The prior 55-case receipt is superseded for range conclusions. Its harness loop unconditionally replaced dispatcher state pointers with `DATA+0x100`; selector-2 cases therefore read the zeroed state-byte fixture instead of the float tuple at `DATA`. The output words were written outside the reported float snapshot, so those apparent passes did not test the range result. The reproduced inert results are marked `SUPERSEDED` in [events-comparison-55-superseded.json](events-comparison-55-superseded.json), with the reproduction limitation documented in [events-comparison-55-superseded.md](events-comparison-55-superseded.md). The corrected harness leaves caller-provided/default pointers intact and includes direct `42ced8` cases alongside selector-2 dispatcher cases. `42ced8` produces the expected return/endpoints for finite boundaries and returns 1 with zero endpoints for NaN and out-of-range values; source NaN classification follows the stock unordered `VCMP` branch behavior.

The comparison cuts only these lower dependencies:

* `platform_control/critical_save.S` is linked into the source ELF and compared directly against stock instructions at `0x41b8ec`; PRIMASK behavior is included in state comparison.
* `platform_startup/delay_math.S` is linked into the source ELF and compared directly against stock `0x41d1c0` math and FPU effects. Its resident ROM cycle call at Thumb address `0x40` is the only cut: both paths record the passed cycle count and return immediately. The comparison makes no elapsed-time or physical clock claim.

No peripheral acknowledgement, physical timing, source integration or complete OTA dependency closure is claimed. Hashes for each stock body and for the locked image remain a prerequisite for regenerating the comparison; run `verify_evidence.py` before `compare_events.py`.
