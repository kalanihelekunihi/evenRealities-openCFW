# Official release/package archaeology, 2026-10-09

This bounded continuation closes the official software-pack/release-index branch
left outside the two integrated shortcut reports. It acquires one useful small
historical manufacturer pack and official package metadata. It does not recover
target instructions, implement firmware, alter `.gitmodules`, or change P2
coverage, authenticated inputs, processor sources, workflow state, or gates.

## Confirmed new package facts

### Ambiq Apollo DFP: real system source, deliberately disabled startup

The official Keil index directs Apollo_DFP to `download.ambiq.com/packs`.
Current PDSC records Apollo510 RTM support in 1.5.0 (2025-04-02), updated package
1.5.2 (2025-05-01), and Apollo330P/Apollo510L RTM in 1.6.0 (2026-07-20).
The Apollo510 startup component remains version 1.5.2 even in the current 1.6.0
PDSC; that is a component identity, not proof of target production date.

Acquired the concrete historical archive
[AmbiqMicro.Apollo_DFP.1.5.2.pack](https://download.ambiq.com/packs/AmbiqMicro.Apollo_DFP.1.5.2.pack):
5,865,215 bytes, SHA-256
`1b63ff8fdddac6500670983e15a83212b6bc8d276f56c733a22bd4c66388e9eb`.
ZIP CRC validation passes all 103 members; nine selected source/header/PDSC
members are retained with member hashes in `inventory.json`. No pack installer,
compiler, flash algorithm, or bundled executable was run.

`apollo-selected/Device/Source/startup_apollo510.c:50` wraps the entire example
in `#if 0`. Its adjacent comment says SDK examples already provide startup and
the example is omitted to avoid duplicate definitions. This definitively
rejects a tempting shortcut: the pack is not an immediately usable producing
startup translation unit. Its disabled declarations/vector table can still be
used as an official naming and ordering comparator, with the disabled status
preserved.

`system_apollo510.c` is a real supplied CMSIS system source. It declares a 96 MHz
default `SystemCoreClock`, optional VTOR setup, FP/MVE CPACR access, EPU low-power
configuration, optional unaligned trap, loop/branch cache with DSB/ISB, optional
TrustZone SAU setup and optional SSRAM MPU configuration. The latter selects
attribute slot 7 and region 15 for `0x20080000..0x2037FFFF`. These are generic
pack defaults, not recovered stock behavior or new matching-byte claims.
The system file declares a 496-entry vector extern while the disabled startup
declares 256 entries; this inconsistency reinforces that the two files must not
be treated as a ready producing project.

The files retain Ambiq BSD-style notices and third-party-license qualification.
The pack PDSC selects the source through the ARMCC compiler condition; it does
not establish IAR compilation or the locked project's startup configuration.
No new Git submodule is proposed for this archive-only reference.

### Infineon CAT2 DFP does not contain a real startup provider

Acquired the official
[CAT2 PDSC](https://itools.infineon.com/cmsis_packs/CAT2_DFP/Infineon.CAT2_DFP.pdsc),
SHA-256 `f36bdeca8b500b09abe774eafbf8168d56eace258047c77f57664fb6bd42f5dd`.
Its release history records 4000T support in 1.2.0 (2023-03-01), subsequent
device and CMSIS flash-loader changes, and current 1.6.0. The sole startup
component explicitly calls itself dummy and says it emits a compiler error;
the only two component files are `README.txt` and `Device/Source/startup_error.c`.
It exists to satisfy PackChk's missing-startup warning. Thus matching 4000T
device support in this DFP supplies neither target CapSense generation inputs
nor a producing startup source. A full pack download was unnecessary.

The official [Configurator documentation](https://documentation.infineon.com/modustoolbox/docs/launching-mtb-capsense-configurator) states the CLI generates source from
`--config`, accepts `--output-dir`, and reports success via exit code. This
strengthens the missing-input boundary: the exact target `.cycapsense` plus
matching generator version/dependencies is useful; a DFP device match alone is
not. Current documentation was read through the web tool; direct archival
fetch returned HTTP 403 and is recorded in `acquisition.json` rather than
misrepresented as a retained document. The preceding official demo/XML report
already supplies the 6.20.0.5091 exemplar, so it was not cloned again.

### STM32 pack histories explain why latest-pack search loses HAL source

Official
[STM32G0 PDSC](https://www.keil.com/pack/Keil.STM32G0xx_DFP.pdsc)
records these distinct version namespaces:

| Device pack | Cube firmware | HAL | Metadata implication |
| --- | --- | --- | --- |
| 1.3.0 | 1.4.0 | not stated | Introduces G0B1 support |
| 1.4.0 | 1.5.0 | 1.4.2 | Historical firmware-containing generation |
| 1.5.0 | 1.6.0 | 1.4.5 | Historical firmware-containing generation |
| 2.0.0 | removed | removed | Removes Cube FW, Startup, HAL/LL components; moves to global generator |
| 2.1.0 | not bundled | not bundled | SVD/template/debug updates |

The 2.0.0 release is dated 2025-03-20. This is new finite acquisition knowledge:
searching current DFP components cannot locate historical HAL providers because
they were explicitly removed. The original STM32CubeG0 repositories already
provide the relevant source family, and the preceding report excludes the
specific 1.6.3 Timers MDK producing recipe. No duplicate Cube tree or old pack
was acquired without a new target-body/version discriminator.

The ARM CMSIS PDSC likewise states the 6.0.0 split: DSP/NN move into separate
packs, RTX5 moves into its own pack, and Arm Compiler 5 support is dropped.
An empty current-Core DSP search is therefore not evidence that historical DSP
source is unavailable. Existing pinned CMSIS_5 remains the stock-family lead.

The Keil ARM_Compiler 1.7.2 PDSC is a compiler-extension pack (retarget I/O,
Event Recorder support), not the Arm Compiler 6 executable/runtime distribution.
It cannot substitute for the producing compiler/runtime package.

## Official source availability refinements

### IAR DLIB: inspect exact installed product source package

The official [DLIB introduction](https://docs.iar.com/ewarm/10.1x/en/iar-c-c---development/the-dlib-runtime-environment/introduction-to-the-runtime-environment.html)
states that library source delivery depends on the product package, with binary
libraries in `arm/lib` and source in `arm/src/lib`. This improves the concrete
next acquisition request: obtain the exact producer-version product package
with its delivered DLIB source, not merely a license key or newer documentation.
The current online portal covers most releases after June 30, 2025 and directs
older documentation to installed software. Its Arm index is 10.10.x; it does
not prove that a 9.70.1 archive or older locked target runtime uses the same
source/configuration. No product download, entitlement change, activation, or
private-source extraction occurred. Existing 5.2 IAR Nema archive evidence
already establishes an object producer and does not itself supply Nema C.

### NationalChip: precise historical TWS source acquisition route

Fresh official GitHub release API responses for `lvp_kws`, `lvp_sed`, and
`lvp_aiot` are empty arrays. No hidden release attachment was acquired; the
unchanged public branch/tag work in the prior report was not repeated.

The official [GX8002 development guide](https://document.nationalchip.com/en/software/lvp/SDK%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97/SDK%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/%E6%90%AD%E5%BB%BA%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83/)
explicitly identifies a private GitLab SDK, a sales/project-manager access
process, and example repository `git@gitlab.com:nationalchip/lvp_tws.git`.
It documents a Linux C-SKY ABI-v2 minilibc toolchain rather than a generic
current compiler installation. This is a more precise unavailable-input lead
than another GX8002D application repo: request the historical GX8002B TWS SDK
and matching compiler/model package, then authenticate it. The public example
clone URL supplies no immutable pin or target attribution. No credentials,
SSH access or contact/message was attempted.

### EM9305 and newer Ambiq radio firmware

The official Keil index has no EM9305 entry. Exact vendor-domain historical SDK
searches surfaced the existing official EM9305 datasheet rather than a v4.2
source archive. That document directs SDK acquisition to EM Microelectronic;
this is bounded search visibility, not universal absence proof. Existing v4.6
ELF wrapper raw mismatches were not repeated or normalized here.

The official Ambiq HAL release API names one release
`v4.3.0-ambiq.v1.0.0`, published 2026-08-31, with no release assets. Its notes
describe a bundled controller firmware/check-update flow and NemaGFX/NemaDC
refactoring. This is the already-inspected `1577f6e…` public branch, not a new
historical EM9305 source package. A later bundled executable cannot satisfy the
source-build goal, so no controller blob was downloaded. No new Git source
merits a proposed submodule or pin in this pass.

## Strong inferences and finite stopping conditions

Package indexes add useful negative discriminators and acquisition vocabulary,
but no package inspected supplies a missing target-specific producing project.
Public package source discovery for these bounded indexes is closed until a
new source/version/body discriminator or authentic private input appears.
This does not close whole-artifact P2 recovery or first-party firmware semantics.

Recommended next actions are input-driven: inventory matching IAR installation
`arm/src/lib`; obtain historical EM9305 v4.2 source/providers and exact MetaWare
project; obtain GX8002B TWS SDK/compiler/model archive; obtain target CapSense
configuration and generator. Compare newly supplied sources only against
authenticated target spans, preserving license/provenance and compiler identity.
The acquired Apollo system source is ready as a named comparator, not accepted
coverage. Original-byte analysis and independent corpus review remain separate.

## Replay and artifact inventory

`acquire.py` records original/final official URLs, status, byte size and SHA-256.
`inventory.py` parses release/component/file metadata, records pack-index
matches, validates ZIP CRCs and extracts only selected source members into this
owned directory. `acquisition.json` and `inventory.json` are machine-readable
evidence; no firmware compilation or vendor executable occurs in either script.
Replays contact moving official indexes, so a later result may differ; retain
this snapshot before replay. All writes in this pass are confined here.
