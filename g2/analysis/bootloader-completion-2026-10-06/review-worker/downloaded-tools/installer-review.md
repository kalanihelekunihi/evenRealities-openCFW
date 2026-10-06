# Supplied SDK installer review (data-only)

Date: 2026-10-06. Scope: inspect the supplied Windows installers as files, assess metadata and safe contents, and check vendor statements about current platform support and licensing. No installer was executed; no tools were installed or activated; no Wine/VM or security setting was changed; no activation key or private license file was accessed. This is an independent, bounded review, not a recommendation to accept any license.

## File identity and format

| File | Size | SHA-256 | `file` result | PE product metadata |
|---|---:|---|---|---|
| `/Users/kalani/Downloads/ewarm-10.10.2.26960.exe` | 1,896,763,200 bytes | `21d79a2df33975b7263638072a3c30b856f7adbe67d5a621c5e6644645b1fb4c` | PE32 GUI, Intel 80386, Windows | IAR Systems; `IAR Embedded Workbench for Arm Installer`; file/product 10.10.2.0; original filename `ewarm-10.10.2.26960.exe`; internal build 198337 |
| `/Users/kalani/Downloads/MDK543a.exe` | 893,488,656 bytes | `5702ed2093680932da3466134885b2141297099df106e5090c38f65a9510b7ca` | PE32 GUI, Intel 80386, Windows | Arm & Keil; launcher is `uVision Setup`, file/product 1.39.0.7. This is setup-launcher metadata, not the MDK package version. The contained manifest identifies Arm Compiler for Embedded 6.24. |

These hashes identify the exact local files examined; no vendor-published checksum or download-chain provenance was confirmed, so they do not authenticate origin.

## Signature evidence and limit

Both PE files contain a PE `SECURITY` directory and a PKCS#7 `WIN_CERTIFICATE` record (EWARM: offset `0x710e2678`, size 10,440; MDK: offset `0x354164f8`, size 10,520). The embedded certificate material contains publisher-named leaf subjects `I.A.R. Systems AB` and `Arm Limited`, respectively, and issuer/chain certificates (DigiCert for IAR; GlobalSign for Arm).

This establishes that certificate-table data is present and names those publishers. It does **not** establish a valid Authenticode signature, intact PE content, trusted chain, timestamp validity, revocation status, or that the files came from the vendors. A full Authenticode verifier and trusted/revocation data were not available in this review; OpenSSL's generic CMS verification did not accept the Authenticode SPC content encoding. Arm's official download page also warns that its installers do not include protection against tampering and advises using a trusted directory. Treat the installer files as unverified until independently checked through the vendor's supported channel.

## Safely enumerable contents and license text

7-Zip 26.03's listing of the IAR setup exposes PE resources and one opaque payload (about 1.896 GB); it does not expose the packaged IAR product files, headers, library maps, or setup-specific EULA in a directly reviewable archive listing. Extracting visible version/string resources only yielded launcher metadata. Thus the exact IAR installer EULA/order terms were **not** reviewed. Do not infer that extracting/running or using it is permitted; obtain and review the applicable terms from IAR before use.

The Keil setup is recognized as containing a ZIP payload. Listing it exposes 7,220 files in 225 directories (about 3.27 GB expanded); file contents can be read/extracted selectively with archive tools without launching the setup. The included `ARM/ARMCLANG/sw/manifest.txt` identifies Arm Compiler for Embedded 6.24 (`armclang`, `armlink`, `armasm`, `armar`, `fromelf`). The included `license_terms/license.rtf`, `supplementary_terms.txt`, and `redistributables.txt` were read as data only; no license was accepted.

The Keil EULA says use is subject to acceptance and applicable order/license documentation; it describes a license rather than a sale and sets license-key, term, and seat restrictions. The included supplementary terms limit the free MDK-Community Edition to individual consumers, academic institutions, and organizations below the stated staffing/revenue thresholds, and bar community use in providing products or services to third parties. The included non-commercial terms restrict the allowed use and distribution of outputs. These are edition-specific conditions: this inspection does not determine which edition, entitlement, or order terms apply to the user. The redistributables document permits only listed components, subject to conditions including redistribution as object code within a qualifying application with substantial additional functionality; it is not a general right to redistribute the compiler/IDE. Review the exact current license/order terms for the intended use before relying on any of these permissions.

## Platform and candidate-tool implications

The supplied `.exe` files are Windows PE installers. The current IAR EWARM page describes the IAR embedded development platform IDE as native on Linux and Windows, and does not list macOS. IAR's evaluation page indicates that the Arm EWARM evaluation is Windows-only; its page describes 14-day evaluation access and associated restrictions. IAR's current Linux offering may provide an option for Linux, but no supported native macOS workflow is established by these sources.

Arm/Keil's current product download page lists MDK-Arm 5.43a (August 2025), says products use a license-management system, and explains that without a current license the product runs as Lite/Evaluation with limitations; evaluation editions do not require PSN/LIC. It warns that installers lack tamper protection. The supplied MDK installer contains Arm Compiler 6.24. Its Windows PE form and µVision setup are not a native macOS IDE/compiler workflow. The available package files/docs can be inspected safely as archives, but that does not make the IDE usable natively on this Mac.

The machine has Apple clang 21.0.3 and GNU binutils `ld` 2.47 available; the repository already uses a clang/Arm-linker workflow. These are viable native-hosted components for an open cross-build, but they are not IAR or Arm Compiler 6.24 and cannot be treated as byte-identical substitutes without build and binary evidence. Arm GNU Toolchain is another distinct toolchain option; official download routing points to Arm/GitLab, but the current page was not machine-readable in this inspection, so no release/platform claim is made here.

Most importantly for the firmware reconstruction: the supplied IAR installer is **10.10.2**, while the separately investigated stock-build candidate is **IAR 9.60.2**. The newer installer is useful only for investigating its own current toolchain and associated package collateral. Its presence does not satisfy or prove the exact historical 9.60.2 compiler, license, device-pack, or byte-reproduction requirement. Likewise MDK 5.43a / Arm Compiler 6.24 is a different compiler profile.

## Official references checked

- [IAR EWARM/platform page](https://www.iar.com/ewarm) — native Linux and Windows platform statement.
- [IAR free trials](https://www.iar.com/embedded-development-tools/free-trials) — trial duration/conditions and platform-specific evaluation notes.
- [IAR 10.10.x CMSIS/IDE documentation](https://docs.iar.com/ewarm/10.1x/en/ide-project-management-and-building/using-an-external-build-system/working-with-cmake-and-cmsis-toolbox-projects/adding-a-cmsis-toolbox-project-to-the-ide.html) — Linux/Windows workflows.
- [IAR Build Tools for Arm](https://www.iar.com/knowledge/learn/cross-platform-build-tools-for-arm/) — Linux and Windows host availability for build tools.
- [Keil product downloads](https://www.keil.com/download/product/) — current MDK listing, licensing/evaluation notes, and tamper warning.
- [Keil/Arm product overview](https://www.keil.com/) — product/component overview.
- [Arm GNU Toolchain downloads](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads) — official download route; redirected to a page that required JavaScript/anti-bot verification, so no detailed download claims were derived from it.

## Reproducibility / actions

Commands used included `file`, `shasum -a 256`, 7-Zip list/extract-to-stdout, PE header/certificate-table parsing, and OpenSSL certificate extraction. Archive extraction was limited to selected small metadata/license files and streamed to a temporary path; the installers themselves were never launched. No software was installed. The result is suitable for deciding what further vendor-sourced verification is needed, not for treating either installer as authenticated or licensed for a particular use.
