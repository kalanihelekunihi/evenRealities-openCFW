# Optimized tick: reduced memory-hook execution failure

The selected optimized failure is reproducible without C compilation, project callbacks, firmware stubs, MMIO, or callback register reads. Registering an empty Unicorn memory hook for accessed RAM changes execution of the same machine code and input. This establishes a precise limitation of the tested Unicorn 2.1.4 Cortex-M4 memory-hook execution profile. It does not identify the underlying native-engine defect or validate the complete optimized scheduler.

## Reproduction

Run from the checkout with the installed OpenCFW Python:

```sh
/Users/kalani/.local/share/opencfw/venv/bin/python g2/analysis/unicorn-it-divergence-2026-10-05/reproduce_machine.py
```

The native JIT requires execution outside the restricted sandbox on this host: the sandbox attempt exited132/SIGILL. Successful authorized offline runs are recorded in `VALIDATION.json`. No hardware is used.

The reproduction reads only `machine-fixture.json`, which retains 296 hash-bound diagnostic bytes from three unchanged linked bodies: tick at0x10000 (238 bytes), list insertion at0x10290 (26), and list removal at0x102ac (32). It needs no ignored ELF, project parser, compiler, Ghidra database or stock firmware. These bytes are a diagnostic fixture, never a firmware implementation or source-completeness substitute. The source ELF SHA-256 is `a04b6f3c7fd1c47d71ccd31615b95ebf44e793382e845cf3bd2c7452d165c478`; this is the reconstructed O2 simulator replica, not the original firmware object.

The fixture contains a single tick call, two aligned priority3 tasks due at tick10, initial tick9, one priority1 current task, empty event-item containers, and no extra future task. The stack is 8-byte aligned and BASEPRI is0x30. Unlike the earlier full case, there is no second/third top-level call, queue, WSF, radio or external-call substitution. Each test uses a fresh emulator. The memory callback consists solely of `pass`.

| Due tasks | Memory hook | Result |
| --- | --- | --- |
| 1 | absent/read/write/read+write | returns1; tick10; correct ready/delayed lists |
| 2 | absent | returns1; tick10; ready priority3 count2; delayed count0 |
| 2 | read-only | unmapped read at0x10296 |
| 2 | write-only | unmapped read at0x10296 |
| 2 | read+write | unmapped read at0x10296 |

Every row is repeated with/without a per-instruction code hook and with `emu_start(count=0)`/`count=20000`: 32 cases, 20 expected successes, 12 expected faults. The script asserts both the completed final-state facts and exact fault facts. `machine-results.json` retains compact results; full instruction histories remain in the original build diagnostic. One due item is a negative control, not evidence that the two-item graph is invalid.

## First concrete discrepancy

On the second ready insertion the caller branches from0x10082 to0x10290. Without memory hooks, the trace includes:

```text
0x10290: ldr r2,[r0,#4]   -> r2=0x2006a4e0
0x10292: ldr.w ip,[r0]
0x10296: ldr r3,[r2,#8]
```

With the empty memory hook, the next recorded instruction is0x10292; the unconditional first load at0x10290 is skipped. R0 is the correct priority3 list address0x2006a4d8, and its `pxIndex` cell at0x2006a4dc still contains0x2006a4e0. R2 remains0 from the preceding removal, so0x10296 reads address8 and faults. The partially completed list has count1 rather than2. This is a change in machine execution, not merely a different display of a successful final state.

The second caller iteration has a false `ITT HI` at0x10072; the first had been true. Hooked traces expose different intermediate IT-state bits. This is a useful localization clue, not proof of a particular IT/cache implementation bug. Smaller synthetic conditional-store/load/return programs in this directory previously succeeded; a blanket claim that Thumb IT is unsupported would be false. Hook registration for an unused0x30000000–0x30000fff range succeeds, whereas an accessed RAM range fails; just installing any unused hook is insufficient.

## Stock, C and ABI checks

`compare_bounded.py` separately runs the corresponding one-call/two-expiry input through authenticated stock instructions and the independent ordered-list/task model, then through O2, O2 with `-fno-strict-aliasing`, and O0 with source memory hooks omitted. All three have exactly equal observable final results and pass the model. The stock Apollo OTA SHA-256 remains `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`; payload load base0x438000 and stock tick entry0x45504c are unchanged. This is one diagnostic case, not optimized full-suite acceptance: source mutation/critical-section memory assertions are absent from this diagnostic and contribute no new validated coverage.

Static independent review found no concrete alignment, field-width, volatile-global or accessed-layout defect. Fixed-address cells use the intended volatile lvalues; list/TCB fields depend on the kernel exclusion precondition. The emitted insertion performs the expected aligned index/count/link accesses. The 32-bit layouts and sparse TCB accessed prefix remain explicit simulation contracts rather than complete scheduler state.

A separate source caveat remains: upstream FreeRTOS uses its compact `MiniListItem_t` sentinel through `ListItem_t *`; this can raise ISO C effective-type/strict-aliasing concerns. O2 with `-fno-strict-aliasing` exhibits the same hook-sensitive failure, and the machine-only reproduction needs no source interpretation. Therefore that caveat does not explain this failure. Original Apollo compiler settings remain unknown; no source fix or flag change is warranted as a claimed firmware repair.

## Fresh full verifier reruns and disposition

The unchanged full verifier was rerun against both current profiles:

- O2 exits1 with the unmapped read. The full failure is preserved in `optimized-full-failure.log`; no passing optimized result was created.
- O0 passes all271 cases. Its result SHA-256 is exactly the prior accepted `e49a44d29a6fb10443e06082ee19d4eaa4fde790603824ea302b452d744d0b63`.

No firmware source, existing verifier, compiler target, shared campaign state, manifest or gate was changed. Current59 foundation source hashes and protected identities remain unchanged. Existing failing artifacts are retained. No commits, staging, flashing or devices were involved.

The bounded investigation can stop here: a self-contained, independently reproducible memory-hook execution limitation has been established. Full optimized validation remains blocked in this emulator profile. Clearing that correctness gate requires an engine correction or a separate validated execution backend that preserves the existing memory/critical-section assertions; simply removing memory hooks or accepting O0 is insufficient. The exact internal Unicorn mechanism and full optimized stock equivalence remain unknown. This packet does not authorize further scheduler expansion or establish source-complete/byte-identical firmware.

Independent review is in `review/report.md` and `review/review.json`; complete artifact hashes and preserved result/log paths are in `VALIDATION.json`.
