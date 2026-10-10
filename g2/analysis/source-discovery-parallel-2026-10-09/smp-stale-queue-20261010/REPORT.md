# SMP stale-token queue cleanup: five offline fixtures

All five original-byte cases agree with an unchanged extracted SDK5.2 SmpHandler body compiled inside an explicit source projection. This adds finite handler/queue-provider behavior evidence; the provider attribution and presence of an Ambiq drain extension were already known. No corpus coverage or source admission is changed.

| Completion / queue | Observable result |
| --- | --- |
| Stale completion, empty queue | One null dequeue, no free/dispatch |
| Stale completion, two stale entries | Dequeue/free entry0, dequeue/free entry1, null dequeue |
| Matching completion, two current entries | Dispatch once; queue untouched |
| Stale completion, mixed three-entry queue | All three entries drained/freed in FIFO order, then null dequeue |
| Closed connection, two entries | No dequeue/free/dispatch; queue untouched |

`results.json` records every dequeue/message-free/buffer-free address, critical-section ordering, node reads and writes. Node reads touch only the four-byte next pointer and one-byte handler ID. Queue payload token fields are never inspected by these cleanup providers: the stale trigger causes a complete drain, including mixed/current entries. This is a finite queue contract, not a claim about whether such mixed requests arise in normal radio traffic. The fixture's payloads are synthetic WSF-header token carriers; real encryption callback unions, ciphertext and operation contents are outside this contract.

## Authenticated binding

Locked main SHA256 36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863; main base 438000, package header20hex bytes; each executed extent/hash is checked in run.py and retained in results.json. The original SmpHandler 537D0C..537E9E reads event at message+2, status at+3, CCB connId at+61 and token at+65. AES event11 and closed connId0 are checked against source/body. Its authentic literal at537EE8 contains20072CD8. SDK sec_main.h declares rand[32] followed by aesEncQueue, yielding candidate secCb base20072CB8; the test needs only the directly evidenced queue address and does not rely on that wider control-block inference.

Original WsfMsgDeq 4BF9EC..4BFA00 calls original WsfQueueDeq 538C4A..538C6E, copies handlerId at hidden header+4 and returns header+8. Original WsfMsgFree 4BF9B0..4BF9BA subtracts8 before calling WsfBufFree5304D4. QueueDeq uses head/tail offsets0/4, reads element-next at0, clears tail when removing the last head and brackets each dequeue (including empty) with WsfCsEnter52B8A4 / WsfCsExit52B8B6. These four original extents execute under Unicorn2.1.4 Thumb/M-class. Every other reached code address fails closed unless explicitly mocked.

## Source and mock boundaries

The nine retained individually licensed Apache-2.0 Cordio source/header members are extracted from the already authenticated user SDK5.2 ZIP; exact members/hashes are in source-provenance.json, original notices intact. sec_api.h confirms generic secMsg_t starts with wsfMsgHdr_t. The entire unchanged SmpHandler function is extracted automatically; its body hash is retained. The native C projection supplies logical queue/free/dispatch stubs with entry IDs, not ARM32 layout or original-byte equivalence. Stock executes the genuine dequeue/free wrappers and linked queue provider; lowest buffer release is mocked and records raw hidden-header addresses rather than exercising the memory-pool allocator. Source queue stubs independently produce expected ordering and remaining count. Logging macros in the source projection are silent.

Stock mocks: smpCcbByConnId5375FC returns the supplied CCB after checking connId1; product logging gates4C9C50 /43D0CE return0; warning52A63C checks supplied token/status; WsfCsEnter/Exit record balanced order; WsfBufFree records addresses without releasing or modifying nodes; smpSmExecute56EE62 checks CCB/message pointers and records dispatch. This does not validate lookup, logging, scheduler/interrupt exclusion, memory-pool recycling, state-machine behavior, concurrency or hardware. CMAC/service events are outside the fixture. Node buffers, message and CCB remain byte-identical; writes are restricted to the eight-byte queue object and stack. SP and callee-saved r4-r7 return unchanged.

Replay: `python3 run.py` with the installed /tmp/mspi-enable-python-deps Unicorn path and local clang. The sandbox's first attempt exited132 before fixture results; permitted local execution succeeded. An initial unmodeled warning call stopped the run, was explicitly bound, and final replay with node-read guards passed all five cases. No hidden provider substitution, relocation masking or firmware-byte modification occurred.

New directory only; no staging, commits, pin/index/registration changes, canonical ledgers, authenticated inputs/seals, production firmware or device access. No new download was necessary. This closes the requested finite cleanup goal; whole SMP/source-build and buffer-free provider closure remain separate goals.
