# QP/C ready-set boundary and queue audit integration

The scheduler's undecoded0x3D2F1000 at0x31163E matches no opcode/mask entry in the installed pinned ARC binutils arc-tbl.h (exact count/hashes in results.json). This bounded table check does not establish that all official ARC extension tables or vendor custom instructions are unavailable. It establishes why this decoder/source table cannot supply the missing operation; alternate endianness is not adopted merely to obtain a name.

Official pinned qpset.h selects a16-bit QPSetBits for maximum active<=16 and QPSet_findMax expands to QF_LOG2. The stock halfword load and subsequent<17 assertion support that configuration family. The separately acquired EMv4.6 port maps QF_LOG2 to log2p1, but its compatibility with producing v4.2 remains unproved. Those associations do not prove that the unrecognized stock opcode implements log2p1 or establish its zero-input behavior.

Stop here for full scheduler semantic reconstruction until an authenticated definition/decoder of the exact vendor instruction or producing object/source is available. Downstream scheduler checks and queue field binding remain valid at the earlier packet's stated static boundary. No new original execution, compilation, source-byte equality or coverage claimed.

QUEUE-REVIEW.md independently passes the prior conditional C-SKY placement result: SRAM Put/XIP Get supports supplied KWS and conflicts with unchanged AIoT contracts without exact attribution. It verifies eight physical slots/seven usable pending events and TriggerAppEvent's discarded enqueue status. This approval is separate from QP/C, pending its own audit. Existing seals and canonical ledger remain untouched.
