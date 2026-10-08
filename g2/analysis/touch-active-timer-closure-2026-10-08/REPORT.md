# Active intervals, launch consumption and application budget semantics

**1,160 cases pass**:240 three-way original/independent/public timer-setter comparisons,4 three-way null-context cases,900 original/source active-launch cases,4 LP→active timer/ISR/reuse sequences and12 successful state1 budget-tail cases. No function-entry stubs. Versioned source ../../components/touch/active_timer_offline/{timer.c,active.c,timer.h} independently reconstructs5d90,6bd4 and the selected state1 tail.

## Units and conversion

5d90 is **active-mode ConfigureMsclpTimer**, not the WOT/LP interval setter. Pinned CapSense247a... documents input in microseconds. Actual offsets are internal+28 desired active interval, +32 encoded timer cycles; LP/WOT interval/cache are separate+36/+40. Pinned structure definitions describe compensation+44 as ILO frequency(Hz)*2^14/1000000. Initializer supplies655 (0x28f), consistent with nominal40kHz scaled by2^14; no actual oscillator measurement is inferred.

The recovered/calculator5d70 does **32-bit wrapping multiplication**, shifts right14, subtracts1 if nonzero, then clamps to65535. The full setter returns1 only for null context; otherwise stores requested/cache and returns0 even when injected factor0 or arithmetic wrap yields0. Example interval65536 with factor65536 wraps its product to0. Boundary tests are supplied inputs, not valid physical calibration claims.

| Application request | Meaning supported by SDK | Cache with initial factor655 |
| --- | --- | --- |
|7773|desired active wait7773µs|309 (310 cycles before-minus-one encoding)|
|31211|desired active wait31211µs|1246 (1247 cycles before-minus-one encoding)|

These approximate128Hz and32Hz active rates by intended wait parameters. They are **not measured scan cadence**: actual ILO calibration, scan work, callbacks, sleep and application activity still matter.

## Setter gate and state transition

Setter stores interval/cache unconditionally for a valid coherent context. Only common status mask0x10 (active widget scanning) updates live AOS_CTL+0x70: clear low16, then OR cached active cycles; upper16 retained. LP status0x20 alone leaves hardware unchanged. There is no busy rejection, so injected active+busy states still update the live timer. Mixed0x30 is documented as a synthetic gate test, not an endorsed coherent state.

Application5d90 calls occur at3d0a (initial7773),3da2 (state1 budget reacheszero→state2/31211),3e12 (state2 detectsactivity→state1/7773),3e7a (LP signal→state1/7773) and3e98 (LP no signal→state2/31211). Literal words3ec0/3ecc contain7773/31211. Previous LP phase leaves LP status0x20 after ISR. Consequently its next active-interval setter changes the cache, not the LP timer. This is confirmed in four actual-pointer sequences, followed by active launch6bd4 consuming that cache.

## Active launch6bd4 and partial-state paths

Validate context!=NULL, nonzero count, first<=4 and unsigned last=first+count-1<=4. Coherent project tests bound allocated descriptors/frames; unsigned-overflow argument values are not a supported contract. Busy rejects0x40 before setting new busy state. Otherwise OR busy0x81 and clear repeat flagbyte115 **before** mode-switch errors can occur. An invalid mode can therefore return1 with busy retained; this differs from LP launch's mode-before-busy ordering.

Reuse is allowed only with prior configuration2/4, matching startu16+72 and loaded countu16+70, count<=21, no status0x2000 (public calibration label), and active status0x10. Synthetic configuration4 tests cover that branch; no claim of an application-installed configuration4. Any failed condition goes through the actual mode/GPIO/public-PDL dependency chain. Successful full setup replaces widget scan flags with0x10, sets operatingmode3, configures AOS timeout1 and cached active timer, writes CE_CTL0x80000000|internalbyte118, masks FRAME interrupt0x10000, initializes range/first-subframe/repeat, and calls the already-validated native/original slot loader664c.

The loader's MRSS wait return is discarded; static timeout inputs can still lead to return0 and scan commands. This is a bounded software fact, not a real stalled peripheral assertion. Null start callbacks are used here; callback bodies/concurrency remain unverified.

Reuse resets current slot and invokes start callback if present, disables/enables CTL and writes WAKEUP_CMD1, without SENSOR_DATA reload. After actual original/native ISR completion, changing the active timer with status0x10 updates live hardware immediately and the next reuse retains it with zero sensor stores. This contrasts with changing RAM frame coefficients: timer updates have an explicit live register path.

Four compositions run LP launch/completion, active setter, active five-slot launch, full original/native ISR, another interval update and active reuse. They vary LP signal and supplied hwIirInit0/1. Hardware IIR register enable is derived from that runtime byte; tests do not establish actual startup setting or analog filter dynamics.

## Budgets are software counts

State1's successful-processing tail3d7e loads u32 budget0x200009c8, subtracts1 with wrap, and when the result is0 writes state2, budget160, then requests31211µs. Original execution includes the real proven no-op logger; native source omits that no-op. Inputs0,1,2,160,640,FFFFFFFF test the complete selected tail. Input0 becomesFFFFFFFF and remains state1; input1 transitions tostate2/budget160.

This decrement is conditional on the preceding successful processing branch; it is **not a hardware timer tick or elapsed milliseconds**. Report-produced tail3c30/3c4a/3c54 sets state1 and resets budget640. That observation is static, not new whole-report validation. The decoded state2 branch does not decrement budget160; no160-tick expiry is established. Multiplying requested intervals by budgets could suggest an intended approximate duration, but would not prove actual elapsed time or behavior. No such timeout guarantee is made.

## Public source and evidence limits

Verbatim pinned public ConfigureMsclpTimer with explicit minimal ARM32 layouts/macros and resolved original calculator peer compiles to70 bytes at-Og. It differs from stock70 bytes in five bytes solely involving branch/return placement; **no exact attribution is claimed**. Its full body and original calculator execute in the240+4 three-way tests, alongside the independent native setter/calculator. Other optimizer results remain recorded; no compiler-search loop was undertaken. Prior distinct exact-source attribution remains438 bytes.

Actual reset-copied context is seeded through validated initialization/preparation source, not full application startup. MMIO/MRSS/FIFO/ISR arrival are synthetic; direct ISR calls do not prove IRQ delivery or physical cadence. Tests compare actual persistent RAM/MMIO and bus sequences for launch; compiler stack frames are excluded. No PM callback, physical deadlock, hardware-safety, source-completeness or byte-identical firmware conclusion.

Reproduce screen_public_timer.py from the pinned source, then build_offline.py with --public-timer-source pointing to its generated wrapper.c, GCC, existing pinned public PDL object and explicit scratch output; verify.py ELF runs1160 cases. Receipts retain source/compiler/ELF hashes and bindings. No shared campaign, Git index, commits, production firmware or device writes. Preservation verifies all prior sealed entries,110 inputs and4 checkpoints.

Next actionable dependency: ILO compensation5dd8 and measurement peers9d90/9ddc/9e18, specifically factor updates/readiness loops and the effect on active versus WOT caches. Actual measured frequency/readiness requires a trace; generated history allocation still independently requires absent cycfg/link-map evidence. The nominal212-result/424-byte full-LP window remains configuration arithmetic, not declared allocation.
