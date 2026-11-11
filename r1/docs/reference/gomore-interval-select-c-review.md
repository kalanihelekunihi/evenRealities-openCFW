# R1 native sleep interval selector in C

`r1/src/application/runtime/native_gomore_interval_select.c` reconstructs
stock application routine `0x72572` from the pinned R1 2.2.6.0009 image.
It stages the stored 32-byte record when the native context enable byte at
`+184` is not 1. Otherwise it copies the 40-byte source at `+192`, sets its
second word from the live current-word pointer, and calls the existing C
interval compose provider with mode 1, two zero control words, the stored
record at `+272`, aggregation at `+232`, and policy at `+304`. It publishes
composed bytes only when candidate byte 26 has bit 3 set; otherwise it
publishes the stored record. All copies use the already sourced native move
provider. No executable stock bytes or assembly are embedded.

The ignored fixture at `build/r1-interval-select-probe-20261110/compare.py`
executes stock and linked C in Cortex-M4 Unicorn environments with the same
modeled clear, move, setter and compose providers. All 576 paired cases
matched complete output/context bytes and provider order/arguments: enable
0/1/2, candidate flag clear/set, four output destinations including aliases
to stored and source state, and 24 seeded state patterns. The stock binary
SHA-256 is `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Provider internals and physical behavior remain outside this fixture.

The current manifest has 964 R1 units in 751 source files, all built, and
`make sources-check` passes. The R1 source build compiles 882 application and
82 bootloader units with no duplicate strong symbols. The strict bootloader
link remains complete and vector-valid. The strict application report at
`build/r1-interval-select-c-20261110/app-link/report.json` removes the
selector import but still has 38 undefined symbols and exceeds flash by
30,136 bytes. `git diff --check` passes. Byte identity is not established.
