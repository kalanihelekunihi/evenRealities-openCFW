# UART RX source recovery

Baseline verified checkpointf3ca176e; [26-alias classification](alias-classification-f3ca.json) separates19 unique OTA code boundaries,4 synthetic logger/test cuts and3 external ROM APIs. OTA families are RX2, startup6, power-mode2, RTOS runtime5, fatal/terminal2 and IAR wrappers2 (shared formatter backend). No duplicate addresses. Harness models are orthogonal to code location and are not counted as additional missing bodies. External ROM and synthetic test addresses are not missing OTA functions.

Selected UART RX because the actual source transfer dispatcher accepts modes1/3 yet both RX targets remained stock aliases. This closes a usable transfer interface, reuses already reconstructed ring/critical code and avoids expanding unresolved task restoration or IAR toolchain work. No whole-firmware source-completeness percentage follows from this selection.

New independent source `g2/components/bootloader/initializer_callbacks/uart_rx.c`;56-byte stock32-bit transfer interface in `uart_rx.h`. Locked image SHA-256f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5; little-endian Thumb at410000.

| Stock body | Function | Bytes |
|---|---|---:|
| 422f4c..422fa2 | RX claim | 86 |
| 422fa2..422fde | RX cancellation | 60 |
| 4232c8..42330e | RX FIFO read | 70 |
| 423350..423390 | FIFO→RX ring collector | 64 |
| 42348e..4234d8 | blocking receive | 74 |
| 4234fa..423524 | receive start | 42 |
| 423608..4236ce | receive pump | 198 |

**422 linked-candidate comparisons PASS; all594 RX body bytes visited**, plus52 dispatcher bytes for modes1/3. The suite covers all four UART module addresses and native source critical-save. Original instruction bytes are authenticated; original ring helpers, critical-save and cancel zero-fill execute. Initial independent359-case evidence is retained separately; it used a controlled source critical-save primitive. No RX/ring/copy answer models, no SRAM write hook. The first trace audit rejected recording synthetic callback08000100 as firmware evidence; rejection is preserved and trace filtering now retains only authenticated-image addresses.

## Call flow and recovered data

`transfer(mode1) → blocking → start → claim → pump`; `transfer(mode3) → start`. Ring mode pump first calls collector then consumes the RX ring; FIFO mode pump reads directly. Descriptor copies only its first7 words into context64..7f and mode52 into context98. All destination/count/callback pointers remain borrowed. Context offsets: requested bytes68; count-output pointer6c; timeout70; callback74/argument78; progress9c; RX ring4c..63; ring-mode byte dd; busy byte11a. Ring words are write/read/count/capacity/element-width/data-pointer at offsets0/4/8/12/16/20. RX and TX busy bytes11a/119 are independent.

Claim accepts busy0 only, sets busy1, copies fields and resets progress; nonzero busy returns**08000005**, not TX's08000004. Start zeros the caller count output even if claim subsequently fails. No handle/null validation here; outer transfer owns validation.

FIFO base40039000+(module<<12), empty flag bit4 atbase18. Read word errorsmask0f00 return**08000000** after consuming the error word; good bytes before it were already copied. NULL destination drains finite FIFO without increasing its reported count, so the requested count does not bound consumed words in that mode. Transferred-out is optional.

Collector reads up to32 into a stack buffer. Any read error skips adding the entire chunk, discarding a good prefix already consumed. Ring-add failure returns**08000001**. Pump ignores collector status, can still consume existing ring contents, and ignores direct FIFO error status while publishing good-byte progress. Receive errors therefore are not reliably surfaced through successful start/blocking returns or completion callbacks.

## Lifetime and callback semantics

| Transition | Retained pointers/state | Callback/count behavior |
|---|---|---|
| allocation | none in this family | no allocation/free |
| claim/start | descriptor values copied; destination/count/callback storage borrowed | count output zeroed before claim; busy1 |
| pump partial | pointers retained; bytes copied to destination | count published after critical restore |
| pump complete | pointers retained; busy0 | callback0 after critical restore, count already published |
| ring-get failure with callback | busy0, fields retained | callback1 inside critical section; no count/progress publication afterward |
| cancellation | requires busy exactly1; clears busy and56 descriptor bytes64..9b plus progress9c | returns0, otherwise7; no callback/free/count-output reset/ring or hardware drain |
| blocking timeout | clears busy only; retains descriptor/progress | return4; no cancellation or completion callback |

Ring-get failure fixtures deliberately use element-width2 with byte-oriented counts; constructor-normal width1 does not establish this path can occur on hardware. With no callback, that synthetic failure can still advance/publish progress despite failed copy. This is reconstructed branch behavior, not a reported live-device bug or justification for a speculative memory patch. Reentrant callbacks, real IRQ/task concurrent access and cancel/drain ordering remain unverified.

Blocking performs pump then delay(argument1000), then checks finite timeout equality. Timeout counts polling iterations; zero is not an immediate timeout. Ffffffff disables the finite check. Completion during a final iteration can still return4 because timeout is checked before the next busy test. Zero/infinite stalls are compared only at a synthetic four-poll stop boundary, not claimed to terminate. No physical timing unit or UART drain guarantee follows from injected delay.

For app/CFW users: keep asynchronous destination/count/callback storage valid until a demonstrated completion/cancellation boundary; stock timeout alone does not erase retained pointers or prove system quiescence. Detect RX data integrity at the protocol layer because this pump can hide the underlying read error. Cancellation frees nothing and does not drain the RX ring or FIFO. Avoid adding owned-buffer freeing until actual interrupt/task cancellation semantics are established.

All seven candidate integration cases, affected regressions and frozen-input reconciliation have passed. The source-linked test ELF is promoted as4edd8e7d; priorf3ca176e is preserved. No commits, flashing, IAR authentication, shared campaign or other-device edits.

Candidate4edd8e7d freezes661 inputs/169 objects. A negative control substituting TX busy code08000004 for RX08000005 is rejected and preserved in `negative-control.failure.json`/log. Existing TX-only suite retains its RX cuts through a source-PC adapter; native422-case RX/dispatcher suite establishes RX behavior separately. All seven integration cases and affected regressions PASS;661 inputs/169 objects and frozen copies reconcile. Candidate4edd8e7d is promoted; f3ca176e remains preserved.

Current [24-alias classification](alias-classification-4edd.json):17 OTA entries (startup6, run/power-mode2, RTOS5, terminal2, IAR wrapper2),4 synthetic logger/test cuts,3 resident-ROM APIs. Prior26-entry classification remains baseline evidence. [Function coverage](function-coverage.json) binds594/594 RX body bytes to the exact candidate receipt; no whole-image completeness percentage is inferred. All489 alignment mappings PASS;24 aliases/42 segments/zero undefined symbols or source-hash mismatches.
