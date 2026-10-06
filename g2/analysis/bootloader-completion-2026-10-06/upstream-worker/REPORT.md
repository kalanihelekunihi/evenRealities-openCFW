# Apollo bootloader upstream-source and rebuild feasibility

Inspection date: 2026-10-06. Scope: source attribution, pinned upstream source
acquisition, and byte-identical rebuild prerequisites for the Apollo510B Even
bootloader in the locked `s200_v2.2.6.10` artifact. The user's current request
authorizes C completion; this report identifies reuse evidence and build
blockers without imposing the superseded historical phase gate.

## Finding

There are strong, concrete upstream source opportunities for the open library
portions of this bootloader: littlefs 2.10.1, EasyLogger 2.2.99, TLSF v3.1
family, and AmbiqSuite 5.1.0 MSPI HAL; FreeRTOS/CMSIS-RTOS2 is attributable by
family but its bootloader revision/configuration is unresolved. Their pinned
submodule commits are already recorded in `g2/docs/reference/libraries.md`,
but the corresponding worktrees are empty/uninitialized in this execution
environment. The main blocker is not simply obtaining these source trees:
the bootloader is an IAR-built image, and neither IAR EWARM (`iccarm`/`ilink`)
nor its project/linker inputs and exact build configuration are available.
Consequently upstream code can ground behavior and candidate source reuse,
but cannot yet produce a byte-identical bootloader. Current evidence does not
justify promoting the main application's FreeRTOS pin or build settings to
the bootloader.

## Locked target and available analysis

- Target payload: `apollo_bootloader`, 148,599 bytes, SHA-256
  `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, raw
  image linked at `0x00410000` (`g2/workflow/target.json`,
  `g2/docs/reference/firmware-formats.md`, `g2/docs/reference/memory-map.md`).
- Ghidra 12.1.4 raw export is present at
  `g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/`: 903
  function entries, 849 decompilations, 292 seeded names; 54 functions failed
  decompilation. It is raw evidence, not independently reviewed pseudocode
  (`g2/docs/reference/decompilation-status.md`).
- The memory map anchors bootloader code and data, including littlefs public
  API at `0x00415128–0x0041531C`, NOR driver at
  `0x00420002–0x00420F70`, filesystem block callbacks at
  `0x004212D8–0x004213D8`, DFU task at `0x0042DE58–0x0042E104`, and platform
  bring-up at `0x00430000–0x004301D6` (`g2/docs/reference/memory-map.md`).
  The executable image spans `0x00410000–0x00434477`; the linked image must
  also preserve its exact vector, constants, data, and padding layout.
- The device also has the Ambiq secure bootloader at
  `0x00400000–0x00410000`. That 64 KiB SBL is explicitly absent from EVENOTA
  (`g2/docs/reference/memory-map.md`); it is an external dependency for full
  device boot behavior, not bytes to invent or append to this payload.

## Upstream reuse candidates

| Bootloader component | Concrete upstream source and match evidence | Reuse status and remaining discriminator |
| --- | --- | --- |
| littlefs | littlefs v2.10.1, pinned commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`; v2.10.1 attribution is proven from a uniquely identifying assertion-line fingerprint. Bootloader geometry and `lfs_config` at `0x00431070` are recorded; public API subset starts at `0x00415128`. See `g2/docs/reference/libraries.md` and `g2/docs/reference/memory-map.md`. | Exact pinned core (`lfs.c/.h`, `lfs_util.c/.h`) and license are acquired under `g2/analysis/bootloader-completion-2026-10-06/upstream-worker/littlefs/`; provenance and host/ARM compile results are in its `PROVENANCE.md`. Need bootloader's exact `lfs_config`, compile flags, IAR version, selected translation units, and link order before claiming object/image byte equivalence. Main's configuration is not automatically the bootloader configuration. |
| EasyLogger | EasyLogger core 2.2.99, pinned `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; source identity is byte-stable over the recorded range beginning at `cd93d9c7`. Bootloader contains only `elog.c` and `elog_utils.c`, with synchronous channel-1 sink. `g2/docs/reference/libraries.md` §2. | Concrete core reuse candidate. Worktree is empty. Sink glue/configuration and IAR translation-unit settings must be recovered; do not import main's async glue into this bootloader. |
| TLSF | TLSF v3.1, exact pin `deff9ab509341f264addbd3c8ada533678591905`; the header and README identify 3.1. Target control-list dimensions (24×32), 32-bit control size (`0xC74`), allocator initialization sequence, and `0x70800` arena match this exact source structurally. Evidence and a compile-time Cortex-M55 layout assertion are in `upstream-worker/tlsf/PROVENANCE.md`. | Strong source/layout match; no IAR object comparison. Source and license are copied into the owned worker directory. Need bootloader-specific wrapper/error/logging code, compile settings, and thread-safety boundary recovered. |
| AmbiqSuite MSPI HAL | AmbiqSuite 5.1.0 family, pinned project source `ambiqhal-apollo510` commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`; bootloader `am_hal_mspi_interrupt_clear` identified as an exact translation-unit leaf, while interrupt-service and power-control code are attributed in the inventory. `g2/docs/reference/libraries.md` §2. | Concrete reuse candidate for source-level provenance. Both Ambiq HAL/SDK worktrees are empty. Need exact file revision and generated config/macros; matching a leaf alone does not establish whole-object or whole-image equivalence. |
| FreeRTOS kernel and CMSIS-RTOS2 wrapper | Bootloader has FreeRTOS plus CMSIS-RTOS2-style wrapper (family strong), but the reference explicitly says revision is not inherited from main. Main application pins FreeRTOS V10.5.1 at `def7d2df2b0506d3d249334974f51e427c17a41c` and CMSIS-FreeRTOS `d213f261b5be6bb29a7cce8b84071706b72f4d53`; those are not established as bootloader pins (`g2/docs/reference/libraries.md` §1–2). | Potential source families only. Both worktrees are empty. First recover bootloader revision and configuration: the existing main pin is not a grounded exact candidate for the bootloader. |
| MX25U25643G NOR driver, DFU logic, board startup, RTOS glue, private platform code | Authenticated-image behavior is located in the memory map, but the inspected references do not attribute all these bodies to a complete public upstream source tree. | Treat as local source-reconstruction work unless a source match is independently established. Public peripheral headers or an SDK with a similarly named driver do not prove exact vendor source identity. |
| IAR runtime | IAR TLS/thread-pointer leaf, C11 constraint handler string/dispatcher (`0x00422590`), `memchr`, double helpers, 64-bit divmod, and qsort/heap-sift fingerprints establish IAR runtime family (`g2/docs/reference/toolchains.md` §2). | Proprietary runtime, not a reusable public SDK. It requires the matching IAR runtime libraries and ABI/configuration, or complete source-level replacements whose compiler output is validated against the locked image. |

