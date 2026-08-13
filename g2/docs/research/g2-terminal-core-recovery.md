# G2 terminal core recovery

Status: read-only, fail-closed closure of stock 2.2.6.10
`app\gui\terminal\terminal.c`.

## Result

The single 122-byte baseline `terminal_request_display` anchor expands to the
complete `[0x005E42EC,0x005E47CC)` translation unit: nine functions / 1,144
instruction bytes plus a 104-byte terminal pool, for 1,248 physical bytes.
Baseline Ghidra missed eight functions, including the mutex helpers, display
exit path, data dispatcher, and three stored callbacks. Sixty-eight image-wide
direct BL sites reach exact entries, 60 externally; all 460 instructions, 73
body calls, three stored Thumb pointers, retained strings, adjacent boundaries,
and the absence of strict-interior or unknown direct targets are pinned.

The object lazily creates and forever-acquires a terminal action mutex. Display
requests use message ID `0x30`, carry eight bytes, and are gated to role value
one and initialized terminal state. The input callback accepts IDs `0x08`,
`0x0A`, `0x44`, `0x45`, `0x48`, and `0x4A`, swapping the `0x44`/`0x45` pair
before forwarding. The data handler dispatches command IDs 1 through 11,
`0xA3`, and `0xFF` into first-party terminal UI/service handlers with fixed
payload sizes.

## Dependency result

No third-party implementation is embedded. Thirty calls are diagnostics at
the admitted EasyLogger 2.2.99-equivalent selected commit `a596b264…`. The
three mutex calls are exact, production-source-owned CMSIS-FreeRTOS v10.5.1
wrappers at commit `d213f261…`. Three calls are bounded IAR memcpy/memset
primitives, and the remaining 29 terminate in first-party role, protobuf
service, UI lifecycle, and command providers. The object has no direct nanopb
or LVGL implementation edge, adds no dependency family, and supplies no new
version discriminator.

The private source and producing commit remain unavailable. The terminal
protobuf schemas and screen implementation are separate first-party objects.
This core object is not production-routed.

## Reproduction

```sh
make terminal-core-closure
```

The target performs authenticated read-only analysis and tests only.
