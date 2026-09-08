# GX8002 keyword-list registration and logging

The macOS C-SKY build reconstructs `LvpPrintMaxKwsList` from NationalChip
`lvp/vui/kws/max_decoder.c` at commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`. The builder authenticates the
source, license, and exact parameter type definitions against Git blob IDs.
The implementation sets the list to the two independently recovered wakeword
records, then logs their names, event values, and thresholds.

The compiled function occupies all 120 original bytes at runtime `0x10208880`
(package offset `0x11e0c`) with the original 32-byte frame. Its five C string
initializers supply 97 bytes that match the original strings exactly. The list
has a real eight-byte C BSS definition at `0x2002e79c`; NOBITS storage adds no
payload bytes to the ownership ledger. The parameter table is separately
source-owned at `0x20026c7c`, with two 88-byte records.

The decoded stock and compiled functions independently match a state-machine
oracle in 546 cases. Comparisons include ordered count/pointer initialization,
count reloads at iteration boundaries, pointer reloads before each field,
format pointers and meaningful variadic arguments, ordered field reads,
final state, and saved-register/stack restoration. Calls clobber caller-saved
registers. Logging-boundary mutations change the live count and table pointer,
including shrinking midway through a row and alternating valid tables.
Nine regression tests reject cached state, wrong field offsets/stride, and
incorrect frames, and check early termination and invalid-domain handling.

The modeled live count is 0..2 with pointers to valid two-record tables.
Corrupt counts are rejected by the harness rather than silently clamped.
Synthetic table fields exercise full-width values. This is not an arbitrary
interrupt, printf implementation, or physical hardware timing qualification.
The unsigned loop comparison follows the observed target; the source does not
claim that an out-of-range count is safe. Full MAX scoring and strategy remain
separate recovery work. The notice is `NATIONALCHIP-MAX-NOTICE.txt`.

Reproduce with:

```sh
python3 g2/tools/verify_gx8002_max_list.py
python3 -m unittest discover -s g2/tests -p test_gx8002_max_list.py
```

The reviewed machine-readable evidence is
[gx8002-max-list-verification.json](gx8002-max-list-verification.json).
