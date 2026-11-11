# Bounded R1 EUS receive reassembly in C

`board/native_eus_reassembly.c` implements stock `0x32198`, closing the missing BLE receive transport entry. It retains the global stream, retry rollback, CRC, callback and ownership behavior for supported packets, with explicit C checks for malformed input.

A new nonzero fragment counter selects static storage for counter 1 or allocates `(counter + 1) * 239` bytes for counters 2–16. A repeated counter replaces the previous fragment by rolling back its payload length. Counter 0 checks CRC over the direct or assembled message, delivers matching data through the existing RX queue callback, or emits the stock six-byte negative acknowledgement. Callback results remain ignored. Owned heap storage is freed after completion; static storage is retained.

The new owners are a zero-initialized 12-byte receive prefix at native `0x20006954`, the completion callback at `0x2000696c` and compatible scratch storage at `0x20019c48`. The callback's cold pointer `0x33dbd` becomes a relocation to the existing C RX enqueue function. The existing transmit callback owner is reused. The 478-byte C scratch bound accommodates two 239-byte payloads; it is not a claim about the original allocation's full extent. Four additional private C bytes track capacity.

The C-only checks reject null data, wire frames above 244 bytes, retry underflow, corrupt used lengths and copies beyond capacity. Overflow rejection clears the stream and frees an owned heap buffer once. Short bad-CRC messages zero unavailable acknowledgement reference bytes instead of reading beyond their logical payload. These are intentional safety changes, supported by the pinned 247-byte ATT MTU and existing 239-byte fragment publisher.

In controlled stock execution, nondecreasing counters `1,2,3` with full payloads overwrite the adjacent ACK registry. The C version rejects the third copy, preserves the guard and successfully receives a fresh message afterward. Heap overflow and corrupted-state recovery have separate tests. This experiment runs only in emulated SRAM.

**1,358 stock/C sequence comparisons pass**, including all first-counter values, callback words/results, allocation failures, CRC rejection, retry rollback and live backend mutation scenarios. The actual C sender, CRC and memory functions execute; generated frames also match an independent polynomial implementation. **13 C-only safety cases** pass, and all **15 compiled defects** are rejected.

The replay covers all **422 reachable native instruction bytes**. Two bytes at `0x32210` are unreachable because `MOVS` loads a fixed nonzero scratch pointer into `r0`, a following store preserves flags, and `BNE` always skips them. The recorded proof assumes ordinary entry and ABI-preserving calls, rather than arbitrary register corruption or interior entry.

Heap services, final transmit/receive callbacks and logging are modeled. The real queue consumer, RTOS, physical BLE and interrupt/reentrant behavior are outside this fixture. One global stream remains; connection isolation is not added. The stock sender accepts up to 4,096 bytes while the receiver rejects first counters 17 and above. The 4,063/4,096-byte tests preserve this failure behavior, so those messages are not reported as successful round trips. This framing asymmetry remains open.

The normal build compiles **852 units**: 770 application and 82 bootloader. One transport import closes without new imports, leaving **66 application imports** and 22 bootloader linker imports. All **841 prior nongenerated objects** remain unchanged. No assembly is added. R1 manifest checking passes; repository-wide checking retains the unrelated unlisted G2 `resident_rom_thumb_set.S` issue. Final placement, complete firmware linking, boot and physical transport remain unverified. Byte identity and paid compilers are not requirements.

Exact hashes, REA evidence, ownership accounting, the native overwrite probe and proof limits are in [rx-reassembly-c-review.json](rx-reassembly-c-review.json). No commit or device write was performed.
