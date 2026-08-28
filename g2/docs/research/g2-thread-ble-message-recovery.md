# G2 BLE message TX/RX thread recovery

## Result

The two product BLE message-thread translation units are completely bounded
in the authenticated G2 `2.2.6.10` image. The transmit unit contains 21
executable bodies and four owned data islands; the receive unit contains 13
executable bodies and two owned data islands. Every accepted direct call,
stored entry pointer, task attribute, retained source path, and physical byte
range is pinned by `tools/analyze_g2_thread_ble_messages.py`.

The transmit behaviors already have an independently authored, production-
integrated implementation in `components/apollo_main/core_overlay`. Five new
MIT files in that directory now provide an independently authored RX
candidate covering all 13 recovered entry points. Its core queue, lifecycle,
dispatch, and enqueue behavior passes a host harness and all sources compile
for a freestanding Thumb target. The candidate is not yet production-routed:
diagnostic parity and placement-sensitive overlay integration remain open, so
the package still executes official stock RX bytes.

## Authority and physical boundaries

The authority is
`blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`, loaded at
`0x00437FE0`, SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.

| Product TU | Physical interval | Code | Owned data | Physical SHA-256 |
|---|---:|---:|---:|---|
| `thread_ble_msgtx.c` | `[0x00475290,0x00475FC0)` | 21 bodies / 3,096 B | 280 B | `7402dc013b7c00390e68c3881563f9a323e04dba0593bb7b6a2b0b0deca0808a` |
| `thread_ble_msgrx.c` | `[0x0048EDB0,0x0048F3A4)` | 13 bodies / 1,390 B | 134 B | `8dd458f569db89c4a0588af573cb6091abed7e4be60c7ee2bb60e9e7ffcacf9d` |

The receive boundary is exact: nanopb code starts at `0x0048F3A4`, so the
128-byte trailing diagnostic/literal table belongs to the product message
receiver, not nanopb.

## Static task configuration

Both tasks use CMSIS-RTOS2 static allocation, a 112-byte control block, a
16-KiB stack, priority `0x30`, and TrustZone module `1`.

| Property | TX | RX |
|---|---:|---:|
| `osThreadAttr_t` | `[0x0075B85C,0x0075B880)` | `[0x0075B880,0x0075B8A4)` |
| Task name | `ble_msgtx` | `ble_msgrx` |
| Control block | `0x200721B0` | `0x20072220` |
| Stack | `0x20047A98` | `0x2004BA98` |
| Product state | `0x20004020` | `0x20003FFC` |
| Lifecycle index | `8` | `7` |

Each product state stores the task handle at `+0x08` and a 150-element,
four-byte CMSIS message-queue handle at `+0x0C`. Both task loops wait on the
24-bit flag mask `0x00FFFFFF`; queue work is bit `0x00400000` and exit is bit
`0x00800000`.

## Transmit behavior

The TX queue drain recognizes command types `1`, `2`, `4`, and `8`, routes
each recovered record layout to its product transport provider, and frees the
record. Type `2` first probes `threadBleWsfWaitOnce(50)`, tying the queue to
the separately recovered WSF transmit-ready semaphore.

All public enqueue wrappers converge on one 1,002-byte core. It preserves the
four message layouts, 16-bit length arithmetic, source allocation/copy,
stream reset behavior, a 500-tick queue-put timeout, cleanup on failure, and
the queue wake flag. The already integrated clean-room replacement covers all
21 bodies; this audit adds whole-object and ingress closure rather than new
production bytes.

## Receive behavior

`Thread_MsgRxFromBle` creates a word-aligned record using
`(uint16_t(length) + 11) & ~3`, stores the type at `+0`, the low 16 bits of
the length in the word at `+4`, copies payload at `+8`, queues with timeout
`500`, and wakes the RX task with bit `0x00400000`.

The private drain recognizes:

- `0x80`, routed to the provider at `0x004D83D8`;
- `0xC0` through `0xC3`, routed to `0x00448670`;
- `0xC4` through `0xC7`, routed to `0x00458B60`;
- `0x200`, which logs the master-pair erase path, dumps the first 16 bytes,
  and calls `0x004D9010` with selector `3`; and
- `0x400`, routed to `0x00458C5E`.

Every drained record is freed. The unit also owns queue initialization,
thread create/destroy, lifecycle enter/ready, flag dispatch, exit, and queue
clear bodies. Its retained path is `platform\threads\thread_ble_msgrx.c`;
the exact historical source is unavailable.

The clean-room candidate is split across `ble_msgrx_thread.c`,
`ble_msgrx_runtime.c`, `ble_msgrx_lifecycle.c`, `ble_msgrx_dispatch.c`, and
`ble_msgrx_enqueue.c`. The host fixture exercises lifecycle publication,
record construction and failure cleanup, every recovered receive route,
record freeing, queue clearing, and the finite thread-entry test seam. A
separate compilation check emits all five files for `thumbv7em-none-eabi` and
requires exactly the 13 expected global text symbols. Stock diagnostics are
deliberately not claimed complete: the `0x200` hexdump is a replaceable hook,
and retained trace/error messages must be restored before production routing.

## Ingress closure

TX has 151 direct entry calls and 190 decoded outbound calls. Its two genuine
stored entries are the task pointer at `0x00475E68` and creator pointer at
`0x007940C8`. Five raw strict-interior value matches are data accidents.

RX has 12 direct entry calls and 93 decoded outbound calls. Its genuine
stored entries are the task pointer at `0x0048F340` and registered
`Thread_MsgRxFromBle` pointer at `0x004C9C64`. Two unaligned entry-valued
windows and 26 interior-valued windows are rejected as byte overlaps. The
only raw BL-like interior target, `0x0048DF70 -> 0x0048F0CE`, begins on the
second halfword of the valid 32-bit `SMULBB` at `0x0048DF6E`.

No authenticated stored pointer, direct BL, or wide branch enters a strict
interior of either unit.

## Provenance and ownership boundary

The official image is the only exact implementation oracle for these two
product files. CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53` authenticates the thread,
queue, flag, delay, and termination provider ABIs only; it does not confer
source identity or licensing on the product glue.

Both TX and the RX candidate are independently authored OpenCFW source. Only
TX is production integrated. RX candidate availability therefore does not yet
change package source/generated ownership; its stock interval remains opaque
until placement, redirects, and diagnostic parity are reviewed together.

## Reproduction

```sh
python3 tools/analyze_g2_thread_ble_messages.py
python3 -m unittest \
  tests.test_analyze_g2_thread_ble_messages \
  tests.test_ble_msgrx_reconstruction
```

The analyzer authenticates the image and three TSV inputs before checking all
body hashes, physical spans, task attributes, strings, call-edge digests,
stored entries, and false-positive exclusions.
