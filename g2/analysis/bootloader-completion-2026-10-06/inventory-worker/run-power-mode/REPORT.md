# Bootloader run/special-mode cluster

Baseline4edd8e7d has17 unique OTA numeric entries. Selected main startup's41ba80 run-mode entry and power-domain selector20's adjacent41bae8 special mode. **Run-mode C wrapper/transition/query/wait implementations already existed and were linked**; the main caller still used a numeric alias. This batch reuses those bodies, binds the main alias to existing native mode-two source, and adds independent `platform_control/power_special_mode.c/.h` for special mode and optional callback dispatch. Numeric OTA entries are not all unwritten source functions.

[Alias history](alias-history.json) binds actual saved manifests. Earlier16 wasca59e9:31 aliases/23 unique addresses/16 OTA. Earlier12 was9affaa59:27/19/12. Broaderbe4ede3b exposes12 startup/power/clock/formatting/RX addresses and removes2 relative to9aff, so12+12-2=22 (relativeca59:16+12-6=22). Later clock config/generator/RX stages give21→19→17. Same normalized unique-OTA-address definition, different selected linker profiles. Alias count, unique address count, existing source presence, modeled execution and whole-source completeness are separate metrics.

## Source and evidence

Locked bootloader SHA-256f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5, little-endian Thumb, load410000. Native **1394 comparisons PASS**; callback/delay boundaries are explicit synthetic inputs, while run-mode/transition/query/descriptors/critical/wait/special-mode bodies execute. Compare ordered MMIO stores, interrupt mask, callback arguments, cache bytes and returns. No SRAM write hooks or copy models.

| Body | Bytes | Observed | Source status |
|---|---:|---:|---|
| 41ba80..41bae8 mode-two wrapper | 104 |104 | existing C, newly bound main alias |
| 41b954..41ba80 transition |300 |300 | reused existing linked C |
| 41bae8..41bbd0 special-mode operation |232 |228 | newly reconstructed |
| 41cde0..41cdfa special callback |26 |26 | newly reconstructed |

New source bodies258 bytes,254 observed; reused bodies404 fully observed. Unvisited four bytes41bb26/41bb28 return1 after query error. Native query is called with fixed selector20 and a nonnull stack output; descriptor lookup accepts selector<34 and writes0/1, so that error branch is not observed under these inputs. No child-answer stub was added to inflate coverage; source preserves the defensive branch.

Earlier wake-not-ready fixtures incorrectly used a base word with bit24 already set. `verify-before-wake-fixture-fix.py` and `comparison-before-wake-fixture-fix.json` preserve them. Corrected base clears that bit and exercises the actual wake-failure branch. A negative control omitting saved-cache synchronization fails; counterexample/log retained separately. No expected-answer adjustment or firmware source mutation was used to obtain PASS.

## Recovered software policy

Run-mode wrapper truncates to lowbyte, accepts1/2, returns6 otherwise. Mode2 first requires40021108[5:4]==3 or returns7; cache20000552 equality then short-circuits success. Otherwise it executes the existing transition, propagates its status, then compares40021000[4:3] to requested mode; mismatch returns1 even if transition updated the cache successfully.

Transition saves interrupt mask. Mode2 calls optional config hook with byte1; temporarily sets wake-control40004044 bit5 if previously clear, requests delay1, executes actual equality wait(count15, status40004030, mask/expected01000000), then explicitly rechecks readiness. Missing wake bit returns1. It writes requested low2 mode bits to40021000 and polls ready bit2 up to20 iterations with delay1, returning4 on timeout. A ready bit becoming set after the twentieth delay is too late for this loop. Temporary wake bit is cleared and notify hook runs even on failure. Success caches mode and disables config for non2; mode2 failure also disables config. Registered callback statuses are ignored. Delays/acknowledgement here are software arguments/synthetic test events, not physical timing guarantees.

Special mode truncates to lowbyte and accepts0/3. Mode3 shares the40021108 capability gate. It queries selector20 (status40021008 mask00040000) before cache checks: query error→1; active resource→3, no writes. If requested equals cache200271a5, synchronize saved byte200271a6 if different and return0, without delays or callbacks.

On change, save mask; for3 call optional hook(operation1, mode3) **before** setting40021090 bit0. For0 clear bit0 first. Delay1, replace4002108c low2 bits, store both cache bytes, delay6, and for0 call hook(operation1, mode0) **after** writes. Restore mask and return0. Hook at20026e38+24h receives lowbyte operation/mode, returns0 if absent; special-mode caller ignores its return. It never copies/retains buffers or allocates/frees memory. Real callback reentrancy/scheduling/hardware safety remains outside proof.

This closes selector20's source dependency: existing power-domain enter may restore saved special mode3; leave requests0 then records saved3 for a future restore. Those callers can ignore the special-mode status, so software bookkeeping is not proof that hardware accepted the change.

Main startup and runtime reachability must be verified on the final integration candidate, distinct from native direct behavior. All seven cases, affected UART/clock/math/logger/kernel/power regressions, alignment and frozen-input reconciliation remain prerequisites for promotion;4edd8e7d is preserved until then. Full vectors/assets/data/layout/compiler equality, IAR backend, task restoration and legitimate external ROM/hardware behavior remain unresolved.

## Integrated reconciliation

Candidate64e525046809722484ff5fe65ebea5550352915ed292e5e6989a5acfa9ea9b7d promoted after all7 cases PASS,664 inputs/170 objects unchanged, exact frozen copies authenticated,490 mappings PASS and zero manifest mismatches. Native selector20 enter/leave256 comparisons PASS with synthetic power acknowledgement, callback bodies and clock return boundaries; no physical ownership/drain proof. Supplemental legacy-power runner failed before execution because its standalone release-needed symbol is absent; no PASS claimed. Prior4edd preserved. Selected OTA addresses17→15, same scope; newly bound41ba80/41bae8.
