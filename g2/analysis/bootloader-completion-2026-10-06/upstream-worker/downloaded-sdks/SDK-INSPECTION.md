# Supplied SDK and toolchain inspection

Inspected 2026-10-06. Scope was local archive metadata, version/documentation and license terms only. Neither shell installer nor any toolchain executable was run. The supplied archive originals remain in Downloads; derived inspection artifacts are confined to this directory and `/tmp`.

## AmbiqSuite_R3.2.0

- Source directory: `/Users/kalani/Downloads/AmbiqSuite_R3.2.0`
- Version evidence: `VERSION.txt` and `mcu/am_sdk_version.h` identify `release_sdk_3_2_0-dd5f40c14b`.
- Platform evidence: the only MCU HAL source trees are `mcu/apollo3` and `mcu/apollo3p`. There is no `mcu/apollo510` tree or Apollo510 `am_hal_mspi.c`/`am_hal_mram.c`. The presence of an Apollo5 linker-config directory and conditional version macros does not supply a chip HAL implementation.
- Relevance: not an Apollo510 bootloader source replacement for the exact pinned HAL 5.1.0 candidate. Some generic/older Ambiq utilities may be useful as behavioral references, but they need separate target attribution.
- License: top-level `AM-BSD-EULA.txt` contains Ambiq's 2024 BSD-3-Clause terms and points to `docs/licenses` for third-party terms. No third-party bundles were imported in this task.

## T9305 EMB SDK installer ZIP

- Original: `/Users/kalani/Downloads/T9305_EMB_SDK_installer.sh.zip`
- ZIP SHA-256: `c618dc7abaae6ea5b462b77528dceacf5c58aaee2c49eb862262b7a5b7310daa`
- The ZIP contains one Makeself shell installer (2.4.2), labeled `EMM T9305 SDK Linux Installer`; its child entry point is `emm_T9305_installer_master.sh`. The member is 356,397,695 bytes. With the verified Makeself skip count of667, the gzip payload starts at member offset16,932, is356,380,763 bytes, and hashes to `8b987ce7d292fc86adbdf77fcae79f3ce672bd499206b81b2fa80fe46ffbb2a4`. Its decompressed tar stream is1,084,426,240 bytes with SHA-256 `57e3397cac620033c0ed5c269f225143735aee9e7f71f77370fe7196edf7e483`. The shell installer was not executed.
- **Correction:** the earlier gzip hash `dee7fc71...` and the entry/expanded-size counts in the prior static listing were derived from the wrong payload slice and are superseded. Do not rely on `T9305-TAR-MANIFEST.tsv` or the previously staged `em9305-v4.6-docs/` material as bound to the verified tar until they are regenerated/rechecked against the tar SHA above. The archive is identified as a mixed source-and-binary SDK package by ZIP-member metadata and the corrected tar stream; exact source/library counts remain pending a verified listing.
- Its Getting Started document identifies EM9305 and ARC EM7D, and gives MetaWare toolchain versions 2019.9, 2022.9 for EM, and EM-custom 2025.06-2. The archive includes a CMake ARCv2EM toolchain file and controller archives such as `lib_emb_controller.a` and CTE/ISO variants.
- Relevance: v4.6 is a plausible later SDK family for EM9305 work, but the repository's existing source-identity evidence is for v4.2. Archive filenames and SDK version do not demonstrate that v4.6 object libraries match the locked stock EM9305 image. No library payload hash, object comparison, code disassembly, or source import was performed. Further matching requires an authorized license review.
- License status: the user confirmed acceptance of the downloaded SDK licenses and authorized local SDK extraction. This supersedes the earlier note that the agreement had not been accepted. The installer remains unexecuted; no SDK source or library is claimed as verified/reused from this archive yet. Any extracted source must be bound to the verified tar hash above, and distribution/reverse-engineering restrictions remain governed by the accepted agreement.

## C-SKY toolchain ZIP

- Original: `/Users/kalani/Downloads/csky工具链.zip`
- Outer ZIP SHA-256: `450ef1b709c0563d4a423ef8a3f28c6ee80b19d9faae73ace321dfd43c27340c`
- Inner `csky-abiv2-elf-toolchain-v3.10.15.tar.gz` SHA-256: `0c6bb77fec9c11b1f7a9b8d73305d12598ca3d3d7527cec742be0a68a84b1688`
- Linux x86-64 subarchive `csky-elfabiv2-tools-x86_64-minilibc-20190929.tar.gz` SHA-256: `df33d1e101d9b0c1d4cc68286bb97a98e3a3095cf321f9e253f0ddf805d8d9f9`. The included Readme MD5 `14c5da904fdce5f5b943ae8218730e4e` matches.
- The vendor Readme identifies a bare-metal C-SKY ABIv2 compile/link/debug tool suite and explicitly lists CK804 among supported CPU families. The bundle contains platform subarchives for Linux x86-64, Linux i386 and Windows Mingw. GCC runtime paths identify GCC 6.3.0. The Linux compiler and objdump were inspected with `file` only: they are x86-64 Linux ELF executables, not macOS binaries; they were not run.
- Relevance: this supplies a concrete C-SKY ABIv2/CK804 toolchain candidate for GX8002 experiments, but it is not a GX8002/NationalChip SDK. No GX8002-specific headers, board support or libraries are identified by the package metadata. The target's exact compiler flags, runtime libraries and SDK/device configuration remain to be matched. The archive's included Readme does not provide a standalone EULA; licensing of each bundled component should be checked before redistribution.

## Inspection artifacts

- `T9305-TAR-MANIFEST.tsv`: static names, types and sizes from the EM SDK payload. It is not an extracted source tree.
- `em9305-v4.6-docs/`: selected license and SDK documentation used to identify the v4.6 release and its terms.
- `Readme.txt`, `changelog.txt`, `CSKY Option elf v2.txt`: C-SKY toolchain package metadata, not executable components.
- `csky-elfabiv2-tools-x86_64-minilibc-20190929.tar.gz`: nested C-SKY Linux x86-64 toolchain archive staged for inspection only; no toolchain installation or executable was run.
- `/tmp/t9305_embedded_payload.bin`: temporary Makeself gzip payload used to enumerate static archive metadata; it has not been installed or executed.
