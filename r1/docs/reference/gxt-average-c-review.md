# Exact GXT310 average and channel wrappers

The exact frame/instruction contract below is superseded by the [ordinary C average](gxt-average-pure-c-review.md). Its 48-byte comparison selection is retired; the four channel adapter selections remain.

`runtime/native_temperature_average.c` supplies missing stock `0x50e1c` in C.
It acquires the bus, enables the sensor pair, calls `osDelay(80)`, reads the
channel-0 and channel-2 temperature values, disables the pair, and releases
the bus. Provider errors do not skip cleanup or alter this call order.

Addition wraps as a 32-bit word before interpreting the sum as signed.
Division by two truncates toward zero; multiplication by 100 wraps modulo
2^32. An empty R0 observation preserves the stock signed intermediate before
multiplication. Without it, Clang emitted a logical shift that produced the
same final wrapped result but differed from the stock arithmetic shift.
Every executed operation remains C. Empty R4 constraints retain incoming R4
before the first read, the first value before the second read, and the wrapped
sum during cleanup. The native provider frame is eight bytes.

`tools/build/qualify_sources.py` independently selects all 48 bytes of the
new routine. It also selects four existing six-byte channel wrappers from
`native_temperature.c`: two temperature reads and two one-shot forwards. They
pass raw address words `0x90` or `0x94` to their native providers. Only these
72 newly proven bytes enter the source plan; other qualification results were
already selected and are untouched.

The product routine passes 10,240 paired stock/C cases over signed boundaries,
odd negative sums, wraparound, maximum/minimum words and seeded full-word pairs,
with success/error statuses and two interrupt-mask states. The tests execute
the actual qualified C channel wrappers, model their final read provider,
and compare ordered provider calls, live R4–R11, saved-frame accesses, final
R0 and preserved masks/SP against stock and an independent arithmetic oracle.
The four qualified wrappers pass another 128 direct cases. Unsigned averaging,
wrong scale, wrong delay and omitted release variants are rejected.

All 582 R1 units compile; all 581 previous objects are identical. Import sets
remain 164 application / 34 bootloader. The original temperature source is
unchanged: the new root lives in its own unit to retain external call boundaries.
The canonical hybrid has 4,155 source-built bytes, 642,005 fallback bytes and
248 resource bytes. Application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

Bus/mode/delay and final sensor providers are modeled; electrical behavior,
actual timing, arbitrary aliases/faults/concurrency and complete source-only
rebuilding remain unproven. Runtime comparison excludes caller-clobbered
registers/flags except final R0. Reproducible probes, REA readback,
qualification and audit are under `build/goal-r1-gxt-average-c`; durable results
are in the adjacent JSON.
