# G2 quicklist mutex and common-event object recovery

Status: read-only, fail-closed closure of stock 2.2.6.10
`app\gui\quicklist\quicklist.c`.

## Result

The single 94-byte baseline anchor expands to `[0x004FFA70,0x004FFBD8)`:
four functions / 310 instruction bytes plus a 50-byte alignment/literal pool,
for 360 physical bytes. Baseline Ghidra missed the 88-byte
`quicklist_data_mutex_init` and the 110-byte stored
`Quicklist_common_data_handler`; the 94-byte lock and 18-byte unlock helpers
were already defined.

The initializer lazily invokes `osMutexNew`; lock uses `osMutexAcquire` with
`osWaitForever`, and unlock conditionally invokes `osMutexRelease`. The stored
handler accepts event 0, invokes the first-party quicklist parser and ready
test, then refreshes local UI state on success. Other events are logged.

Twenty-five image-wide BL sites reach exact entries: one is the handler's
internal initializer call and 24 are external. The handler has the sole stored
Thumb pointer at `0x006A45F4`. All 129 instructions, 22 body calls, the one
path pointer, adjacent objects, and absence of interior or unknown entries are
pinned.

## Dependency result

No third-party implementation is embedded. Fifteen calls are EasyLogger
diagnostics at selected 2.2.99-equivalent commit `a596b264…`. The three mutex
calls are exact, production-source-owned CMSIS-FreeRTOS v10.5.1 wrappers at
commit `d213f261…`. Three remaining calls are first-party quicklist protobuf
and UI providers; their generic nanopb ancestry terminates at the admitted
0.4.7–0.4.9.1 seam. The object adds no dependency family or version
discriminator, and its private producing commit remains unavailable.

The object follows a dashboard status sender/pool and ends exactly before the
separately closed health mutex initializer. It is not production-routed.

## Reproduction

```sh
make quicklist-closure
```

The target performs authenticated read-only analysis and tests only.
