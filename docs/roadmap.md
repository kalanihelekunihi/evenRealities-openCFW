# Roadmap: full decompilation, then byte-identical C

The work has two goals, pursued in order.

1. **Decompile everything.** Recover reviewed pseudocode for every executable
   byte of every payload of both devices, and account for every non-code
   byte. Use industry-standard tools and identify every upstream component.
2. **Reduce to C.** Only once goal 1 is frozen, turn that pseudocode into C
   that the original toolchains compile and link into images byte-identical
   to the locked artifacts. Iterate until every payload and container
   matches.

The G2 phases and gates are defined normatively in
[`../g2/workflow/PROCEDURE.md`](../g2/workflow/PROCEDURE.md) (P0–P6, G1–G6).
This roadmap applies the same phases to R1, sets the order of work, and lists
the shortcuts that make it tractable. Where this page and the procedure
disagree about G2, the procedure wins.

## Targets

| Device | Artifact | Payloads |
| --- | --- | --- |
| G2 | EVENOTA `s200_v2.2.6.10`, SHA-256 `f4dfb0b4…` ([target lock](../g2/workflow/target.json)) | Apollo main app, Even bootloader, EM9305, GX8002 codec, PSoC touch, STM32G0 case |
| R1 | application `2.2.6.0009` + bootloader + UICR ([identities](../r1/blobs/official/2.2.6.0009/PROVENANCE.md)) | nRF52840 application, Secure DFU bootloader; S140 7.2.0 is Nordic's binary |

## Phases

Each phase ends at a gate. A gate passes only on evidence produced by that
phase: hashes, coverage indexes and independent reviews. Progress is
measured per payload with four separate numbers: **bytes classified**,
**functions reviewed**, **functions byte-matched**, and **bytes produced from
source**. They are never merged into one percentage.

### Phase 0 — Environment and oracle

- Place the official inputs. Every tool refuses unknown hashes.
- Install and pin the analysis tools (`tools/bootstrap/bootstrap.py --record`,
  then commit the hashes). Initialise the needed submodules.
- Install the licensed original compilers and fingerprint them with
  `bootstrap.py --licensed`: IAR EWARM (candidate 9.60.2), Synopsys MetaWare
  T-2022.09, and Arm Compiler 5.06. Without them, phases 5–7 cannot reach
  byte equality. Try to obtain the exact releases early, because it is the
  longest-lead item.
- Record the Ghidra version, processor modules (ARM, the ARC fork, C-SKY)
  and analysis options in the campaign identity.

### Phase 1 — Inventory and container accounting (G2 P1/G1)

- Write Kaitai Struct specifications for EVENOTA, the main-image preamble,
  touch and codec FWPK, the codec BINH A/B images, the EM9305 record package
  and the case `EVEN` wrapper, from
  [`../g2/docs/reference/firmware-formats.md`](../g2/docs/reference/firmware-formats.md).
  Round-trip each official payload through its specification byte for byte.
- Classify every byte of every payload as container, vector table, code,
  literal pool, read-only data, initialised data image, compressed data,
  asset, model weights, or padding.
- R1: the same for the application, bootloader, UICR and the
  `__scatterload` compressed RW image. Decompress it and record the
  decompressor as a stock Arm Compiler runtime function.

### Phase 2 — Identify everything that already has a source

This is the highest-leverage phase. Every function attributed to a pinned
upstream is a function nobody has to decompile by hand.

- **Evidence harvest.** Collect embedded version strings, `__FILE__` and
  assert paths (`s200_ap510b_iar_git/...`), log format strings, SDK
  configuration constants, and the naming seeds already in
  [`../g2/symbols/`](../g2/symbols/README.md) and
  [`../r1/docs/reference/`](../r1/docs/reference).
- **FunctionID and BSim databases.** Build one per candidate compiler and
  option set from the pinned submodules: FreeRTOS, CMSIS, Cordio, LVGL,
  littlefs, nanopb, FreeType, liblc3, LZ4, TLSF, EasyLogger, FlashDB, cJSON,
  TinyFrame, QP/C, the Infineon PDL, STM32CubeG0, NationalChip `lvp_kws`,
  the nRF5 SDK, and so on. Add the vendor runtime libraries from the licensed
  installs: IAR DLIB, the MetaWare runtime, and the armcc C library. Apply
  them to every payload.
- **Pin what you find.** For each identified library, bisect its version by
  matching functions against upstream tags and commits. Add or correct the
  submodule under `third-party/upstream/` at the exact commit, or at the
  best commit inside a proven interval, stating which. Record the evidence in
  the device's library reference. Consume upstream code from the submodule;
  never re-implement it.
