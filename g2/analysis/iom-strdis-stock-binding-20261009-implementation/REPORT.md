# Stock IOM STRDIS branch binding

Result: **OLD behavior in all three locked Apollo main configuration branches**. The stock words exactly equal the prior source expressions and differ from the unchanged SDK 5.2 defaults only in STRDIS bit 24. This excludes the unchanged new STRDIS=1 configuration path for these three writes; it does not identify the entire producer SDK revision.

| Rate argument | Stock store | Literal address | Stock/old MI2CCFG | SDK 5.2 default | CLKCFG |
|---|---|---|---|---|---|
| 100000 | 0x55cb94 | 0x55d264 | 0x3f070 | 0x103f070 | 0x773b2301 |
| 400000 | 0x55cba6 | 0x55d26c | 0x3f270 | 0x103f270 | 0x1d0e2301 |
| 1000000 | 0x55cbb8 | 0x55d274 | 0x23040 | 0x1023040 | 0xb052301 |

Configuration code entry `0x55CA94`, code extent `[0x55CA94,0x55CC10)`, 380 bytes. The prologue/validation precede interface selection at `0x55CAEA`; I2C mode 1 is tested at `0x55CB66..0x55CB6A`. Frequency comparisons at `0x55CB6C..0x55CB86` load 100000/400000/1000000 from `0x55D258`, `0x55D25C`, `0x55D250`. Valid branches load CLKCFG and MI2CCFG independently, compute r2=r7+(r6<<12), then store r1 at r2+0x2C0. r6 comes from handle+4 at `0x55CAD4`; r7 loads `0x40050000` through `0x55CADA` from `0x55CF38`. Valid module check compares against 8 at `0x55CABE`. Thus the write address is `0x400502C0 + module*0x1000`, module 0..7. Each branch reaches common CLKCFG store `0x55CB2A` through `0x55CB22`; no intervening modification to MI2CCFG data occurs. Unsupported rates return 6; unsupported modes return 5.

Original receipts independently decode each Thumb LDR.W halfword and aligned PC+4 literal target and assert each original STR.W encoding `c2f8c012`. The exact raw function and each 18-byte branch appear as hex plus SHA-256 in `stock-receipts.json`. Literal ranges are separately accounted; objdump rendering of literal words as instructions is explicitly not a code claim. The full function boundary is prologue through terminal POP, with adjacent magic literals separately recorded; shared pool ranges are dependencies, not function code.

Authenticated OTA main payload SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`; virtual mapping uses payload offset=address-0x438000+32. Locked outer bundle and all six payloads match target sizes/hashes. SDK ZIP SHA-256 `d9751350ef593b306838792a64a5620e4912c84ddf32dc9ff6aacd5cca049cad`. ZIP Apollo510 source SHA-256 `cb8024be21b6b86171637d9bd33170e720a56944933635b0940939a2fdcc63f2`; previous source SHA-256 `a75ec905d833aa0c721e1ea7207df2d6a8adccdf57d7d1a42fb47ce0734c6530`. Registered upstream checkout remains `5efc0228528a8adce5eae0d226fac85d2551eb3b`.

Use the independent field contract at `../dependency-gap-audit-fresh-2026-10-09T192823Z/next-sdk-audit/STRDIS-FIELD-REVIEW.md` and `STRDIS-CONTRACT.json`: STRDIS position 24, mask 0x01000000, register offset 0x2C0. The official description is “Disable detection of clock stretch events smaller than 1 cycle”. Stock sets this field to zero; the new default sets it to one. The nominal 1MHz branch source comments approximately 860kHz. No inference about measured frequency or stretching is made.

Limits: static binding only; no firmware/device execution or compiler reconstruction. No full-function byte equality to either source revision is claimed. No physical bus behavior, live module selection, callback state, private patch provenance, producer compiler/flags or whole-image source coverage follows. This pass binds the main image only; it makes no claim about bootloader equivalent branches or other MI2CCFG writers. No missing input blocks this finite conclusion.

Preservation: 3437 prior sealed entries checked under the existing preservation policy exclusions, zero mismatches; all 110 protected audit inputs and four checkpoints match; index hash unchanged during this task. Existing policy exclusions are retained, not upgraded to new seal claims. Only this unique analysis directory and temporary derived image/disassembly were written. No production changes, device writes, commits, pushes, submodule changes or index operations. No closed audio/DSP/LZ4/Nema test was executed. No local skill was applicable to this static firmware-byte question.

Replay: `python3 g2/analysis/iom-strdis-stock-binding-20261009-implementation/verify.py`. Supporting files: `stock-receipts.json`, `original-disassembly.txt`, `preservation.json`.
