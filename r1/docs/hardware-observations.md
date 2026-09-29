# R1 physical and field observations

These are observations from owned retail rings. They are compatibility evidence for stock
behaviour. Some were taken on later application versions than the locked 2.2.6.0009 artifact.
Sources are repository-root paths with line numbers. Tags: **Proven** (observed/measured),
**Strong**, **Inferred**, **Unverified**.

## 1. Firmware and hardware versions seen

| Version / identity | Where observed | Use | Tag | Source |
|---|---|---|---|---|
| App `2.2.6.0009` | OTA payload (locked artifact) | analysed image, oracle | Proven | `r1/research/decompilation/artifact-inventory.csv:2` |
| App `2.2.7.0005` | owned ring used for the security audit and on-device read-only probes (bootloader/UICR/APPROTECT/NFCT/ST25 dumps, DFU-entry proof) | probes; live bootloader/UICR capture 2026-08-10 | Proven | `r1/tools/probes/r1_227_uicr_dump.S:1-7`; `r1/tools/probes/r1_227_approtect_runtime_dump.S:1-5`; `r1/docs/SECURITY.md:33-35` |
| App `2.2.8.0002` | ring `EVEN R1_B56EE2` (BLE validation 2026-08-18); MBR-config probe | cross-revision behaviour | Proven | `r1/docs/closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md:94-104`; `r1/tools/probes/r1_228_mbr_config_dump.S:1-8` |
| Hardware string `603MV1.9.3` | deviceInfo slot 2 on 2.2.8.0002; embedded in 2.2.6.0009 (CmBacktrace init args) | Bravechip BCL603M module family | Proven | `AUGUST-18-...VALIDATION.md:96-100`; `r1/docs/correlation/CMBACKTRACE-CORRELATION.md:39-40` |
| Product code `B210` | build path `product/B210/app/_build/B210_Application`; DFU name `B210_DFU_…` | – | Proven | `r1/docs/PROVENANCE.md:83`; `AUGUST-18-...VALIDATION.md:9` |
| Live bootloader | 24,576 B, sha256 `566cd2a5…ab8b` (captured 2026-08-10) | oracle | Proven | `r1/research/decompilation/artifact-inventory.csv:3` |

A later owner-authorized ACE read captured all 216 live pages `0x27000..<0xFF000` and the
0x308-byte UICR. The record says "the live application and owner bootloader matched their
authenticated reference images byte-for-byte". The live settings store was classified as exactly
two Nordic FDS data pages plus one swap page
(`r1/docs/closures/AUGUST-18-PHYSICAL-VALIDATION-BLOCKER.md:18-41`). Tag: Proven (record);
the captured bytes are not tracked.

## 2. BLE observations on 2.2.8.0002 (macOS CoreBluetooth, iPhone nRF Connect)

Source: `r1/docs/closures/AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md`

| Observation | Value | Lines |
|---|---|---|
| Advertising | connectable; name `EVEN R1_B56EE2`; company id `0x5245`; 23-byte manufacturer element | 92-94 |
| Advertising interval (host-observed) | 1.006–15.052 s between distinct observations (mean 9.447 s), consistent with slow mode. Not an on-air measurement | 106-112 |
| GATT | exactly two primary services: BAE8 (4 characteristics) and `FE59` (`8EC90003-…` write/indicate) | 116-128 |
| Host write limits | CoreBluetooth max write 512 with response, 20 without response. Not a proven ATT MTU | 130-133 |
| Role gating | without `pairAuth` the status request gets no reply. `pairAuth` → success (1 zero byte) + unsolicited type-2 `pairAuth` model + unsolicited device status | 198-220 |
| `pairAuth` round-trip | 57.9, 61.2, 92.9 ms | 207-208 |
| Bonding | macOS retained the bond ("My Devices"); reconnection needed no prompt; the bond alone does not restore the phone route | 208-220 |
| Sequential status | 3/3, 0 drops, 37.975–69.351 ms (mean 55.581) | 222-229 |
| Burst of 20 status requests | 20/20 in order, 59.740–478.024 ms (mean 293.226) | 231-236 |
| CCCD toggle | disable/re-enable then 3 replies at 57.8/157.7/99.9 ms | 243-254 |
| Disconnect under load | 4/20 delivered before disconnect; readvertised; reconnect 3.123 s; `pairAuth` 91.452 ms | 256-266 |
| Channel 1 + channel 2 interleave | 20 ch1 opcode-`0x89` frames (valid flag 0) + 20 ch2 status: 20/20 ch2, 0 ch1 replies, 179.7–1318.1 ms | 274-304 |
| One host connection | retail app permits a single host connection at a time | 22-24 |
| nRF Connect classification | "DFU: Yes (nRF5 SDK)" | 165-168 |

## 3. DFU and bootloader observations

| Observation | Tag | Source |
|---|---|---|
| The ACE DFU request (244 B) triggered Secure DFU; the DFU advert name was `B210_DFU_B56EE3` (address + 1) | Proven | `AUGUST-18-...VALIDATION.md:7-10` |
| Secure DFU accepted an owner-signed 24,576-byte bootloader image (0–100 %, success). The ring then stopped advertising. Cause: LFXO default instead of the stock LFRC config `00 10 02 01` at `0x000FDC68` | Proven | same `:11-38` |
| The earlier DFU-entry proof on 2.2.7.0005 wrote GPREGRET `0xB1` and reset | Proven | `r1/tools/probes/r1_227_dfu_proof.S:1-20` |
| The retail bootloader programs MBR config words at `0xFF8` / `0xFFC` after S140 is installed | Strong | `r1/tools/probes/r1_228_mbr_config_dump.S:1-8` |
| No SWD/serial debug endpoint is exposed over BLE; no flash/UICR read characteristic | Proven | `AUGUST-18-PHYSICAL-VALIDATION-BLOCKER.md:114-118`; `AUGUST-18-...VALIDATION.md:126-128` |
| APPROTECT disabled on the tested legacy nRF52840 | Strong | `r1/research/bootloader-reconstruction/SECURITY-MODEL.md:33-38` |

## 4. Physical characteristics not yet measured

The following are listed as capture-gated (`r1/docs/reference/r1-capability-matrix.csv` rows
R1-049, R1-082..R1-088, R1-101, R1-102, R1-200):

- the installed accelerometer variant (LIS2DW12, BMA456W or QMA6100);
- optical geometry;
- battery divider transfer function;
- PMIC rail semantics;
- on-air advertising interval;
- negotiated MTU and PHY;
- `i2c_3` purpose;
- the `mcu_reset_irq` and `pmic_irq` aliases.

## 5. Units referred to

- `B56EE2`: retail 2.2.8.0002, later used destructively. It went non-advertising after the
  transition-bootloader DFU and needs power-cycle or SWD recovery
  (`AUGUST-18-...VALIDATION.md:15-20`).
- An unnamed owned 2.2.7.0005 ring: audit and probes.
