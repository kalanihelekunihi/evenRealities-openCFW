# Ring TX allocator budget and cooperative shutdown prerequisites

Completed 2026-10-01. Continues the [queue ownership batch](../ring-tx-ownership-2026-10-01/README.md).
The normal inline-message design now has concrete allocation bounds. Cooperative
shutdown does **not** establish a completed WSF drain or exclusion of all TX
producers; this batch stops at that exact boundary rather than inventing one.
No firmware modification, hardware access, commit or shared campaign update.

## Deliverables and provenance

- [allocator_lifecycle.pseudocode.c](allocator_lifecycle.pseudocode.c): manual
  reconstruction of allocation/free and the relevant lifecycle paths, with
  omitted branches and provider boundaries stated.
- [ring_tx_budget.h](ring_tx_budget.h): safe host-side allocation/MTU budget
  helpers for evaluating proposed layouts, not firmware management code.
- [verify.py](verify.py), [validation.json](validation.json),
  [disassembly.txt](disassembly.txt): **49 passing stock-instruction scenarios**,
  15 hashed bodies / 2,964 bytes, fresh SRAM initialization and concrete traces.
- [test_budget.c](test_budget.c), [host-validation.txt](host-validation.txt):
  26 layout-boundary vectors match original allocator behavior; additional
  assertions cover negotiated-MTU bounds and size-overflow rejection.

Input: `g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, 3,523,396 bytes,
SHA-256 `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
ARM Thumb/M-class code uses file offset + `0x00437FE0`.

The pool configuration and task callback records reside in **compressed SRAM
initialization data**, not a directly readable flash table. The verifier executes
stock initializer `0x0043A11E` on descriptor `0x0075D3F4`, regenerating 17,752
bytes at `0x20000000`; SHA-256
`df1a1fdf7b2792a7c4ef7a2c5cc6d1423bc7833b556fdfcedb8d6d927fbbb743`.
This matches the prior independent initializer review, but the new verifier does
not require ignored decoded output or execute a shared campaign script.

## Actual allocator configuration and limits

Startup `_bleExactleStackInit` (`0x004B7F64`) supplies
`WsfBufInit(0x2940, 0x2004FA98, 4, 0x200003B0)`. The freshly decoded configuration
at `0x200003B0` is `10 00 08 00 20 00 04 00 40 00 0A 00 E0 01 14 00`.
Original `WsfBufInit` (`0x00530364`) constructs these pools:

| Block bytes | Count | Block storage start | Storage end, exclusive |
|---:|---:|---|---|
| 16 | 8 | `0x2004FAC8` | `0x2004FB48` |
| 32 | 4 | `0x2004FB48` | `0x2004FBC8` |
| 64 | 10 | `0x2004FBC8` | `0x2004FE48` |
| 480 | 20 | `0x2004FE48` | `0x200523C8` |

Four 12-byte descriptors precede storage. Initialization consumes `0x2930`
bytes (10,544) of the `0x2940`-byte arena. The largest block is **480 bytes**.
`WsfBufAlloc` (`0x00530446`) scans in order and uses the first fitting nonempty
pool. If that class is exhausted it tries larger classes, then returns null;
there is no heap fallback in this body. An exhaustion test consumes all 42
blocks in class order. Free/reallocate tests confirm reuse.

`WsfMsgAlloc` (`0x004BF99E`) reserves eight bytes before the public message.
Thus its maximum nonwrapping public message size is **472 bytes**. The wrapper
adds eight then narrows for the u16 allocator: an explicit original-instruction
test shows request 65,528 wrapping to allocator size zero and obtaining a
16-byte block. Proposed callers must reject oversized arithmetic before calling
this API. This is an API edge-case test, not a demonstrated reachable ring input.

`WsfBufFree` (`0x005304D4`) assumes a valid allocation pointer; it is not a bounds,
alignment or double-free validator. The proposed ownership discipline must
continue to supply only valid, singly owned WSF allocations.

### Inline payload and ATT budgets

Let N be ring payload bytes and H the public ring-message header bytes.

| Proposed representation | Required block bytes | Pool-only payload ceiling |
|---|---:|---:|
| Existing 12-byte shape with inline payload | `8 + 12 + N` | 460 |
| Extended 16-byte header with inline payload | `8 + 16 + N` | 456 |
| ATT's own packet copy | `8 + 11 + N` | 461 |

Additionally, ATT Write Command needs `N + 3 <= negotiated_MTU`, as recovered
in the prior ATT batch. Therefore the existing-header inline design's ceiling
is `min(460, negotiated_MTU - 3)` for MTU >= 3. This is neither a claim that the
ring negotiates a large MTU nor a claim that every payload up to this size is a
valid ring command. At MTU 23 the write payload ceiling is 20.

For H=12, payloads 0–12 use a 32-byte block, 13–44 use 64, and 45–460 use 480
when those preferred pools are available. For H=16, boundaries become 0–8,
9–40, and 41–456. Normal recovered 4–8-byte commands remain in the 32-byte
message class under either proposal.

**Peak capacity matters:** the inline message still exists when ATT allocates
its copy. A stock-allocator test leaves one 480-byte block free, successfully
allocates the 460-byte inline-message payload, then fails the ATT copy allocation.
After freeing the inline message the ATT allocation succeeds. Large sends need
at least two simultaneously available large blocks, plus ATT's separate message
envelope. The pools are shared; nominal counts are not runtime availability.

### Epoch field option

