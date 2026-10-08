# Case local command replies and control selection

**240 PASS original/independent selected-command comparisons**, now including actual acknowledgement and GPIO helpers as shared original peers. The send routine 0x0800680C is an entry boundary; it never executes or returns a stub. [Reconstructed C](../../components/case/local_commands_offline/local.c), [results](results.json), [instructions](original-disassembly.txt).

Scope: destination byte +2 equals 2; commands 0x50,0x5C,0x5D,0x68, logging disabled at entry by control byte 0x200000BF=1. Full binary handler entry 0x08000E1C executes on the original side; independent source has selected-local-command contract and does not repeat general routing. Logical length 0/4/5/6/20; bytes4 0/1/2, byte5 0/1; status byte0/1. All inputs have allocated256-byte storage even for shorter logical length. This does not establish buffer safety for short allocation.

| Command | Recovered behavior | Length gate and downstream boundary |
| --- | --- | --- |
| 0x50 | Constructs seven bytes **50 01 03 03 01 02 39**. | No length check in selected branch. Send receives those exact bytes; fields1/2/39 not labeled firmware version without producer evidence. |
| 0x5C | Constructs **5C 01 03 01 VV**, VV = logical NOT of byte 0x20000880. | No length check in selected branch. Meaning of status source is not yet established. |
| 0x5D | If byte4 nonzero, invokes 0x08006B80; otherwise 0x08006B98. Argument is logical NOT byte5. Then acknowledgment **5D 01 03 01 00**. | Requires logical length>=6. Actual helpers write GPIO mask0x40 or0x80 to 0x50000018 for set, 0x50000028 for reset. |
| 0x68 | Writes boolean byte4 to 0x200000BF (same byte the dispatcher tests to suppress logging); acknowledgment **68 01 03 01 00**. | Requires logical length>=5. Downstream log consumers beyond this handler are excluded. |

GPIO wrapper 0x08006B80 selects base0x50000000/mask0x40; 0x08006B98 selects mask0x80. Original 0x08004E9E writes offset0x18 for nonzero argument, offset0x28 otherwise. Passive emulator MMIO is mapped; verifier asserts ordered writes independently of original/native equality. No peripheral emulation or physical set/reset side effect is claimed. Board pad identity, attached circuitry and safety requirements need hardware/reference mapping before device use. Actual ack0x080068D0 builds a five-byte payload and calls the send entry; comparison asserts argument/payload and persistent state, not incidental return-register ABI.

Useful app implication: command0x5D has two control selectors, with polarity inverted from byte5; it is not a generic arbitrary GPIO register write. These recovered fields can guide simulator/protocol modeling, but this batch does not demonstrate host acceptance, transport framing/checksums, actual transmission or reachable remote GPIO control. Commands0x06/14/3E/3F/51/56/5E/5F and nonlocal3D remain open static leads. Logging-enabled branches are also untested.

Build via build_offline.py, then opencfw venv verify.py (temporary tool/ELF locations in receipt). Locked case image is authenticated by wrapped hash 36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374, header32/load0x08000000. No production changes, commits, index edits or hardware actions. Older904 seals,110 audit inputs and four checkpoints preserved. This is bounded source knowledge, not an exhausted command implementation or a complete rebuilt firmware.
