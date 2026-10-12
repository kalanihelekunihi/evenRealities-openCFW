# BINH B stage-1 source/layout candidate

`build_stage1_candidate.py` compiles 11 CK804EF C units in `g2/components/gx8002/image_b_stage1_candidate/`, links a separate stage-1 ELF with `layout_probe.ld`, extracts a 0x1734-byte load image, and checks source coherence. It does not edit the selected stage-2 archive. The loader’s normal branch still copies exactly 0x1408c stage-2 bytes; it does not load late audio.

The 24-byte BINH header is file-only: stage-1 runtime PC equals file offset plus `0x0fffffe8`. Stock vectors and reset are at 0x10000000 and 0x10000100. The candidate ELF preserves those addresses, the 0x10000130 native default-loop address, and the authenticated stage-2 entry contract 0x10003100. Its vector bytes and reset instructions outside the relocated boot-setup call match stock.

The pinned NationalChip SDK commit `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5` supplies source attribution for the clock, GRUS trim, boot-info, transfer-mode, baud, and flash JEDEC records. `verify_clock_gate_tables.py` checks 26 parameter records, 20 pointer relocations, 10 source records, DTO/divider bytes. `build_stage1_candidate.py` verifies the seven source-owned load ranges, including the 20-byte 0x20001720..0x20001734 initialized runtime records, byte-equal stock. `audit_direct_calls.py` accounts for 23 corrected-PC native BSR targets: 20 source C entries, two pinned-source inlines, and one stage-2 entry. That is a target census, not proof that every body has equal runtime effects.

The experimental ELF ends at load offset 0x1734, within the stock 0x3000 stage-1 extent. An experimental typed BINH header and CRC-32/MPEG-2 footer are generated from the C-built load image; no stage-2 payload is appended. Physical IRAM/DRAM aliasing, flash/MMIO effects, computed edges beyond the six scanned tables, and whole-body equivalence remain separate gates. The stage-2 late-audio section is still outside the stock normal copy. No package or hardware was changed.
# Corrected-PC register control flow

`python3 audit_computed_edges.py` checks the full native code span
`0x10000100..0x10001324`. It finds 20 register branch sites: 12 returns,
six bounded table dispatches, and two computed calls in the loader. The
loader constructs `0x10003100` (stage-2 reset) and `0x10000100` (stage-1
reset) directly before those calls. The receipt is
`computed-edge-census-receipt.json`. This closes the syntactic register-edge
inventory only; individual dispatch effects and the physical transfer remain
separate qualification gates.

## Full loader branch review (2026-10-12)

`loader-branches-review-receipt.json` independently reviews both native branches against the selected C loader, and `verify_loader_branches.c` passes32 host UBSan cases (both marker paths, four package offsets and four loaded words). The alternate zero-byte read and unsigned32 wraparound remain exact source contracts. Reader return values are ignored as native; fixtures always provide the local word, so failed reads retaining ambient stack are outside proof. Reset and flash are child cuts. Pinned SDK `spl.c` loads the DRAM window and jumps the corresponding IRAM entry, corroborating intended alias usage; physical alias and complete package execution are still unproved.
