# SDK 5.2 source and archive mapping

Authenticated input: user-supplied AmbiqSuite 5.2.0 ZIP, SHA-256 `d9751350ef593b306838792a64a5620e4912c84ddf32dc9ff6aacd5cca049cad`, 30485 members. This is a reference SDK, not an authenticated stock build input. No code from the SDK was executed, and no proprietary library was newly extracted or registered in this follow-up.

## New inventory beyond the emulator's GPU audit

`ARCHIVES.json` records all 55 archive paths, sizes, SHA-256 hashes and embedded IAR compiler strings. The prior emulator report concentrated on the seven graphics archives and missing GPU simulator/ISA material. This inventory additionally covers board BSPs, HALs, CMSIS and crypto libraries.

| Archive family | Concrete new inventory | Bound and next target |
|---|---|---|
| Apollo510/510L/330P HAL and four BSP IAR archives | IAR 9.70.2.500; corresponding HAL/BSP C is included | Distinct compiled provider oracles. Only compare a currently owned, address-bound unresolved HAL/BSP body; existing 5.1 provider closures remain closed. New SDK version/compiler does not prove stock identity. |
| CMSIS M55 IAR DSP | IAR 9.60.4.438; 15 object groups enumerated in `CMSIS-IAR-MEMBERS.json`, including BasicMath, Filtering, Transform and CommonTables | Previously separate from the graphics audit. CMSIS/ARM contains 67 files but no implementation C/S files. A locked target must first be independently attributed to CMSIS DSP; compiler resemblance alone is insufficient. |
| Nema IAR extension | IAR 9.40.2.374 | Different producer from the main Nema IAR 9.70.1 archive. No new comparison performed; prior single-function mismatch and lineage boundary remain closed. |
| CryptoCell/mbedTLS | M4/M55 GCC/Keil archives; README names public CryptoCell branch and mbedTLS 2.16.2 plus Ambiq patches | Public reconstruction recipe exists for this SDK provider. Current canonical references/symbol search supplies no stock attribution to it. CryptoCell has mixed proprietary/BSD notices, so public hosting is not unrestricted licensing. |
| IAR DLIB/runtime | No separately named DLIB/runtime archive among all 55 archives | SDK does not supply the authentic IAR runtime source or producing link configuration. HAL/BSP compiler strings cannot fill that gap. |

`SOURCE-COUNTS.json` records OpenAMP (38 implementation files), TinyUSB (26), crypto (16 HAL/PAL files), and CMSIS/ARM (zero). Counts describe supplied source availability, not stock coverage or a complete source build.

## Verified public reference candidates

URLs/revisions were verified on 2026-10-09; metadata is retained in `UPSTREAM-PINS.json`. No root-index or submodule mutations were made.

| Public repository and pin | SDK basis / license evidence | Acquisition decision |
|---|---|---|
| ARM-software/cryptocell-312-runtime `91539d62a67662e40e7d925694e55bbc7e679f84` | Explicit README branch `update-cc110-bu-00000-r1p4`; archived official repository; mixed Arm-proprietary/BSD notices | Do not register wholesale as licensed OSS. No stock-bound target; no acquisition. |
| Mbed-TLS/mbedtls `d81c11b8ab61fd5b2da8133aa73c5fe33a0633eb` | Explicit 2.16.2 README/header; supplied version header Apache-2.0; repository-wide current metadata says Other | Candidate for a verified crypto-provider target only, with pinned-version license review and supplied patch provenance. No acquisition. |
| hathach/tinyusb `86ad6e56c1700e85f1c5678607a762cfe3aa2f47` | SDK 0.18.0 header; MIT upstream and supplied notice | New possible submodule candidate if stock USB implementation is established. Apollo510 board support in a SDK does not establish G2 inclusion. No acquisition. |
| ARM-software/CMSIS-NN `69823017d0973440e311dcf900b2162b17609fb0` | Apache-2.0; v6.0.0 tested only as a date-based candidate | Supplied NN header does not exactly match this pin. Version and stock inclusion unproven; do not register as exact provider. |
| packetcraft-inc/stacks `86372d84ef0386d8834ed036e613c8f2ded1ff16` | Explicit Cordio profile README URL in supplied SDK | Existing Cordio source family already registered; no duplicate acquisition or re-pin. Treat this as an SDK provenance lead, not a stock producing revision. |
| CMSIS DSP source | SDK arm_math.h declares 1.10.0; standalone CMSIS-DSP v1.10.0 ref lookup failed; existing registered CMSIS_5 5.9 pin provides the family source | Tested CMSIS_5 5.8.0 and existing 5.9 header hashes both differ from supplied header. Preserve raw mismatches in `PUBLIC-HEADER-CHECKS.json`; no guessed pin or duplicate download. |

OpenAMP and libmetal source is already supplied with BSD-3-Clause file notices; no additional download is justified absent a linked stock target. FreeRTOS, Cordio, CMSIS Core and other established families remain available in existing registered references. `PUBLIC-REFERENCES.json` inventories explicit upstream links from SDK reference/license/version documents.

## Stop conditions and remaining limits

No genuinely new, license-cleared public source acquisition has a demonstrated stock target in this bounded inventory. Therefore no source checkout or submodule is proposed for immediate registration. A later acquisition must name an unresolved locked function or data provider, show why existing registered sources cannot answer it, pin the actual useful upstream revision, and review that revision's license rather than GitHub's current metadata alone.

The SDK adds useful archived producer candidates, particularly CMSIS M55 IAR DSP, but does not remove private IAR runtime, Nema implementation, exact stock configuration, or whole-artifact coverage boundaries. Archive compiler versions are inventory evidence, not permission to bypass those boundaries. DSP, LZ4 and the Nema single-function result were not re-probed. No firmware sources, canonical ledgers, evidence seals, root index, devices or emulator code were changed.
