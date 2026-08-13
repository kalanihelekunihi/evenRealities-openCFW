# G2 UART synchronization object recovery

## Result

The retained `framework\sync\uart_sync.c` object is closed as five functions
at `[0x00541790, 0x00541AF8)`. The physical object is 872 bytes with SHA-256
`95687bbb2342d095658c6986dac9270648f8b3afdf69a34aabd78a969b9f576c`:
758 executable bytes and a 114-byte shared literal pool. The retained path
directly anchors only `uart_thread_handler` and `uart_instance_init`; adjacency,
pool ownership, two stored Thumb pointers, and ingress restore the synchronous
write wrapper, receive callback, and UART reset helper.

This object embeds no third-party definition. It composes already identified
dependencies and first-party adapters:

| Boundary | Calls | Origin, version, and selected source |
|---|---:|---|
| logging | 30 | EasyLogger 2.2.99-compatible core, `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, plus the separately closed G2 compact hook |
| RTOS | 8 | CMSIS-FreeRTOS v10.5.1 `d213f261b5be6bb29a7cce8b84071706b72f4d53`, FreeRTOS-Kernel V10.5.1 `def7d2df2b0506d3d249334974f51e427c17a41c`, CMSIS_5 5.9.0 `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` |
| compiler runtime | 1 | bounded IAR `memset`; EWARM 9.20+ floor and 9.60.2 leading candidate, exact archive unobservable |
| stream object | 4 | first-party G2 stream wrapper over RTOS primitives |
| UART hardware adapter | 5 | first-party adapter over Apollo510 UART/GPIO/cache APIs; AmbiqSuite SDK 5.1.0 compatibility source `5efc0228528a8adce5eae0d226fac85d2551eb3b` |
| frame/sync layer | 4 | first-party sync policy over MightyPork/TinyFrame exact core blobs introduced by `eb75483e035916ef9f3e9fce0d2ae389cb09785f`, core-identical through `a29167a69f052975b0e0134a73b4d31d03afa8fa` |
| peer/subsystem policy | 10 direct + 1 indirect | first-party G2 initialization and synchronization seams |

The AmbiqSuite commit is the authenticated public SDK 5.1.0 compatibility
baseline, not a claim that the private firmware checkout can be recovered.
Likewise, TinyFrame core bytes select the exact minimum-patch commit, but
cannot distinguish a historical checkout within the core-identical interval.
No new third-party version discriminator or recoverable private generating
commit is present.

## Reproduction

Run:

```sh
make uart-sync-closure
```

The analyzer authenticates the official payload, all five bodies, the physical
object and both neighboring objects, every decoded instruction, direct and
indirect calls, whole-image ingress, stored entries, retained path and
diagnostics, upstream provenance records, and absence from the production
overlay.

| Evidence | Result |
|---|---:|
| Linked / Ghidra-discovered functions | 5 / 5 |
| Restored / path-anchored functions | 3 / 2 |
| Raw path references / referencing functions | 6 / 2 |
| Body / pool / physical bytes | 758 / 114 / 872 |
| Reachable instructions | 297 |
| Direct calls | 63 |
| Internal / external direct calls | 1 / 62 |
| Bounded indirect calls | 1 |
| Whole-image direct `BL` entries | 4 |
| Stored exact entries / strict-interior entries | 2 / 0 |

The executable-body SHA-256 is
`abcaf8e394fffe0ca78733c6669bd0c8d1c9e5af2d3b787cc670e53f70ea685d`.
The instruction topology digest is
`bf3108a63a6c98c085b62c25d4a4d7f1dd6792bc299ded75a926f8587e3e1893`,
and the direct-call digest is
`39b6bae2a0c6e29987505d5c1919ac694942b3acbf3f97677afb247f45887e53`.

## Recovered transport contract

`uart_instance_init` creates the worker with `osThreadNew` and returns zero on
success or minus one on failure. The worker creates one mutex, one event-flags
object, and a 24,576-byte receive stream, then initializes the role-selected
TinyFrame instance. Successful initialization invokes one function through RAM
slot `0x20000658`, initializes peer-facing subsystems, resets the UART adapter,
and emits its fixed six-byte handshake.

The event loop waits forever on mask `0x7` with no automatic clear and handles
each bit explicitly:

- bit 1 clears itself and drains receive data;
- bit 2 clears itself and drains the sync-framework send queue; and
- bit 4 clears itself and services TinyFrame ticks.

Normal receive handling clears a 1,024-byte staging buffer, reads up to 1,024
bytes at a time, and dispatches each nonempty chunk to the sync framework. One
wake handles no more than 32 chunks and stops once cumulative bytes exceed
`0x7FFF`. In the product-mode handshake branch, a one-byte flag is cleared and
exactly ten bytes are read into the adjacent handshake buffer instead of being
passed to TinyFrame.

The receive callback writes incoming hardware data to the stream and sets bit
1. The synchronous write wrapper passes buffer, length, and timeout unchanged
to the lower UART provider; provider return zero maps to public zero, while any
failure maps to minus one. This is the same 20-byte wrapper already used as the
authenticated TinyFrame transport boundary.

## Residual first-party and hardware seams

The one indirect call at `0x00541914` loads a function pointer from RAM slot
`0x20000658`. The image contains no immutable target for that runtime slot, so
the call site and single-call placement are bounded but its runtime target
cannot be named statically. This is first-party initialization policy, not an
unidentified third-party library.

The lower UART adapter at `0x00584BC0` and siblings is also first-party code.
Its transitive calls and ABI are consistent with the authenticated Apollo510
UART, GPIO, cache, and RTOS interfaces, but hardware timing, pins, interrupt
behavior, and the peer handshake still require a device or golden capture.
Those constraints do not prevent a source candidate for this orchestration
object, but they do gate production replacement of the live transport.

No device, signing, flashing, erase, or runtime operation was performed.
