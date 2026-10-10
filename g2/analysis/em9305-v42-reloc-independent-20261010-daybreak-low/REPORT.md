# EM9305 v4.2 independent relocation-aware comparison — 2026-10-10

This is a bounded independent review of the authenticated v4.2 standard IHEX/SYM pair against the locked G2 EM9305 payload. It preserves `P2_EXECUTING` and changes no canonical symbol ledger, gate receipt, firmware source, vendor input, gitlink, or shared analysis project.

## Result

The pass independently reproduces all 40 exact v4.2 named-symbol byte matches reported by `../daybreak-source-frontier-20261010/`. Each signature occurs once in the complete locked payload. Thirty-five matches land on a canonical symbol boundary with the same name. `RF_RfChannel2BleChannel` lands exactly on the canonical `llConvertRfChanToChanIdx` record; this is compatible with identical conversion-table or helper content but does not justify replacing the canonical name. Four matched v4.2 symbols (`cRF_MacTiming`, `cRF_config`, `cRF_powerLevelConfig`, and `gIRQ_PRIORITY`) have no same-span canonical record and are configuration/data-shaped symbols, so the earlier phrase “40 functions” is too broad. The defensible class is **40 named symbol bodies/objects**, with executable-function status determined separately.

The release comparison also reproduces all 18 v4.2 discriminators:

- Seven same-sized v4.6 symbols contain different bytes: `IRQ_Cleaning`, `NVM_BeforeOperation`, `PML_Dbm2PmlRfPower`, `RF_Ln`, `RF_RfChannel2BleChannel`, `RF_TestModeStart`, and `gIRQ_PRIORITY`.
- Eleven v4.6 same-name symbols have different sizes: `NVMEntry_CopyJLITable`, `NVM_AfterOperation`, `ProtTimer_StoreConfig`, `RF_BleChannel2RfChannel`, `RF_GetOutputPower`, `RF_SetMacTiming`, `SleepTimer_SetWakeupTime`, `VoltMon_UpdateFlags`, `llPrbs9Payload`, `receiverTestCheckParameters`, and `scan15_4CheckParameters`.
- The remaining 22 exact objects are byte-identical in same-sized v4.6 symbols and identify common provider lineage, not v4.2 specifically.

The apparent prior “missing in v4.6 by name” result for `scan15_4CheckParameters` is not reproduced: the local authenticated v4.6 SYM does contain that name, at a different size. This pass therefore classifies it as a size discriminator.

## Relocation-aware extension and false-positive controls

The scanner masks only position-dependent Thumb encodings it can recognize without relocation metadata: 16-bit unconditional and conditional branches, `CBZ`/`CBNZ`, Thumb `BL`/`BLX`, 16-bit literal loads, and 16-bit `ADR`. It retains all arbitrary immediates, literal-pool words, pointers, and other bytes. Candidate discovery uses the longest retained byte run and then verifies the complete masked body at every halfword-aligned payload location.

That conservative extension produced **zero new relocation-masked matches** beyond the 40 exact matches. This is a negative result with a precise boundary: common branch and 16-bit PC-relative relocation changes alone do not expose additional v4.2 objects. It does not exclude matches requiring relocation records, 32-bit PC-relative normalization, literal-pool relocation, function splitting, or compiler-generated instruction changes.

False-positive checks were:

1. Search the entire 211,948-byte locked payload, rather than a predicted address window.
2. Require a unique whole-body masked match; all 40 exact results have multiplicity one.
3. Map file offsets with the established EM9305 base `0x301fdc` and compare spans against `g2/symbols/ble_em9305.tsv`.
4. Keep canonical name conflicts and data-shaped symbols explicit instead of treating every SYM entry as a function.
5. Compare against v4.6 by presence, size, and bytes separately.

## Exact scope and boundary

Inputs and hashes are recorded in `results.json`. The v4.2 source is limited to the downloaded standard IHEX and SYM at commit `e4412bc98d4e76d441d1226ca3696e53cfae5f54`; v4.6 is the registered local standard IHEX/SYM; the target is only `firmware_ble_em9305.bin` SHA-256 `91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9`. The script considers addressed v4.2 symbols at `0x300000..0x35ffff` with size at least 24 bytes.

These results strengthen provider/version attribution for the 18 listed objects. They do not identify the producing MetaWare project or options, prove whole-image v4.2 identity, supply proprietary source, establish runtime behavior, or admit pseudocode coverage. No additional candidate is proposed for canonical admission from the relocation-aware extension. P2 remains executing and G3–G6 remain closed.

Reproduce with:

```sh
python3 g2/analysis/em9305-v42-reloc-independent-20261010-daybreak-low/compare.py
```
