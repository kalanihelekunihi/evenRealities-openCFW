# R1 bootloader and DFU security model (stock)

The stock bootloader is the nRF5 SDK 17.1.0 secure BLE bootloader (`pca10056_s140_ble` family)
at `0x000F8000`. Live-dump SHA-256 is
`566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b`. It contains 304 named
functions: 218 Nordic, 41 CryptoCell, 30 nanopb, 12 ArmCC runtime and 3 R1
(`r1/research/bootloader-reconstruction/README.md:8-28`).

Tags: **Proven**, **Strong**, **Inferred**, **Unverified**. Sources are repository-root paths
with line numbers.

## 1. Trust anchor and verification

| Item | Value | Tag | Source |
|---|---|---|---|
| Public key | raw P-256 `X‖Y`, 64 B at `0x000FD868` (bytes in `config-recovered/r1_dfu_public_key.c`) | Proven | `r1/research/bootloader-reconstruction/MEMORY-MAP.md:10`; `sdk-overlay/r1_dfu_public_key.c:9-22` |
| Signature | ECDSA-P256 / SHA-256 over the init command, verified before version policy | Proven | `r1/research/bootloader-reconstruction/SECURITY-MODEL.md:9-10` |
| Crypto backend | `nrf_crypto` with CC310_BL (`PkaEcdsaVerify` etc.) and a CC310_BL SHA-256 table | Proven | `research/bootloader-reconstruction/README.md:91,100-104` |
| Init packet | nanopb `dfu-cc.pb` decode. Rejects missing, wrong-type, wrong-length, hash-failing or signature-failing init commands | Proven | `SECURITY-MODEL.md:10-11`; `SDK-SOURCE-MANIFEST.md:56` |
| SoftDevice requirement | S140 7.2.0, FWID `0x0100` (in the signed init packet of the 2.2.6.0009 OTA) | Proven | `r1/research/decompilation/README.md:28` |
| Required signed app update | `NRF_DFU_REQUIRE_SIGNED_APP_UPDATE 1`; `NRF_BL_APP_SIGNATURE_CHECK_REQUIRED 0` (no boot-time app signature) | Strong | `research/bootloader-reconstruction/firmware-project/config/r1_recovered_config.h:32-35` |
| Dual bank | `NRF_DFU_SINGLE_BANK_APP_UPDATES 0` | Strong | same `:34` |
| HW version | `NRF_DFU_HW_VERSION 52` | Strong | same `:10` |
| Bonds | `NRF_DFU_BLE_REQUIRES_BONDS 0` (bootloader); buttonless app side `SUPPORTS_BONDS=0` | Strong / Proven | same `:11`; `r1/docs/correlation/NORDIC-SDK-CORRELATION.md:955` |
| DFU entry | GPREGRET (`0xB1` = `BOOTLOADER_DFU_START`) and buttonless only. Button and pin-reset entry are off | Strong | `r1_recovered_config.h:24-27`; `r1/tools/probes/r1_227_dfu_proof.S:1-20` |
| App data preserved | 36 pages below `0xF8000`, `NRF_DFU_APP_DATA_AREA_SIZE = 36*4096`; retail 2-byte delta at `0xFB54E` vs the SDK example | Proven | `sdk-overlay/r1_sdk_overrides.h:17-19` |
| LF clock | `nrf_clock_lf_cfg_t` bytes `00 10 02 01` at `0x000FDC68` (LFRC, 16, 2, 500 ppm). Using the PCA10056 LFXO default leaves the SoftDevice unable to start on R1 hardware | Proven (physical failure mode) | `r1_recovered_config.h:13-22`; `r1/docs/closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md:30-38` |
| Debug port | `NRF_BL_DEBUG_PORT_DISABLE 0`. On the tested legacy nRF52840, physical debug protection (APPROTECT) is disabled | Strong | `r1_recovered_config.h:37-38`; `SECURITY-MODEL.md:33-38` |
| Watchdog | bootloader WDT feed reduces the reload by 3200 ticks, with a 150-tick floor (`nrf_bootloader_wdt_*` `0x000FB198..0x000FB1C0`) | Proven | `research/bootloader-reconstruction/README.md:113` |

## 2. Retained security behaviour (stock)

Source: `SECURITY-MODEL.md:7-24`. Tag: Proven.

- The signed total size bounds DATA object creation. One object is limited to `0x1000` bytes.
- Fragment writes cannot pass the current object or the total image size.
- The full staged image's SHA-256 is checked independently before activation.
- Bank codes `0x01`, `0xA5`, `0xAA` and `0xAC` select activation of the application, SoftDevice,
  bootloader, or combined SoftDevice + bootloader.
- A valid settings backup (`0xFE000`) restores bank, progress, init command and validation state
  over a writable primary page (`0xFF000`).
