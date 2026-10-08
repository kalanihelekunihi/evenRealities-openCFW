# Lazy device-info dispatcher `0x41d792`

`g2/components/bootloader/application_storage/device_info_dispatch.c` provides
`opencfw_boot_device_info_query(selector, record)`, a readable source provider
for the stock selector wrapper. Its standalone profile compiles this dispatcher,
source helper `0x41d294`, source mode-0 helper `0x41d69c`, and the required
selector gate `0x421548`, and required source-owned table data. The source ELF
runs without original-image fallback.

The wrapper returns 6 for a null record and for any selector other than 0 or 1
after `UXTB` truncation. Selector 1 calls `0x41d294` and returns 0. Selector 0
reads `0x40020014`, writes bytes 0 through 10 in the stock order and bit
mapping, invokes `0x41d69c`, ignores its return value, and returns 0. To match
volatile access behavior, the source preserves the first status sample for
bytes 0–2 and reloads the register for every later byte. The initial
differential exposed the stock's repeated reads; reusing one cached word did
not match its MMIO trace.

The same source exports
`opencfw_boot_storage_range_valid(address, size)`. On a zero range cache, that
provider now obtains its limit by calling `opencfw_boot_device_info_query(1,
temporary_record)` and reading record word 11, matching the stock `0x430a60`
cache-miss path instead of projecting the register/table calculation locally.
This executes the full mode-1 snapshot helper and its ten delay callbacks at
cache miss.

`make verify PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python` passes
432 dispatcher/mode fixtures, 112 stock/source range-cache fixtures, and 11
selector-gate fixtures; the profile traces 928 distinct original instruction
bytes.
The matrix covers selectors 0, 1, 2, 3, `0x100`, `0x101`, `0x102`, `0x201`,
and `0xffffffff`; all four low status modes; null records; and mode-0 power,
wait-status, and result boundaries. Selector 1 compares the entire 64-byte
record, ordered MMIO reads, and ten delay callbacks. Selector 0 compares the
record bytes, exact register-read order, wait-call arguments/results, and
return behavior.

The mode-0 helper `0x41d69c` calls selector gate `0x421548` with arguments
`(1, 0x244, 1, &result)`. The source gate truncates the selector to a byte,
allows only selectors 1, 3, and 5, returns 6 for all others, and forwards all
four argument registers unchanged. Eleven direct stock/source selector cases
cover allowed, rejected, and high-bit inputs. The remaining scheduler/event
service at `0x4213e6` is a bounded callback which records arguments and supplies
a wait status plus 32-bit result. On a successful wait, the helper reads
`0x4002000c`. If bits `[7:4]` equal 2, bits `[3:0]` are at least 2, and result
is below 255, it decrements result unless the low nibble is 3, writes byte 1
of record word 3 as 2, and sets bits 16 and 17. The other successful-wait
branch writes the result byte and sets bit 16. A failed wait writes only the
result byte. The callback does not model scheduler or event timing.

The range-cache fixtures invoke original `0x430a60` and source
`opencfw_boot_storage_range_valid` over four mode limits, four cache states,
and seven address/size boundaries. They compare return, cached word, volatile
read sequence, and delay callbacks, including the cache miss that now passes
through selector 1 and record word 11.

Selector 1 calls synthetic delay service `0x41f9e6`/`0x08000200`; all MMIO
and core-debug memory is synthetic Unicorn memory. This evidence establishes
source/instruction agreement under those modeled callbacks, not physical
timing or hardware behavior.
