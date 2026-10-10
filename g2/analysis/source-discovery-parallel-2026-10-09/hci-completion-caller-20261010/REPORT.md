# Actual command-complete caller to security handler

Local authenticated stock bytes and retained SDK source are sufficient for a **bounded caller contract**. Two original-byte cases passed: a normal complete LE_ENCRYPT parameter stream and temporary event allocation failure. This advances beyond direct invocation of secHciCback, without asserting a real controller event or command/completion reachability.

Normal observed order is allocate22, actual parser, actual security callback, actual message/queue dequeue, AES type-callback boundary, temporary free, command-credit boundary. Allocation failure produces only allocate22 and command-credit, preserving the security queue and skipping parser/callback. Exact events, provider arguments, memory accesses, original extent hashes and table bindings are retained in results.json; run.py is the replay harness.

## Authenticated execution boundary

The locked main hash is36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863, original base438000 and file-header20hex bytes. Original functions executing under Unicorn2.1.4 Thumb/M-class:

- hciEvtProcessCmdCmpl56B182..56B37C,506bytes, canonical Strong source mapping.
- hciEvtParseLeEncryptCmdCmpl56A0D0..56A0EA,26bytes, canonical Strong source mapping.
- candidate secHciCback536234..536324 and genuine WsfMsgDeq/QueueDeq, as checked in earlier receipts.
- Original copy provider439BE4..439C8A,166bytes, authenticated unnamed function; selected parser-copy execution stays within its extent and calls no external provider. This does not create a canonical memcpy/source attribution.

Actual caller literals bind hciCb20073870, event-size table6E3720 and parse table6C910C. Event27's authentic size is22 and parse pointer56A0D1. Caller selects hciCb+12 security callback for opcode2017; fixture supplies authentic Thumb entry536235. Other hciCb callback entry is a distinct fail-closed sentinel. Source/caller registration was statically authenticated in the prior registration receipt; registration is not re-executed here.

Input is the20-byte Command Complete **parameter stream**, not a full HCI transport packet: numPkts1, opcode2017, controller status0,16 bytes0..15. Source hciEvtProcessMsg strips its HCI event header before calling this function; that outer receiver/transport path is not part of this test. One valid unique64-byte node is initialized as8 hidden WSF bytes plus56 request bytes; handlerID36, clientparam1, SMPevent11, retained request token7, AES type0. No empty-security-queue experiment is added.

## Precise source projection and comparison

Retained SDK5.2 hci_evt.c from the prior authenticated ZIP provides complete caller/parser source. Their exact definition bodies and hashes are saved here. The comparison model in run.py is an independent **selected-source Python projection**, not unchanged compiled C or a full module comparator. It fixes one supported opcode and length; projects numPkts/opcode extraction, callback selection, temporary allocation, source header initialization, original parser's status/data placement, selected security dequeue/callback and final free/credit order. It asserts the full22-byte temporary representation, including its untouched final padding sentinel. Source provider scaffolding and target pointer geometry are not equated.

The complete authentic parameter input satisfies the SDK caller's minimum-length check. Stock entry bytes perform numPkts/opcode reads without that SDK check, so this test does not establish whole-function SDK equivalence. The minimum guard is a separate observed source/byte difference; no short-length test, exploit, vulnerability or malformed event reachability claim is made.

Parser sees p=input+3 and length20, matching source's unchanged len argument after pointer advancement. Original parser writes controller status at temporary+4 and header.status+3, and copies16 data bytes to+5. The request's own header status7 remains untouched; temporary controller status0 and request token7 are demonstrably distinct objects. At the type-callback boundary, its arguments are request-message pointer, parsed temporary pointer, handlerID36. Temporary event is freed only after that callback returns. All packet/node bytes and event guard bytes remain unchanged; nonempty queue becomes empty. SP and callee-saved r4-r9 return unchanged. Failure control leaves temporary storage and queue untouched.

## Explicit mock boundaries and finite stop

WsfBufAlloc530446 is a recording mock returning the supplied22-byte arena orNULL. WsfBufFree5304D4 records temporary-pointer handoff without allocator release. WsfCsEnter/Exit52B8A4/52B8B6 record one balanced pair on successful dequeue without interrupt exclusion. The AES type callback is a recording mock, not SecAesHciCback or WSF message delivery. hciCmdRecvCmpl52AEF8 records numPkts1 without exercising timeout/command-queue progression. Every unrecognized executed PC aborts. Guest writes are confined to the temporary22bytes, queue8bytes or bounded512-byte stack. Input reads are checked not to exceed the supplied20 bytes.

No missing input blocked this selected caller-to-handler contract. Broader claims still require changed boundaries: real pool allocation/free and command-credit providers; actual receive/transport parsing and allocation lifetime; type-callback/message forwarding; controller command acceptance/completion and event ordering after cleanup. A direct invocation of the genuine caller does not establish those conditions, and chaining the handler artificially after a drain would not supply them. No live radio/controller, target process or device runs.

The identified null-guard difference remains resolved as a direct-ABI semantic distinction, with hardware reachability unknown. Implementation/audit own the separate hardware-error cleanup receipts. This caller contract closes the requested offline neighborhood at its explicit providers; it does not prove source completeness, producing compiler/version, byte-identical build or canonical coverage.

Only this new directory is written. No installations, MCP restart/discovery, shared project switches, source admission, staging, commits, index/pin/registration or production/device changes. Source evidence is referenced from prior retained licensed SDK files; no new download was needed.
