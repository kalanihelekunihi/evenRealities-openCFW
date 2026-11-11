# R1 legacy sensor reply sender in C

`r1/src/application/board/native_legacy_reply.c` supplies stock entry
`0x8967c` (34 bytes), resolving the factory motion adapter's
`r1_legacy_bounded_reply_send` dependency. REA's byte receipt matches the
locked application, and its decompilation agrees with local disassembly.
The evidence and production object hashes are in
[the review receipt](legacy-reply-c-review.json).

The sender obtains the glasses connection handle once. Exactly `0xffff`
returns 1 without dispatch; other full-width values pass through. It forwards
the original pointer and full 32-bit length to
`r1_ble_tx_queue_dispatch_type2`, returning the queue result's low eight bits
zero-extended. It adds no null-pointer check, packet limit or retry. The
motion adapter declaration now matches the result-bearing provider; its
existing machine code is unchanged.

The production Clang object passed 2,016 paired native/C cases covering
invalid and high-bit handles, null/unaligned/unmapped payload values, zero and
large lengths, signed/high-bit queue results and interrupt mask states.
Calls, arguments, R0, preserved registers, stack restoration, masks and watched
payload memory match. Both bodies use a 16-byte frame at provider calls.
Three compiled negative controls were rejected: low-half-only handle testing,
omitted result narrowing and length truncation.

A further 2,301 paired cases link the actual C motion adapter and new sender,
with clear, connection lookup and type-2 queue calls modeled at their
boundaries. They compare packet bytes, access ordering and factory/cache state,
including invalid handles and active/inactive factory mode. This retains the
motion adapter's known packet-placement difference (native SP-48, C SP-56).
The fixture does not prove asynchronous ownership or physical BLE delivery.
Caller-saved residue and APSR are excluded from these behavior comparisons.

`build/sources-goal-r1-legacy-reply-c/report.json` compiles all 619 units,
composes both payloads without duplicate strong symbols, and reduces application
imports from 167 to 166; bootloader imports remain 34. All 618 prior object
hashes are unchanged, including the motion adapter. The existing type-2 queue
C provider resolves the new sender's dependency, but is intercepted in this
turn's replays.

Exact qualification compiles the unit but rejects its differing instruction
bytes. No new region enters the canonical source plan. The fresh hybrid still
has 4,295 source-built bytes, 641,865 executable pull-through bytes and 248
resource bytes and matches locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
A full source-only link, remaining hardware providers, instruction identity and
physical sensor/BLE validation remain open.

A [subsequent actual queue-chain review](motion-reply-queue-review.md) now executes
the C getter, type-2 dispatcher and memory copy together, including the actual
motion stack packet. It establishes the tested synchronous heap copy and
submission cleanup while retaining the RTOS/physical-delivery boundaries.