- Application handoff (`nrf_bootloader_app_start_final` `0x000FAF56`) write-protects
  `0xF8000..0xFEFFF` and flash `0..` the page-aligned application end via ACL. It then resets
  privilege, loads the MSP and jumps to the vector table (`README.md:96`).

## 3. Audit findings (stock defects and weaknesses)

| Finding | Detail | Tag | Source |
|---|---|---|---|
| Debug-validation build | The image behaves as if built with `NRF_DFU_DEBUG_VERSION`. The installed-app CRC is not meaningfully compared (a mismatch is accepted), and version handling is relaxed for signed debug init packets. Package signature verification remains | Proven | `SECURITY-MODEL.md:33-38`; `r1/research/bootloader-reconstruction/REBUILDABILITY.md:58-61`; `r1_recovered_config.h:40-48` |
| Fail-open settings | If the primary settings are valid and the protected backup is invalid, the primary is accepted wholesale. The tested ring's backup was valid and identical | Proven (behaviour) | `SECURITY-MODEL.md:21-24` |
| Short BLE control-point ops | Operation-specific minimum lengths are not enforced, so a short packet causes an over-read | Proven | `SECURITY-MODEL.md:26-31`; `REBUILDABILITY.md:49-56` |
| Nested nanopb varint | An unterminated varint reads past the buffer | Proven | same |
| Advertising-name length | Unchecked against the 20-byte record | Proven | same |
| MBR primitives | Unauthenticated MBR copy/vector primitives exist, but persistence requires state in the ACL-protected MBR param page | Strong | `SECURITY-MODEL.md:40-45` |
| App channel-1 overwrite (2.2.7.0005) | A 244-byte channel-1 value overwrote the 36-byte legacy workspace, giving a controlled callback on retail hardware | Proven (audit) | `r1/docs/SECURITY.md:33-35` |
| App system handlers | Malformed declared-length paths and ACK-before-effect ordering. Examples: `powerControl` checks only length != 12; `systemSettings` ACKs before validating; `removeRingNotify` treats any nonempty frame as destructive | Proven | `r1/docs/SECURITY.md:38-40,144-153`; `r1/docs/reference/r1-capability-matrix.csv:29,197` |
| kv.bin | Snapshot selection uses class-0 magic only. Both sectors are erased at rollover, so a power loss can lose data | Proven | `r1-capability-matrix.csv:109` |
| sleep.db | Two transient append failures erase the whole sleep DB | Proven | `r1/docs/SECURITY.md:28-29` |

A byte-identical rebuild must reproduce all of the above exactly. Hardening is out of scope for
that target.

## 4. Application-side DFU path

- Buttonless DFU (`FE59` / `8EC90003-…`): the app callback `0x0005232C` handles prepare by
  disabling advertising-on-disconnect and disconnecting all links. Then SVCI 3 sets the advertising
  name, and the bootloader advertises `B210_DFU_<addr+1>`
  (`r1/docs/correlation/BUTTONLESS-DFU-EVENT-POLICY-CORRELATION.md:27-43`;
  `AUGUST-18-...VALIDATION.md:7-10`). Tag: Proven.
- System `otaStart` (`01/00/09`) is a phone-reachable DFU entry (`r1/src/r1_dispatch.c:911`). Tag: Strong.
- A Nordic DFU application ZIP is rooted at `0x27000` and declares SD requirement `0x0100`
  (`AUGUST-18-...VALIDATION.md:183-186`). Tag: Proven.

## 5. Physical DFU observation

The owner-signed 24,576-byte transition bootloader was installed through retail Secure DFU. The
transfer reached 0–100 %, but the unit went silent after activation. Root cause was an LFXO
clock configuration in that build (see section 1)
(`AUGUST-18-...VALIDATION.md:5-40`). This confirms that the retail bootloader accepts a correctly
signed bootloader-bank update. It also confirms that LF-clock configuration is critical for any
rebuilt bootloader.

## 6. Values that were openR1 choices (not stock)

- The `hardened` profile (no `NRF_DFU_DEBUG_VERSION`), bounded parsers, and the functional-model
  repairs (`REBUILDABILITY.md:49-61`).
- The owner-signing key, MCUboot and Zephyr full-flash replacement, and owner authorization
  (trust-on-first-pairing) (`r1/docs/SECURITY.md:42-123`). None of these exist in stock.
- The `transition` profile (`firmware-project/src/r1_transition_*.c`).

## 7. Open questions

- Exact UICR APPROTECT/DEBUGCTRL words (only in the untracked snapshot) and whether production
  units differ from the tested "legacy" ring.
- The bootloader settings page contents and version (`NRF_DFU_SETTINGS_VERSION=2` per the SDK
  example; not image-proven).
- The stock bootloader `sdk_config.h` beyond the recovered deltas, for example log configuration
  and `NRF_BL_DFU_INACTIVITY_TIMEOUT_MS`.
