# Public-source discovery and acquisition — 2026-10-09

Scope: source discovery, acquisition and provenance only. No firmware recovery, downloaded-code execution, staging, root index/submodule mutation, device access or production change. All writes are inside this directory. Canonical ledgers remain owner-controlled. Repository AGENTS.md, workflow README, third-party registry, consolidated tooling/toolchain references, repository-goal reconciliation and final-static source successor were read. `.agents` and `.agents/skills` do not exist in this checkout.

## Useful new acquisitions

| Source | Verified public URL and detached pin | License and expected gain |
|---|---|---|
| embARC OSP | https://github.com/foss-for-mips-arc-processors/embarc_osp — `67ea926c6a62aa6e19efdc3b11cba3ea0b467e29` | Root LICENSE is Synopsys BSD-3-Clause; bundled components have their own terms. ARCv2 startup, vector installation, exception frame and auxiliary-register/cache/timer sequences provide a public semantics comparator for bounded EM9305 P2 startup/exception work. |
| NationalChip lvp_aiot | https://github.com/NationalChip/lvp_aiot — `d4aa00943e22f9ddfa424f979fae3ee2a62f5c0b` | Root MIT, copyright NationalChip 2024; bundled dependencies and binary archives require per-component review. Alternate official GX8002 SDK exposes differing application/board/configuration/provider code beyond registered lvp_kws. |

Acquisitions are shallow detached Git checkouts under `acquisitions/`. `provenance.json` records exact pins, remote URLs, sizes and SHA-256 of every acquired working-tree file (excluding Git metadata). Nothing downloaded was executed. Git checkout only materialized source. The old Synopsys organization URL currently redirects to the MIPS ARC organization; the verified current repository remains a public ARC-project comparator. Official Synopsys embARC datasheet: https://www.synopsys.com/dw/doc.php/ds/cc/embarc-ds.pdf .

## Concrete comparison leads for owner

NationalChip comparison against existing registered `third-party/upstream/nationalchip-lvp-kws` working tree yields 424 C/header/assembly files: 318 identical, 68 different, 38 new paths. Full file-level evidence is `nationalchip-comparison.json`. These are differences, not added firmware coverage. Prioritize:

- `boards/nationalchip/grus_gx8002b_dev_1v/{boot_board,audio_board,clock_board,misc_board}.c` and board configuration headers: alternative official board initialization/configuration oracle.
- `lvp/common/{uart_message_v2,lvp_audio_in,lvp_i2c_msg,lvp_system_init,lvp_queue}.c`: alternate provider and protocol framing lineage.
- `include/driver/{gx_flash,gx_pmu_ctrl}.h`: different public API contracts.
- embARC `arc/startup/arc_startup.s`, `arc/arc_exc_asm.s`, `arc/arc_exception.c`, `arc/arc_cache.c`, `arc/arc_timer.c`: startup/exception semantics reference.

Each must be tied to locked image bytes by owner recovery and independent review before admission. Neither checkout is proven to be the producing source; embARC is not proof that EM9305 linked embARC. Alternate NationalChip configuration does not prove stock board settings. The owner may find all differences irrelevant; acquisition does not imply acceptance.

Proposed additions for owner review only: `third-party/reference/embarc-osp` and `third-party/reference/nationalchip-lvp-aiot` at the above pins, comparison-only and update=none. No `.gitmodules` edit or gitlink was made.

## Searches and exclusions

Reviewed existing Ambiq `5efc0228528a8adce5eae0d226fac85d2551eb3b`, FreeRTOS/CMSIS, Cordio, LVGL/Nema headers, Infineon, STM32, NationalChip KWS/DNN and tool registry. No duplicate Ambiq acquisition. Web searches checked official ARC startup/EM7D sources, C-SKY GCC/binutils sources, official EM9305 SDK availability, NationalChip GX8002 SDK and Ambiq NemaGFX source. C-SKY compiler/binutils are already pinned in tooling references, so no duplicate acquisition. Existing NationalChip lvp_kws and gxDNN likewise were reused as references.

Official NationalChip documentation https://document.nationalchip.com/en/software/software/ describes SDK GitLab account registration; no authenticated access was attempted. Public searches found no new official EM9305 implementation source or NemaGFX implementation source. Lack of a search result is not proof of universal unavailability. No model/entitlement access denial occurred. Initial sandbox DNS restriction was resolved through approved public Git network calls.

## Remaining limits

This search identifies two previously unregistered public comparison sources; it does not claim all public knowledge is exhausted. It cannot supply exact private producing checkout, MetaWare/IAR proprietary runtime sources, Nema implementation, private Packetcraft/controller source, resident ROM/factory evidence, signing inputs or physical state. Existing audio/UART/power static boundary remains unchanged. Whole-image P2 and independent-review/freeze gates remain owner work. Existing 110 inputs, four checkpoints and concurrent evidence were not written or resealed; their integrity audit belongs to the audit track.

## Follow-up static comparison

See `STATIC-COMPARISON.md` and `locked-target-candidates.json`. Raw differences were refined: 25 of 68 different source/header files are comment/whitespace-only under a lexical heuristic. UART-message and boot-board inspected diffs are copyright-only. Concrete differing board clock/audio and FFT/VAD branches remain comparison leads. Locked payload VAD strings favor the existing KWS active diagnostic branch over unmodified AIoT. No exact new source attribution was admitted.