The gitlinks are pinned but unpopulated: `git submodule status --recursive`
reports these upstreams with a leading `-`, and direct inspection finds empty
directories for `third-party/upstream/{littlefs,tlsf,freertos-kernel,
cmsis-freertos,easylogger,ambiqhal-apollo510,ambiqsuite-sdk}`. No network fetch
was attempted for the submodules; the separately downloaded littlefs snapshot
is described above. Tool discovery found only `/usr/bin/clang`; `iccarm`,
`iarbuild`, `arm-none-eabi-gcc` were not on PATH, and the repository contains
no `.icf`, `.ewp`, or `.eww` project/linker files. This establishes local
unavailability, not whether the user has a separate licensed installation.
Do not use the main FreeRTOS/CMSIS pins as bootloader source until a
bootloader-specific match is established. The Ambiq SDK link is a source/header
candidate; current evidence does not establish that it contains private/
pre-release bootloader inputs or IAR archives.

## Exact missing prerequisites for a byte-identical build

1. **Exact compiler/runtime toolchain.** Obtain a licensed IAR EWARM installation
   compatible with the image. The family is proven/strong; release is unknown,
   with 9.20 as the practical Cortex-M55 floor and 9.60.2 a candidate, not a
   proven selection. Determine DLIB/CLIB variant and math archive, object-level
   optimization/ABI flags, and runtime library version by binary comparison.
2. **Original build recipe.** Recover or independently infer the bootloader
   `.icf`, boot/reset/startup inputs, initialized-data/compression table,
   selected objects, archive member/link order, section sorting/alignment,
   garbage collection, and fill/padding rules. No such project/scatter file is
   in the checked repository. IAR-style initialization is supported by runtime
   evidence; the exact layout and options are not.
3. **Per-library source/config binding.** Populate the recorded upstream
   gitlinks and bind exact files plus bootloader-specific macros/configuration
   to target function ranges. For FreeRTOS, identify its revision first. For
   TLSF, upgrade family attribution to exact source. Preserve separate source
   and build evidence for code compiled into this bootloader.
4. **Remaining source and data attribution.** Identify vendor-only/private
   HAL, flash driver, wrappers, build-generated tables, runtime, and all
   non-code image bytes. The open export's 54 failed-decompilation functions
   and all data/padding still require complete whole-image pseudocode/accounting
   and subsequent source coverage.
5. **Comparison harness and exact end-to-end proof.** Build the entire raw
   bootloader at `0x00410000`; compare the full 148,599 bytes, including vector
   table and every data/gap/tail byte, against the authenticated target hash.
   Only then can the repacked EVENOTA bundle be checked for the locked bundle
   hash. Matching isolated leaves or behavioral equivalence does not close this
   gate.

The Ghidra bootloader export is raw and unreviewed, with 54 entries lacking
decompilation. This is an evidence-coverage fact, not a restriction on the
user-authorized C work. Keep pseudocode coverage, source completeness, and
byte-equality results distinct while that work proceeds.

Commit pointers checked directly with `git ls-tree HEAD`:

| Path | Pinned commit |
| --- | --- |
| `third-party/upstream/littlefs` | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` |
| `third-party/upstream/tlsf` | `deff9ab509341f264addbd3c8ada533678591905` |
| `third-party/upstream/freertos-kernel` | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| `third-party/upstream/cmsis-freertos` | `d213f261b5be6bb29a7cce8b84071706b72f4d53` |
| `third-party/upstream/easylogger` | `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| `third-party/upstream/ambiqhal-apollo510` | `5efc0228528a8adce5eae0d226fac85d2551eb3b` |

## Source references

- `g2/workflow/README.md`, `g2/workflow/PROCEDURE.md`: phase and corpus-freeze
  gates.
- `g2/docs/reference/toolchains.md` §2: IAR/runtime and uncertainty.
- `g2/docs/reference/libraries.md` §1–2: versions, commits, licenses, match
  strength, and bootloader-specific revision warning.
- `g2/docs/reference/decompilation-status.md`: raw export counts and review
  status.
- `g2/docs/reference/firmware-formats.md`, `g2/docs/reference/memory-map.md`:
  target hash, base, sizes, and address anchors.
- `g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/RUN.json` and
  `census.txt`: raw-analysis identity and function counts.