- **Compiler identification.** Compile matched upstream functions under each
  candidate compiler release and option set, and keep the combination that
  reproduces them byte for byte. This fixes the toolchain for phases 5–7.
  Open candidates:
  - IAR release and DLIB configuration for the Apollo payloads;
  - GCC release for touch, and the Arm Compiler 6 (armclang) release for
    the case, which is a Keil MDK build (`tools/matching/experiments.md`);
  - C-SKY GCC release for the codec;
  - armcc 5.06 update level for R1.
- **Recover configuration.** Derive config headers from constant tables and
  code shape (`lv_conf.h`, `FreeRTOSConfig.h`, `sdk_config.h`, `fdb_cfg.h`,
  Cordio feature flags), starting from `config-recovered/`. Check them by
  compiling the upstream and matching bytes.

### Phase 3 — Whole-image decompilation (G2 P2/G2)

- **Set up the analysis project.** Import each payload at its load address.
  Create memory blocks from the SVD file and the memory-map reference, and
  seed vector tables and known entry points. Import data types by parsing the
  pinned SDK and upstream headers into Ghidra. Apply FunctionID/BSim names and
  signatures, then the naming seeds.
- **Harden the decompiler.** Fix disassembly with the GNU objdump oracles
  wherever Ghidra is weak: MVE/Helium and low-overhead loops on the
  Cortex-M55, ARCv2 EM long immediates, and C-SKY DSP instructions. Record
  every manual override.
- **Recover types and interfaces.** Recover structures, enums and globals
  from upstream headers first, then from usage. Recover inter-processor
  message formats from [`protocols.md`](../g2/docs/reference/protocols.md) and
  the R1 [`protocol.md`](../r1/docs/protocol.md).
- **Export and iterate.** Export raw pseudocode per function in the
  workflow's record format, then iterate: unknown spans, unresolved indirect
  calls and switch tables, and data mistaken for code, until coverage is
  complete.
- **Use dynamic analysis to settle ambiguity.** Run the G2 firmware emulator
  once it is added, Renode's nRF52840 platform for R1, Unicorn for isolated
  functions, and the XuanTie and ARC QEMU builds as instruction oracles. Use
  execution only to decide between hypotheses, never as a replacement for
  review.

### Phase 4 — Independent review and freeze (G2 P3/G3)

- A reviewer independent of the author checks every function's pseudocode
  against the disassembly, checks every non-code byte's classification, and
  reconciles globally: call graph, data references and interrupt vectors.
  Iterate phases 3–4 until nothing is unexplained.
- Freeze the corpus with a manifest and store it in a durable, versioned
  evidence location, as the workflow requires. From this point, C work may
  depend on it.

### Phase 5 — Build-system recovery and contracts (G2 P4/G4)

- Recover each payload's link map: section order, object boundaries,
  alignment and padding, and link order. The EM9305 appears sorted by
  `.text.*` name. R1 uses an armlink scatter layout. Apollo uses the IAR
  `.icf` placement.
- Write a linker script, scatter file or `.icf` per payload that reproduces
  the stock placement exactly. Split the frozen corpus into
  translation-unit-sized chunks with shared headers, and freeze those
  contracts.
- Add a **matching scaffold** per payload. Every function starts as its
  original disassembly in a `.s` file, so the build is byte-identical from
  day one. Every C conversion is then checked immediately. The assembly
  scaffold is a progress aid only and never counts as source completeness.
  Track the bytes still in scaffold as a separate number.

### Phase 6 — Reduce to C (G2 P5/G5)

Work in order of leverage:

1. **Upstream libraries.** Build them from their submodules with the
   recovered configuration and the identified compiler. When these match,
   whole blocks leave the scaffold at once.
2. **Vendor SDK code** from pinned SDKs, with the recovered deltas as patches
   in `config-recovered/`.
3. **Binary-only vendor code** (GoMore, Goodix algorithms, NemaGFX,
   Packetcraft LL). Link the vendor's original object archives where they can
   legitimately be obtained. Otherwise byte-match decompiled C like
   application code, recording which approach each function uses.
4. **Application code** from the frozen pseudocode, one function at a time.

For each function, the loop is: write C from the pseudocode, compile with the
identified toolchain, diff with objdiff or asm-differ, and use
decomp-permuter to close the last differences. When it matches, replace the
scaffold entry. Assets (LVGL images and fonts, protobuf descriptors, string
pools, model weights) are generated from declared sources with the
`assetgen_*` tools, or carried as declared data files with provenance.

### Phase 7 — Integration and byte equality (G2 P6/G6)

