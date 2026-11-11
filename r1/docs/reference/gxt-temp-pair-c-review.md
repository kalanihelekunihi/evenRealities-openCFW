# Exact GXT310 raw temperature-pair output in C

`runtime/native_gxt310_temperature_pair.c` supplies missing stock `0x51260`.
It acquires the bus, enables the sensor pair, calls `osDelay(80)`, reads each
channel, stores its low halfword through the corresponding caller pointer,
disables the pair, and tail-calls bus release. There is no averaging or extra
scale in this entry. The packed volatile halfword view preserves native
unaligned accesses and ordered overlapping writes without asserting pointer
alignment or adding another data owner.

Empty register observations retain the second pointer in R4, the first in R5,
and incoming R6 at provider boundaries. The native 16-byte frame is restored
before the final release, which sees the original caller registers/SP/LR.
Its raw R0 is observed unchanged at return; the C entry itself returns void.

`tools/build/qualify_sources.py` selects the complete 44-byte routine. The
product executes the already-qualified C temperature-channel wrappers, passing
raw address words `0x90`/`0x94` to the final read provider. The runtime suite
passes 64,512 paired stock/C cases over 12 output layouts: equal, one-byte
overlapping, adjacent, disjoint, aligned and unaligned pointers. Raw high-word
values, halfword boundaries, callback mutations, provider errors and both
interrupt-mask states are covered. Tests compare the two ordered halfword
stores, provider snapshots, live R4–R11, saved-frame accesses, final output and
guards, SP/masks and observed final R0. Wrong destination, widened store,
wrong delay and omitted release variants are rejected.

All 585 R1 units compile. All 584 earlier objects and the 164 application / 34
bootloader import sets remain unchanged. Only these 44 newly qualified bytes
enter the source plan; channel wrappers and state owners are reused. The
canonical hybrid now contains 4,245 source-built bytes, 641,915 fallback bytes
and 248 resource bytes. Application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

Bus/mode/delay and final sensor-read providers are modeled. Caller-clobbered
registers/flags except observed final R0, electrical response, actual timing,
faults, arbitrary aliases/concurrency and complete source-only rebuilding
remain unproven. Probes, REA readback, qualification and audit are under
`build/goal-r1-gxt-temp-pair-c`; durable evidence is in the adjacent JSON.
