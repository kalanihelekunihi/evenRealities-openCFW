# CASE round 3: original entry imports

The archive now includes `evidenced_providers.c` as its twelfth source object. It resolves three original import names:

| Candidate | Original evidence | Scope |
| --- | --- | --- |
| `case_event_post` | Frame callback hook binds to Thumb `0x0800a889`; that is entry `0x0800a888`, independently reconstructed as `case_event_flags_set` in the event-flags closure. | Delegates 32-bit event address in r0 and flags in r1. |
| `case_forward_event` | Binary forward hook also binds to Thumb `0x0800a889`. | Delegates same pointer/flags ABI. |
| `HAL_UART_ErrorCallback` | Retained original disassembly at `0x08005f42` is exactly opcode `7047`, Thumb `bx lr`. | Empty `void(void *)` callback; built object is opcode `4770` as displayed little-endian, `bx lr`. It does not model unrelated callbacks. |

`verify_evidenced.py` checks those retained address bindings and original/candidate error-callback instructions. It passes. The event-set body itself has prior original-versus-independent comparisons in `case-event-flags-closure-2026-10-08/REPORT.md`; round 3 did not rerun Unicorn runtime comparisons, so the new provider alias path has static ABI/address verification only. Any stock IAR byte-equality claim is excluded.

The rebuilt archive has 12 objects, 27 defined symbols, and 24 unresolved names. `provider-census.json` now attaches a concrete per-symbol original address where a prior hook recorded one and a specific blocker for every unresolved import. It distinguishes four missing/indirect address bindings from prior stop-before-entry boundaries and kernel peers. CASE original body and source search still leave coherent scheduler/list/queue, transport and command paths open. No stub was inserted for them.

**Round count and remaining work:** three small imports completed this round; 24 remain. At least 24 provider compatibility checks remain, with several sharing the same kernel state model. A conservative lower bound remains one linked-image gate and one integrated behavior campaign after provider work, plus the per-symbol investigations in the census. This is not an exact effort estimate in hours; original child bodies and hardware behavior may expand scope. The boundary exhausted in this round is the retained direct-hook/address evidence for these three names, not the entire CASE firmware.

Reproduce with `python3 g2/components/case/source_candidate_20261010/build.py`, `python3 g2/analysis/case-source-candidate-round2-20261010/classify.py`, then `python3 g2/analysis/case-source-candidate-round2-20261010/verify_evidenced.py`. These scripts use only Python standard library, absolute `/usr/bin/clang` and `/opt/homebrew/bin/arm-none-eabi-{ar,nm,objdump}`. `receipt.json` records the actual Python interpreter, tool identities/hashes, all compiler header dependencies and hashes, exact compile/archive commands, and deterministic archive rebuild comparison.

The event-post and forwarding aliases also pass 384 original-versus-compiled-source Unicorn comparisons each with explicit kernel-result boundaries; see [ROUND3-CLEAR.md](ROUND3-CLEAR.md) and `behavior-results.json`. This replaces the earlier static-only validation state for those alias paths.
