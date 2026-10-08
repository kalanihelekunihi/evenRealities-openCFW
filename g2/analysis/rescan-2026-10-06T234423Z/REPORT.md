# Source and integration rescan

Snapshot 2026-10-06T23:44:23.860423+00:00, compared with g2/analysis/rescan-2026-10-06T231254Z. Read-only project inspection; only this scan directory was written. Concurrent integration work continues. No build, generator, emulator, staging, commit or hardware action ran for this scan.

Bootloader source files: **221 → 222**; foundation **89 → 89**. Changes: 1 added, 4 modified, 0 removed. Across both roots: 310 tracked, 1 untracked, **0 ignored source files**. Counts include headers/assembly/fixtures and do not measure source completeness.

## Substantive change

Requests 30/34 now route to reconstructed handlers in control_remaining.c and are selected by the shared image compile/link paths. Native NOR timing/address/serial handlers replace their former numerical entry aliases. Initializer runner, callback bodies, callback table and context configuration data are selected in the shared image. The callback table is source-defined; no whole callback success stub is claimed. Child platform/ADC/RTOS providers remain modeled or numerical bindings.

Separate shared-image receipts for 3388449d identify 33 request30 and 19 request34 PASS cases. Callback receipts identify 31 callback and 60 mode-register PASS cases. These are bounded synthetic comparisons, not the final seven-case full integration result; they cannot transfer to ac4b without replay.

## Validation boundary

The prior d79edbcb checkpoint remains the last verified seven-case image; all 5 prior pinned identity checks still match: True. Its seven PASS cases and 31,344 observed original trace bytes remain valid for that exact image.

New immutable candidates b451c420, 3388449d and ac4b5688 exist with matching path identities. **ac4b is not a seven-case validated replacement.** Current worker diagnostics pinpoint an actual linker defect: odd-length rodata ends at 0x31a9b and the NOR timing assembly entry is placed at that odd address. Thumb execution then encounters bytes a8 df at even PC0x31aa4 (SVC #0xa8), while the existing exception adapter assumes SVC #2 and reaches its fatal store0x10034. This is an integration alignment defect, not evidence of a hardware fault or an unsupported floating-point instruction. Correct section alignment and rerunning the exact resulting image are next required steps. Diagnostic finding was received from the active worker; this scan did not independently rerun the emulator.

Current linker exposes 75 numerical bindings at 67 unique addresses. The increase over the old38 ledger exposes callback child boundaries while removing whole-family cuts; it is not a count of newly missing functions. Runtime/ISR/task cancellation, ADC/context/service children, logging/fatal paths and resident ROM behavior remain boundaries. Whole firmware assets/layout/compiler reproduction and byte equality remain unproven.

## Ignore interpretation

The build/ rule hides ELF and build-local receipts. No source file in these two roots is ignored. New code is present; the material change is integration and evidence, with a current failing alignment case—not hidden source generation. No local exclude file or global excludes configuration was found. One nested ignore exists in the unrelated shortcut-batch resources directory; neither source root contains a nested ignore. Earlier staged/unstaged work was preserved.

## Changed source paths

- `g2/components/bootloader/initializer_callbacks/callback_table.S` — added
- `g2/components/bootloader/initializer_callbacks/platform_finish.c` — modified
- `g2/components/bootloader/nor_init/nor_init.c` — modified
- `g2/components/bootloader/nor_mspi_init/control_remaining.c` — modified
- `g2/components/bootloader/nor_mspi_init/control_remaining.h` — modified

Machine-readable hashes, Git views and artifact identities are in snapshot.json; full checkout status is in git-status.txt.
