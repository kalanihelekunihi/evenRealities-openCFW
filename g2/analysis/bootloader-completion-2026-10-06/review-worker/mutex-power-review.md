# Independent mutex and power-guard review

Scope: read-only review of current queue mutex wrappers and platform power guards, their verifiers, and the saved 500-case source-control integration. No source files were edited. The locked reference identified by the result files is SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

## Results

I independently reran the native offline Unicorn comparisons with the repository venv and wrote fresh results here:

- `mutex-independent.json`: PASS, 288 cases, 258 distinct original trace bytes.
- `guards-independent.json`: PASS, 14 cases, 164 distinct original trace bytes.

Both use the current source files and local ELF inputs. They compare real stock and compiled-source control flow while intercepting the explicitly synthetic kernel or power-control providers. The 288 mutex cases cover both entry points, handle tags/nulls, timeout choices, provider returns 0/1/2, and six interrupt-mask/runtime-state fixtures. Exact `== 1` provider success behavior is exercised. Kernel mutex storage, scheduling, contention, recursive ownership, priority inheritance, and nonzero IPSR behavior are outside the tested claim.

The saved integrated `control-comparison-first.json` records 500 PASS cases and its 11 basename-keyed source hashes match the current files when resolved under `g2/components/bootloader/platform_control/`. It exercises the source power guards and critical-save assembly, with static synthetic MMIO and a synthetic power-control callback. It does not establish physical MRAM/power behavior, timing, or firmware write safety.

## Power callback argument review

Stock begin entry/body is `0x41BD92..0x41BDE2`; end is `0x41BDE4..0x41BE34` (half-open ranges). In begin, `push {r2,r3,r4,lr}` at `0x41BD92` saves R3, `str r0,[sp]` at `0x41BDA8` writes the status-derived configuration word, and `mov r2,sp` at `0x41BDAA` passes the pair to `0x41CD1A` at `0x41BDB0`. Thus `[SP+4]` is preserved incoming R3. The recovered caller at `0x42E4A0..0x42E4F2` saves input R3 in R7 (`0x42E4A8`), calls critical-save (`0x42E4BC`), calls guard begin (`0x42E4C2`), then stores R7 at `[SP]` (`0x42E4C6`), so the incidental second word is the input word count. End's `push {r7,lr}` at `0x41BDE4` saves LR at `[SP+4]`; it writes only status at `[SP]` (`0x41BE26`) before the op-5 call (`0x41BE2E`).

`0x41CD1A` dispatches through the callback slot initialized by `0x41CE52`; its `blx r3` at `0x41CD2C` preserves R2 as the third callback argument. The recovered selector branches choose callback entries `0x42A879`, `0x42BA01`, `0x42D563`, or `0x42F38F`. The op-5 paths are: `0x42A878` compares saved request (`sb`) to 6 at `0x42A97E`, branches `<6` at `0x42A984` to `0x42A9B8`, and reads `[r4]` at `0x42A9BC`; `0x42BA00` compares at `0x42BB02`, branches `<6` at `0x42BB08` to `0x42BB3C`, and reads `[r0]` at `0x42BB40`; `0x42D562` compares `r0` with 6 at `0x42D578`, branches `<6` at `0x42D57C` to a return-only block `0x42D5BC..0x42D5C0`; `0x42F38E` compares at `0x42F3A4`, branches `<6` at `0x42F3A8` to a return-only block `0x42F3D4..0x42F3DA`. I found no op-5 read of `config[1]`. Thus the second stack words do not affect these recovered op-5 callback behaviors; their incidental values should not be mistaken for part of the modeled contract. This covers the recovered selector/callback implementations, not proof of which callback is active on a particular physical device. The fixture captures only config word 0, which is adequate for those known op-5 implementations but does not independently validate arbitrary callback code or other request values.

## Evidence freshness and limits

The prior standalone `guards-comparison-first.json` is stale: its recorded shared `verify.py` hash is `c41f678c0956590c50ef315a42f9584cfc0853acac0656ef4b1611e57ce82961`, while the current file is `10aef878f48b24517e96323685a96ddd7a1e0cb4ec13438b20ea7b0f3c083762`. The fresh independent guard result above is bound to current inputs. The 500-case integrated control result is separately bound to current sources and is not stale on this check.

The guards test statically holds synthetic registers, so it covers immediate-ready and poll-exhausted paths but not changing status, elapsed time, interrupt interleavings, or physical power transitions. The `10000` poll count is an iteration bound, not a verified time unit. Kernel/power provider interception means these results do not prove full-source bootloader completeness, stock-binary identity, or hardware behavior.
