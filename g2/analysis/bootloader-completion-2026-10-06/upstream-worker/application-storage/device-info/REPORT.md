# Stock device-info snapshot helper

`device_info.c` reconstructs the bounded stock helper at `0x41d294` as
`opencfw_boot_device_info_initialize(volatile uint32_t *record)`. This helper
is reached by mode 1 of `0x41d792` (the range callback's current original-side
field cut). It fills a 16-word record. The range consumer uses word 11 at
offset `0x2c`; the same function also captures five system-status words,
clock-factor words at offsets `0x20/0x24/0x28`, and core-debug snapshots at
`0x30..0x3c`.

The source preserves ordered volatile reads and ten calls to
`opencfw_hal_delay_us(10)`. The clock-factor table is a source-owned 12-halfword
array at the locked address `0x433754`; the range-limit table is provided by
`storage_callbacks.c` at `0x43401c`. The standalone source ELF contains both
tables at those addresses. Its machine starts with zero-filled image data and
asserts that each source-ELF table equals the corresponding locked bytes; it
never copies original tables into the source machine.

Run from this directory with `make verify`. The ARM Cortex-M4 source compiles
with `-Wall -Wextra -Werror`; original/source Unicorn comparison passes 80
fixtures across all four range selectors and clock selectors, with complete
64-byte record equality, ordered MMIO-read equality, and ten delay calls of
argument 10 in each case. The run covers 336 distinct original instruction
bytes. Raw image and per-file source hashes are stored in `out/comparison.json`.

For integration, add `device_info.c` to the existing application-storage
module and call `opencfw_boot_device_info_initialize` into the same 64-byte
temporary record used at the `0x41d792` mode-1 call. The existing source-owned
range table must be linked at `0x43401c`; the new clock-factor array occupies
`0x433754`. `opencfw_hal_delay_us` is an explicit sibling provider and can map
to the existing delay implementation. The test intercepts stock `0x41f9e6`
and source `opencfw_hal_delay_us` as ordered 10-unit delays; it does not execute
the lower wait implementation at `0x41d1c0` or make timing claims.

This closes the `0x41d294` snapshot provider and its table data. It does not
claim the complete `0x41d792` dispatcher: the other selector paths and their
status/peripheral side effects remain outside this profile. The parent callback
profile's original-side cut should be replaced by the exact mode-1 setup and
this source provider when its current integration baseline is released.