The existing outbound `0xAC` record has an unused trailing halfword at public
+10, whereas receive records use that offset as an ATT handle. It is a candidate
for a TX-only 16-bit epoch without increasing H from 12. That is a **proposal**,
not a verified change: review every consumer for this event and define how
connection/epoch are captured consistently across waiting and reconnect.
A 16-bit epoch also wraps; it cannot distinguish indefinitely retained records
across a full epoch cycle. Do not silently equate it with permanent uniqueness.

## Cooperative lifecycle path recovered

Fresh initialized SRAM contains:

| Task descriptor | Create pointer | Deinit pointer |
|---|---|---|
| ring `0x20004120` | `0x004C4DA5` | `0x004C4DD1` |
| BLE WSF `0x20004068` | `0x004D0AF7` | `0x004D0B1D` |

These stored deinit callbacks are different from the cooperative exit mechanism
below. Available direct-call metadata has no callers for the two deinit bodies;
that alone is not proof they are never called indirectly. The examined manager
mode-event paths request flags rather than invoke those callbacks.

The task manager event handler `0x004C995E` uses retained diagnostic strings to
identify modes: bit 0 poweroff, bit 1 reboot, bit 2 ship mode, bit 3 low power,
bit 4 temperature abnormal, bit 5 OTA. They are independent tests, not a switch.
OTA has a one-time guard. Each applicable mode calls `0x004C9778`, which:

1. Calls `0x004C96B6` to post exit flag `0x800000` to selected tasks.
2. Waits for the resulting acknowledgment mask, options 1, **5,000 kernel ticks**.
3. Logs mismatches, then returns even when the wait timed out.

The ring task (ack index 6) is included in all examined modes. OTA skips BLE RX,
BLE TX and BLE WSF (indices 7, 8, 9); other modes request all three as well.
Expected masks are `0x187A` for OTA and `0x1BFA` otherwise. Twelve tests cover
six mode bits with successful and failed acknowledgment waits; a further test
verifies repeat OTA suppression. This proves control flow with synthetic wait
results, not task completion in a real scheduler.

Ring flag handler `0x004C507E` processes its input-queue flag `0x400000` before
exit flag `0x800000` when both are present. Its exit body `0x004C53A6`:

1. Publishes ack bit 6 through `0x004C9C3C` **before queue deletion**.
2. Deletes the ring CMSIS input queue if present, then zeros its stored handle.
3. Loops in `osDelay(UINT32_MAX)`.

Tests verify that order, both with exit alone and combined queue/exit flags.
The input drain is a stub in these tests: they verify its call order, not that
all work disappeared. An exit-only flag does not itself call the drain.
The input queue is not the global WSF queue; neither its deletion nor ack proves
that previously queued `0xAC` sends have been consumed.

`ring_task_msg_send` (`0x004C549C`) returns -1 when the input queue handle is
zero, tested after synthetic deletion. That gate does not cover all direct
`APP_BleRingSendDataMsg` producers. Corpus direct callers include five service
encoders and `0x005814D4`, which parses into a local 128-byte buffer and calls
the ring sender directly. Its execution context/quiescence is not established
by deleting the ring input queue.

## Exact remaining boundary and design requirements

The inline design is feasible for the recovered command sizes, subject to pool
availability and MTU. It uses existing WSF envelope ownership and normal
handler-return cleanup, established in the previous batch. It does **not** by
itself solve teardown or connection-generation races.

The examined BLE WSF entry (`0x004D0A4C`) loops in `wsfOsDispatcher`; neither
examined body supplies a ring-TX shutdown barrier for the manager's thread exit
flag. A manager ack may precede ring queue deletion, and manager timeout does
not enforce failure. Consequently **all-producers-stopped + WSF-drained is not
proven**. No whole-system leak, dropped-command occurrence or unsafe hardware
shutdown is inferred from these partial facts.

Before implementing a lifecycle-safe patch, specify and verify a transition
that prevents new ring TX from every producer, waits for or explicitly disposes
of owned pending records, and only then resets/deinitializes the queue/allocator.
The epoch snapshot must be synchronized with connection changes; checking only
numeric connection ID or sampling an epoch before an unbounded wait is inadequate.
Pool exhaustion must have defined token/error behavior. Do not reset pools while
messages or ATT packets still reference their blocks.

This batch stops at whole-system scheduling/power-transition behavior. To close
that boundary requires either a faithful offline scheduler/lifecycle model or an
existing trace for the relevant mode showing: task identities and flags; producer
entry/return; pending WSF queue records; outstanding ATT allocations; and the final
reset/power transition. A static or runtime account of the direct command
producer's disable path is also needed. No new firmware image is required for
the allocator facts, and no hardware run was requested or performed.

## Reproduction and limits

```sh
~/.local/share/opencfw/venv/bin/python g2/analysis/ring-allocator-lifecycle-2026-10-01/verify.py
clang -std=c11 -Wall -Wextra -Werror -fsyntax-only g2/analysis/ring-allocator-lifecycle-2026-10-01/allocator_lifecycle.pseudocode.c
clang -std=c11 -Wall -Wextra -Werror g2/analysis/ring-allocator-lifecycle-2026-10-01/test_budget.c -o /tmp/opencfw-ring-budget-test
/tmp/opencfw-ring-budget-test
```

Result: `PASS 49 cases; 15 body hashes; fresh stock SRAM initializer`. Host
vectors match allocator traces; syntax checks pass. Capstone 5.0.7 / Unicorn
2.1.4; macOS Unicorn requires native JIT access outside the restrictive sandbox.
Allocator functions and initializer execute original instructions. Critical
sections are no-ops in the single-threaded harness; logging is disabled. RTOS
flags, waits, queue deletion, delay and ring input drain are explicit stubs.
There is no full scheduler, radio, final power transition, or complete-source
claim. All new outputs are confined to this directory.
