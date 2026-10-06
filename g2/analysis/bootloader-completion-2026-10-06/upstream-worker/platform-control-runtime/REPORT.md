# Platform-control runtime providers

The provider sources are `platform_control/runtime.c` / `runtime.h`, plus the isolated transition candidate `runtime_transition.c` / `runtime_transition.h` and query provider `runtime_query.c` / `runtime_query.h`. Mode one reuses `clock_manager/clock_class_providers.c` for stock `0x41d92c`; the transition profile reuses `critical_save.S` for `0x41b8ec`.

The isolated Cortex-M33/Unicorn differential passes 171 cases against locked image SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b`, comparing 876 distinct original instruction bytes. `make verify` writes case details to `out/mode-one.json`. The source machine maps only compiled source segments, synthetic RAM/MMIO, and the two mode-one literal inputs at `0x434158` and `0x43415c`; it does not map stock executable bytes, so source cannot silently fall back to firmware instructions.

## Query table and helpers

`runtime_query.c` defines a typed table of 34 four-word descriptors from stock data at `0x430660`. Each descriptor contains command register, command mask, status register, and status mask. All 34 descriptors were compared directly against the raw copier output. Selector 20, used by cleanup, is exactly `[0x40021004, 0x00040000, 0x40021008, 0x00040000]`.

`opencfw_boot_control_query_descriptor_copy(destination, selector)` models stock `0x41b8f8`: null destination or selector >=34 returns 6; otherwise it copies the selected 16-byte descriptor and returns 0. `opencfw_boot_control_query(selector, result)` models `0x41c2d8`: null output returns 6; otherwise it clears the output, byte-truncates the selector, invokes the descriptor copier, reads the descriptor's status register, stores whether the selected mask is nonzero, and returns 0. The source machine uses this static typed table and does not map firmware bytes. The stock profile executes `0x41c2d8`, `0x41b8f8`, and the actual stock 16-byte copy helper `0x4156ac`.

Tests cover selectors 0–33 for both clear and set status bits; selector byte truncation; invalid selectors 34, 0x22 after truncation, 255, and 0xffffffff; null output; and direct copier valid/invalid/null-destination cases. Cleanup at `0x41c990` now executes its real query path in both stock and source tests, with only the optional finish callback target at `0x41cd60` remaining external.

## Other recovered providers

Mode one at `0x41f8ba` selects records at `0x20000454` with `0x1c` stride, clears byte `+0x18`, reads register IDs from offset 8 and object pointer at offset 4, then calls source `opencfw_bl_power_register_update` with ROM words `0x434158` (3) and `0x43415c` (`0xe083`).

The source prefix for power apply `0x422ba8` returns 2 for a null pointer or when `(object[0] & 0x01ffffff) != 0x01ea9e06`; for a matching object it returns 6 when `operation != 0 && operation > 2`. Accepted operations 0, 1, and 2 continue through `opencfw_boot_control_power_apply_configure(object, operation, (uint8_t)enable)`. The data/resource-configuration tail remains that explicit cut. Differential cases cover null object, zero header, wrong header, and matching header with rejected operation.

Mode two `0x41ba80` uses an exact byte read of saved mode at `0x20000552`, configuration field in `0x40021108`, and current context mode bits in `0x40021000`. The isolated transition candidate reconstructs `0x41b954`: it saves/disables PRIMASK through `critical_save.S`, handles mode-2 wake-control bit 5 at `0x40004044`, calls the status-wait boundary with `(0x0f, 0x40004030, 0x01000000, 0x01000000)`, writes mode bits 0–1 at `0x40021000`, polls the completion bit for at most 20 delay calls, updates the saved-mode byte, and restores PRIMASK with the raw unconditional `MSR` behavior. Callback table dispatch uses base `0x20026e38`, mode configuration slot `+4`, and no-argument mode notification slot `+0x28`.

The stock four-argument wait at `0x41d21c` checks `(*address & mask) == expected`, calls `delay_us(1)` between checks, and returns 4 when its count expires. The separate five-argument `opencfw_hal_status_poll` at `0x41d246` matches it when called with `equal=1`. The delay implementation at `0x41d1c0` remains a timing boundary.

## Integration boundaries

To use the transition candidate, include `runtime_transition.c/.h` and `critical_save.S`, and provide `opencfw_boot_control_delay_us(uint32_t)`; the four-argument status wait can use `opencfw_hal_status_poll(count, address, mask, expected, 1)`. Mode-hook table slots remain callbacks. For accepted power objects, provide `opencfw_boot_control_power_apply_configure(uint32_t *, uint32_t, uint8_t)`. Mode-one also needs `clock_class_providers.c` for the recovered register updater. Query and descriptor-copy symbols are implemented in `runtime_query.c/.h`.

MMIO, callback effects, and delay/completion behavior are synthetic. No physical peripheral effects or timing behavior were exercised, and accepted-object power configuration remains an external boundary.
