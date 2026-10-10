# OpenCFW shortcut-theory third frontier, 2026-10-09

This continuation used three GPT-6.1 Sol low-reasoning tracks to exhaust the
remaining defensible third-party/dependency branches identified by the prior
two shortcut reports. It stayed within the active P2 procedure: no canonical
coverage, firmware source, installed processor, authenticated input, or gate
was changed. The findings below are candidates ready for independent review,
not accepted campaign coverage or proof of a complete source build.

## Net new knowledge

### NationalChip provider archives

- Eleven registered NationalChip objects contain 121 executable sections and
  175 sized symbols. Relocation-aware comparison found 44 XIP section
  candidates and 82 noncontradictory function candidates, including 34 exact
  function extents. The aggregate sizes are identification inventory, not
  additive pseudocode coverage.
- `_ain_reset` is an exact 320-byte provider match. Additional exact or
  relocation-qualified matches constrain PCM/input selection, gain, EVAD,
  FFTVAD, audio initialization, SNPU register helpers, PMU control, and clock
  control. Sixty linked branch targets were corroborated; 40 remain explicitly
  unresolved.
- Relocation masking initially made `npu_dis_interrupt` look like a match at
  the `npu_en_interrupt` address. Native target decoding rejected it because
  all seven stock calls reach `reg_set_bit`, while the archive's disable body
  requires `reg_clr_bit`. This is a reusable guard against masked-call false
  positives.
- The GRUS audio-v2 ABI passes five callbacks by value. Stock supplies record,
  configuration, and update callbacks and leaves energy-VAD and FFTVAD null on
  the inspected initializer path. PMU request 13 is source-defined as
  GPIO|audio|I2C, and the stock suspend root is tied to the archive PMU setter
  and enable providers.

### Source-aware analysis automation

- Authenticated Apollo main bodies at `0x004D0524..0x004D0554` and
  `0x004CFFC2..0x004D003A` match TLSF `control_construct` and
  `search_suitable_block` on the exercised domain.
- The control structure is 3,188 bytes: a 16-byte sentinel, first-level bitmap
  at +16, 24 second-level bitmap words at +20, and 24 by 32 free-list heads at
  +116. Initialization performs exactly 795 word writes while preserving the
  sentinel's first eight bytes and the tail.
- Original-byte execution passed all 768 bins within 2,672 search cases and
  verified the initializer write set. The inconsistent-bitmap path carries the
  original `third_party\\tlsf\\tlsf.c` assertion expression and line 568,
  matching the pinned source family.
- Private Ghidra bounded exports, GNU decoding, Ablation call profiles, and
  Unicorn execution agree. Ghidra-MCP and REA remain useful transport and
  orchestration layers, but neither adds an independent semantic oracle for
  this branch. Reusable authenticated scripts and hashed receipts are retained.

### Official package and release archaeology

- The official Apollo_DFP 1.5.2 pack was acquired and hash/CRC verified. Its
  Apollo510 startup is deliberately disabled by `#if 0` and directs users to
  SDK examples, so it is not a producing startup source. Its real generic
  `system_apollo510.c` is retained as a named comparator only.
- Infineon's CAT2 DFP exposes a dummy startup whose purpose is to emit a
  compiler error. It does not provide target CapSense generated C; the exact
  `.cycapsense`, generator version, and dependencies remain required inputs.
- STM32G0 pack history explains the current-source dead end: DFP 2.0 removed
  Cube firmware, startup, HAL, and LL components in favor of a global
  generator. Historical DFP/Cube/HAL version mappings are now recorded.
- IAR documentation makes DLIB source delivery product-package dependent and
  locates it under `arm/src/lib`. The actionable input is therefore the exact
  producer-version IAR product package, not a current compiler-extension pack.
- NationalChip's official GX8002 guide names the private historical acquisition
  route `git@gitlab.com:nationalchip/lvp_tws.git` and says access is arranged
  through sales/project management. Public NationalChip release arrays are
  empty. This turns a generic search into a precise unavailable-input request.
- Official EM9305 and Ambiq release/index checks exposed no historical v4.2
  implementation source or useful immutable Git source beyond the sources
  already registered.

## Acquisition and submodule decision

The official release pass retained 17 hash-identified metadata snapshots and
the Apollo_DFP 1.5.2 archive with selected source members. These are versioned
archive evidence, not Git repositories. No newly discovered Git source met the
bar for another submodule: the useful NationalChip TWS repository is private
and lacks an authenticated pin, while the relevant public source families are
already registered. Existing Ghidra-MCP, Ablation, REA, Ambiq, Infineon, and
NationalChip pins were not changed by this continuation.

## Finite third-party boundary

For the currently authenticated bodies, registered archives, official package
indexes, and public histories, no untried third-party/dependency source lead
remains that can add defensible identity without a new input or a new target
body discriminator. Repeating generic repository, release, package, or tool
queries would not close the remaining obligations.

The residual work belongs to different evidence classes:

- independent review and canonical admission of these private P2 candidates;
- first-party G2 application/protocol semantics and further bounded firmware
  review, including unresolved provider calls and callback effects;
- authentic private inputs: historical GX8002B `lvp_tws`, EM9305 v4.2,
  producer-version IAR `arm/src/lib`, the exact MetaWare project, or target
  CapSense configuration/generator;
- resident-ROM and hardware/runtime behavior; and
- whole-artifact pseudocode completion, corpus freeze, later source
  implementation, and byte-identical rebuild under the existing gates.

This is a finite exhaustion claim over the evidenced source set, not a claim
that unavailable private material does not exist. Newly supplied authentic
inputs or a newly selected authenticated body can reopen a bounded branch.
No cybersecurity classifier rejected any phase, so Daybreak Blue was not
needed. G2 remains in P2; later implementation and byte-equality gates remain
closed.

## Evidence

- `../shortcut-provider-archive-20261009-agent1/REPORT.md`
- `../shortcut-provider-archive-20261009-agent1/archive-inventory.json`
- `../shortcut-provider-archive-20261009-agent1/function-inventory.json`
- `../shortcut-tool-automation-20261009-agent2/REPORT.md`
- `../shortcut-tool-automation-20261009-agent2/receipt.json`
- `../shortcut-tool-automation-20261009-agent2/ghidra-receipt.json`
- `../shortcut-release-archaeology-20261009-agent3/REPORT.md`
- `../shortcut-release-archaeology-20261009-agent3/acquisition.json`
- `../shortcut-release-archaeology-20261009-agent3/inventory.json`