- Build every payload from source, repack it with `open_cfw.py` (G2), and
  compare against the locked identities. `diffoscope` explains any
  difference.
- When all six G2 payloads, the EVENOTA container and the R1 images are
  identical from a clean checkout on a clean host, the gate passes. Run it in
  CI so the result stays true.

### Phase 8 — Maintenance

- Move a submodule forward, rebuild, and diff to see exactly what an upstream
  fix changes. Keep each such change separate from reconstruction.
- Test changed images in the emulator (G2) or Renode (R1) before hardware.
  Hardware steps follow
  [`../g2/docs/reference/hardware-validation-notes.md`](../g2/docs/reference/hardware-validation-notes.md)
  and the R1 bootloader cautions in
  [`../r1/docs/security-and-bootloader.md`](../r1/docs/security-and-bootloader.md).
  Omitting the LF-clock settings has already bricked a ring once.

## Suggested order across payloads

Smaller payloads with mostly public upstream code go first. They validate the
toolchain identification and the matching pipeline cheaply.

| Order | Payload | Why |
| ---: | --- | --- |
| 1 | R1 bootloader (24 KB) | nRF5 SDK 17.1.0 Secure DFU is public, 304 functions are already named, and the compiler family (armcc 5) is known |
| 2 | G2 touch (34 KB) | PSoC 4000T PDL and CAPSENSE are public (pinned); small GCC build |
| 3 | G2 case (55 KB) | STM32CubeG0 and FreeRTOS are public; built with Keil MDK Arm Compiler 6, which is free for non-commercial use (`TC-ARMCLANG6`); this pins the Cube release |
| 4 | G2 EM9305 (212 KB) | about 1,450 functions already matched exactly to the EM9305 SDK v4.2 archives; the compiler is known |
| 5 | R1 application (646 KB) | nRF5 SDK and FreeRTOS are public; all 2,687 functions are already attributed to a provider |
| 6 | G2 codec (326 KB) | NationalChip `lvp_kws` is public; needs the C-SKY compiler release |
| 7 | G2 Even bootloader (149 KB) | IAR; shares libraries with the main application |
| 8 | G2 Apollo main (3.52 MB) | the largest; benefits from everything above |

G2 payloads can run in parallel under the workflow's task contracts once the
G2 gate allows it. The order above is a recommendation for where to start.

## Shortcuts and inferences

- **Upstream before decompilation:** every function matched in phase 2 skips
  phases 3–6 for that function except verification.
- **Evidence the images already give away:** version strings, source paths,
  assert and log strings, and SDK build IDs.
- **Existing seeds:** 12,500 naming seeds in `g2/symbols/`, the 2,972-function
  R1 ownership table, the EM9305 SDK archive matches, and the 7,449-function
  Apollo Ghidra export.
- **Compiler fingerprints from a few matched functions** fix the flags for
  everything else.
- **Link order and placement** from the stock layout yield object boundaries
  and translation-unit structure almost for free.
- **An assembly scaffold** keeps the build byte-identical throughout, so every
  step is measurable.
- **Shared code across payloads:** Apollo main and the bootloader share IAR
  runtime and Ambiq HAL code. The case and touch share Cortex-M0+ runtime
  code. Match once and reuse.
- **Parallel workers** follow the task contracts and model settings in
  [`../g2/workflow/prompts/README.md`](../g2/workflow/prompts/README.md),
  with independent reviewers for every output.

## Open blockers

| Blocker | Affects | Next step |
| --- | --- | --- |
| Licensed original compilers not yet installed. IAR 9.60.2 comes only via IAR MyPages (subscription); MetaWare T-2022.09 from MIPS/Synopsys or through EM Microelectronic; Arm Compiler 5 needs an MDK Professional licence | G2 Apollo and bootloader, EM9305, R1 | obtain and fingerprint them (phase 0); see [`tooling-availability.md`](tooling-availability.md) |
| G2 firmware emulator not reachable | dynamic testing | provide the repository URL or access; see [`../third-party/README.md`](../third-party/README.md#g2-firmware-emulator) |
| No public ARCv2 Ghidra module (PR 3006 is ARCompact only) | EM9305 | use IDA Pro's ARC module or `arc-elf32-objdump`, or extend the SLEIGH to ARCv2 in a project-owned fork |
| Exact IAR, C-SKY GCC and Cube releases unproven | several | phase 2 compiler identification |
| CAPSENSE release ambiguity (v3.0.1 vs v10.0.0) | touch | phase 2 function matching |
| Hardware facts still unmeasured | documentation, testing | [`hardware/README.md`](hardware/README.md) open questions |
