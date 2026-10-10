# EM9305 SDK v4.2 provenance and configuration review — 2026-10-10

This review extends `g2/analysis/daybreak-source-frontier-20261010/` without changing its comparison result, the canonical coverage ledger, firmware sources, `.gitmodules`, or the `P2_EXECUTING` workflow state. It evaluates the newly visible mirror as a provenance and build-configuration input only. No firmware implementation was performed.

## Provenance result

The useful snapshot is GitHub commit `e4412bc98d4e76d441d1226ca3696e53cfae5f54` in `C0R3YY2/em9305_original`, tree `f5cb9ba00df71c2612d6d64cf39e05615a2feb64`. The GitHub commits API reports the commit signature as valid and verified. The repository is a two-commit, non-fork personal mirror created in March 2025; the first commit message says it copied an original EM9305 directory. It has no GitHub-detected repository license, tag, or upstream relationship.

That establishes an immutable public snapshot, but the GitHub signature authenticates the mirror commit, not publication by EM Microelectronic. The stronger content-level authenticity evidence is cumulative:

- coherent SDK v4.2 release notes, versioned EM-Core v4.2 images and headers, build scripts, generated maps, and MetaWare target configuration occur in one tree;
- EM copyright/license headers occur in the selected interfaces;
- the prior Daybreak comparison found 40 exact named bodies in the locked G2 EM9305 payload, including 18 bodies that discriminate v4.2 from the registered v4.6 image;
- current official EM material independently confirms that EM9305 software development uses the ARC EM7D MetaWare environment and that the SDK is distributed through EM's developer channel.

The correct provenance label is therefore **authenticated third-party historical SDK mirror with strong content corroboration**, not **official public upstream** and not proof of redistribution permission.

## Newly retained configuration evidence

Eight small, high-value files were fetched through commit-qualified raw URLs into ignored local vendor input storage at `third-party/local-vendor/sources/em9305-v4.2-public-mirror/`. Their Git blob IDs, sizes, and SHA-256 values are in `receipt.json`.

The files add these configuration facts:

1. `common/9305/tool_config/compile.arg` selects ARCv2 EM `core4`, code density, 16-bit LPC, 24-bit PC, radix-4 divide/remainder, swap, bitscan, `mpyd`, shift assist, barrel shifter, DSP2/complex/divsqrt/ITU/accshift, single-precision FPU options, timers 0/1, RTC, stack checking, CCM, and DMA.
2. `compile_mw_for_em.arg` selects the `em9305` TCF and a narrower feature set. The coexistence of these two profiles means a body match does not by itself select the exact compiler target profile used for that body.
3. `cmake/toolchains/arcv2em.cmake` binds C/C++/assembly to MetaWare `ccac` and archives to `arac`, optionally under `MW_INSTALL_PATH`. It does not pin a MetaWare release or optimization level.
4. `cmake/build_configs.cmake` defines ASIC plus DI03/DI04/DI05 build families, but its ASIC CFLAGS are empty. The file is identical to the registered v4.6 copy and is family evidence rather than a v4.2 discriminator.
5. `apexextensions.h` declares the custom APEX instructions `log2p1` as opcode 7/sub-opcode 0 and `log2p0` as opcode 7/sub-opcode 1, plus JLI-rebase, CRC, and FPU extension presence. This file is byte-identical to v4.6, so it authenticates the extension ABI but does not prove v4.2-specific arithmetic semantics or the producer's selected hardware profile.
6. `memory_map.h` and `config.h` differ from their v4.6 counterparts and are useful historical ABI/configuration comparators. They expose SDK linker-symbol contracts and module persistent/non-persistent memory structures, but do not provide concrete linker placements or the G2 producer's application configuration.
7. The v4.2 release notes identify the EMB Mango 2.2.0 controller update, Bluetooth qualification device `Q338654` / included design `244581`, PML calibration and SCA changes, and multiple radio/timing changes. These are useful hypotheses for version-specific behavior; release-note statements are not direct proof that each change is present in the locked G2 image.

## What the mirror can and cannot supply

The standard `emcore/bin/v4.2` subtree contains images, symbol maps, and 123 public interface headers. It does not contain source for the standard EM-Core image. The separate `emcore/custom/source` subtree is a small customization/application wrapper around SDK libraries, not the source of the standard controller image. The tree also contains generated build output and proprietary prebuilt archives.

Accordingly, the mirror is useful for:

- exact symbol/body attribution and v4.2 versus v4.6 discrimination;
- ARC target-feature and custom-instruction ABI recovery;
- SDK interface, memory-contract, release-change, and build-family evidence;
- locating candidate component source for bounded comparisons, provided each candidate is independently matched to stock bytes and its license is recorded.

It does not establish:

- the exact MetaWare release, optimization flags, link order, linker script, or producing project used for the G2 payload;
- source availability for the standard EM-Core image or proprietary Packetcraft/controller libraries;
- that the locked G2 payload is a simple relink of `emcore_standard.ihex`;
- accepted pseudocode coverage, implementation permission, or hardware behavior.

## Repository versus pinned-file decision

No submodule is justified. The mirror is a 128,017 KiB personal snapshot with two commits, no release tags, no declared repository license, no authenticated upstream relationship, and substantial generated/proprietary content. Its useful evidence is a small immutable subset. A gitlink would preserve the same commit identity but would also make the whole unlicensed mirror a repository dependency and imply maintainable upstream source history that does not exist.

The preferred treatment is:

- keep the mirror URL, commit, tree, Git blob IDs, SHA-256 values, and access date in tracked receipts;
- keep selected mirror bytes in the ignored vendor-input area;
- admit individual source files later only when a concrete source match requires them, with file-level license/provenance review and a content hash;
- do not add the full mirror, archives, generated binaries, or a gitlink to the tracked dependency graph.

This decision does not rule out a future submodule for a genuine maintained upstream repository with a clear license and source history. No such EM9305 v4.2 repository was authenticated in this pass.

## Gate boundary

The new configuration evidence narrows architecture and ABI assumptions and strengthens historical release attribution. It does not change the active workflow phase or open G3/G4. Any use in canonical P2 evidence still needs bounded admission and independent review against the locked payload.
