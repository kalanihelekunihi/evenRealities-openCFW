# ATT queued-request representation: three offline comparisons

**Original stock matches the SDK `onDeck[connId-1]` projection in all three fixtures, and differs from public r20.05c `onDeck[connId]` in all three.** This establishes the selected dispatcher's queue-selection representation for the supplied valid connection/response state. Independent review is still required before canonical admission. No producing-SDK or vulnerability claim follows.

## Complete original and field binding

Authenticated Apollo package SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`; complete dispatcher `[0x4B5448,0x4B557A)`, 306 bytes, SHA-256 `f8256375f5cad966c0c74be78977523bce416b3fdeb41f06c9b98537cd9edd18`. Original bytes and complete disassembly are retained. No masking, replacement instructions or fitted compile options.

Actual CCB fields: main pointer +0; outstanding message +4, event +6, status +7, packet pointer +8 and handle +12; timer +24; bearer slot +40; connection ID +41. Caller callback/global reads and response processor pointers are authenticated from the locked image, not supplied replacement tables.

Initializer `[0x531B1C,0x531B90)` uses the same `attcCb` base 0x2006F904 as the dispatcher. Its loops establish three connections and three bearers, 44-byte CCB stride and 132-byte connection stride. It writes connection ID `i+1` to +41, slot `j` to +40, main-CCB pointers from authenticated `attCb` base 0x200610AC, and places `pSign`/auto-confirm at +432/+436. The identical public/SDK source header places onDeck after the CCB array and before pSign. Thus nine 44-byte CCBs occupy 396 bytes; three 12-byte queue messages occupy the next 36 bytes. The queue starts at **G+396**, not G+384.

Stock's instruction arithmetic `G+384+12*connId` therefore means `G+396+12*(connId-1)`. This is why a raw multiply without an explicit subtraction is not an old-indexing proof. `FIELD-AND-MEMORY-RECEIPT.json` retains initializer bytes/hash, literals, field geometry and fixture memory checks. Exact producing configuration remains unproved; these are observed stock dimensions.

## Fixtures and projections

All fixtures use connection ID 1, slot 0, no flow disable, null application callback, a valid write response (opcode 0x13 at original packet +8, payload length 1), matched outstanding method 9 and completed status 0. Both queue entries are fully allocated and readable. Stock's actual method-9 table pointer is 0x4B53DD and actual minimum table value is 1.

| Queue readiness | Stock / SDK result | Old public result |
|---|---|---|
| Entry 0 event 10, entry 1 event 11 | Setup entry 0 and clear its event | Setup entry 1 and clear its event |
| Entry 0 event 10, entry 1 empty | Setup entry 0 and clear its event | No setup |
| Entry 0 empty, entry 1 event 11 | No setup | Setup entry 1 and clear its event |

The complete original dispatcher executes in the existing Unicorn Thumb/M-class runtime. Four dependency boundaries are explicit recording mocks: timer stop 0x52A4D2; selected write-response processor 0x4B53DC; packet-free 0x531AC0; request setup 0x531160. Unexpected providers stop execution. Processor/free/setup mocks do not execute real parsing, deallocation or transmission. The packet pointer already is null in outstanding state, so the source free mock's null assignment and stock return-only free hook have equal effects here.

Complete public and SDK dispatcher bodies are extracted verbatim and compiled by the existing host compiler with documented named-field projections. Host C layout is not used as Arm layout evidence. The projected function table supports method 9 only; the projected minimum table supplies its actual value 1. Other methods, guards and processors are outside this comparison. Source provenance is in the predecessor source-lead packet. No whole-module build or compiled source-byte identity is claimed.

## Reads, writes and finite boundary

Memory hooks verify stock reads exactly one packet byte, the opcode at +8; the entire initialized 32-byte packet remains unchanged. Stock writes are confined to its 40-byte stack frame, outstanding event at control offset 6 and selected entry-0 event at control offset 398. The neighboring queue and remaining 512-byte control region stay unchanged. R4–R7 and SP are preserved. Setup hook verifies CCB pointer and selected message pointer and records its event before the original code clears it.

These cases identify queue selection, not actual source request setup, timer ownership, continuation rules, callback mutation/reentrancy, flow-disabled behavior, queued API producer composition, highest connection ID behavior, live Bluetooth delivery or security impact. Stock producer indexing and exact private revision require separate evidence. SDK method/PDU checks are visible statically but are not admitted as tested behavior by these valid-response fixtures. No out-of-range or malformed traffic fixture was used.

New outputs are isolated here; predecessor/source files were read only. No production source, existing pin, root index, protected input or checkpoint was changed by the script, and no commit, push or device operation occurred. Replay: `python3 g2/analysis/cordio-att-ondeck-threecase-20261009-source-track/run.py` with the existing local compiler/Unicorn runtime and native mapping permission. `RESULT.json` retains all three raw instruction visits, accesses, call projections and mutations. Stop repeating these cases unless new evidence changes a dependency or field binding.
