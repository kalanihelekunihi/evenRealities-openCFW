# CASE command-handler control-flow frontier

The locked CASE image is SHA-256 `36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374` after its 32-byte wrapper. `decode_switch.py` checks the image hash, exact legacy dispatch and helper bytes, and decodes all sixteen Thumb-1 table entries at `0x08000944`; `switch_table.json` records opcode, raw byte, Thumb target and code address. The helper at `0x08009190` obtains the maximum index from `LR-1`, clamps larger indices to 15, reads a byte displacement from `LR+index`, doubles it and branches relative to the entry array. Thus the apparent instructions at `0x08000944..0x08000954` are table data, not executable code. The decompiler's unresolved-jump-table note is superseded for **target enumeration**, not for body semantics.

The legacy table maps `0xa0..0xaf` to code addresses respectively `0x080009fe`, `0x08000a24`, `0x08000a44`, `0x08000a84`, `0x08000aee`, `0x08000b0c`, four defaults at `0x080009fa`, `0x08000b2c`, `0x08000b2a`, two defaults at `0x080009fa`, `0x080009d2`, and default `0x080009fa`. The surrounding comparisons also dispatch `0xb0`, `0xd0..0xd4`, `0xdd`, `0xdf`, `0xee` and `0xff`; the table is only one branch family. The extracted stock window reaches `0x08000c68` literal data and includes calls to power, reset, peripheral and logging children. A complete C provider must account for each reachable case, the length guards, state writes, child argument order, and bounded nonreturning reset/standby exits. Those contracts and a whole-entry original/source branch matrix are not yet present.

The binary handler begins `0x08000e1c`; the retained `case-local-commands-closure-2026-10-08/original-disassembly.txt` proves selected commands `0x50`, `0x5c`, `0x5d`, `0x68` and two acknowledgement cases `0x06`, `0x41`. Its 240 comparisons explicitly restrict destination byte `+2` to 2, selected opcodes, logging-disabled state and allocated 256-byte buffers. The same entry visibly branches to `0x08000f22`, `0x08000f26`, `0x08000f42`, `0x08000f54..0x08000f5c`, `0x08001052`, and `0x08001108` for additional opcode families. It cannot be replaced by the selected local-command helper without inventing routing and effects. The earlier `case-binary-forward-closure-2026-10-08` contract likewise isolates forwarding, not all cases.

No complete direct source unit was integrated. The CASE archive remains 37 objects, 61 provided symbols and five unresolved imports: four direct (legacy command, binary command, UART other IRQ, UART DMA boundary) and one lower formatter. Direct completion stays **8/12**. The legacy table target set is now finite (16 entries, ten distinct code targets), but semantic closure still needs every reachable case and lower child; binary routing needs the additional opcode families and coherent branch/side-effect oracle. The UART full-handler and formatter frontiers remain as documented in `case-remaining-direct-frontier-20261010`. These are four direct contracts plus one lower contract, not five equal-sized tasks or a defensible duration estimate.

## Ten table targets and their local children

The target instructions through `0x08000c64` were read from the fixed image with `arm-none-eabi-objdump -D -b binary -m arm -M force-thumb`, treating the 17 table bytes as data. These are observed call boundaries, not source ownership claims.

| Table cases | Target | Local action / lower calls |
| --- | --- | --- |
| `0xa0` | `0x080009fe` | Conditional logs at `0x08009170`, sampling `[r4+8]`, then newline/return. |
| `0xa1` | `0x08000a24` | Requires length >=2; sends input byte 1 bit `0x10` through GPIO wrapper `0x08006b98` and bit 0 through `0x08006b80`. |
| `0xa2` | `0x08000a44` | Calls `0x08002f60` to fill eight stack bytes, `0x080067c8` to log hex, then conditionally formats eight byte arguments through `0x08009170`. |
| `0xa3` | `0x08000a84` | Calls three value producers `0x08009ff0`, `0x08009f18`, `0x0800a01e`; conditionally logs their words and input fields. |
| `0xa4` | `0x08000aee` | Conditionally logs the input word at `[r4+12]`. |
| `0xa5` | `0x08000b0c` | Requires length >=8; logs/hex-dumps eight input bytes via `0x080067c8`, then calls `0x08003664`. |
| `0xaa` | `0x08000b2c` | Branches to `0x08000c56`, calling `0x0800d1bc` then `0x0800d218`. |
| `0xab` | `0x08000b2a` | Branches to `0x08000c60`, calling `0x08003558`. |
| `0xae` | `0x080009d2` | Requires length >=2; booleanizes input byte 1, writes through literal at `0x08000c90`, conditionally logs state text. |
| `0xa6..0xa9`, `0xac`, `0xad`, `0xaf` | `0x080009fa` | Shared stack restore/return. Out-of-range helper indexes clamp to the `0xaf` default entry. |

This eliminates jump-target ambiguity but exposes unowned child effects. `0xa3` depends on three value producers, `0xaa` and `0xab` on control children, and logging branches on the still-open formatter `0x08009210`. The high-opcode family outside the table includes state writes and calls to `0x080035d4`, `0x08002c8e`, `0x08002c30`, `0x08005094`, `0x080050a8`, `0x080050c4`, `0x0800502c`, and `0x080039e4`. There is no whole-entry oracle covering all branch side effects and return/nonreturn behavior. A full source body remains open.
