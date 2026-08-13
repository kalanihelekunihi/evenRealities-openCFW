# IQS7211E ATI-error diagnostic audit correlation

## Decision

The 372-byte function `0x00041A40..<0x00041BB4` has exact SHA-256
`51820b7e27a675b7dd1b217f477e4aeaa7d3cd75ee5dd913bbdae642d4c109c3`
and one direct caller, `0x0006FA2A`, inside the R1 IQS7211E ATI-error recovery
adapter. It is R1 diagnostic policy around the attributable IQS7211E provider,
CMSIS tick source, and logging framework. It is admitted as
`r1_product_specific` / `clean_room_behavior_only`.

The clean implementation is split into `r1_iqs7211e_ati_audit_begin` and
`r1_iqs7211e_ati_audit_summarize` in
[`../../src/r1_iqs7211e.c`](../../src/r1_iqs7211e.c). This split
lets an executor perform the provider read only when the recovered cadence says
it is due.

## Recovered behavior

Every call increments a UInt32 sequence with wrap. Sequence 1 is audited
immediately. Later calls audit when unsigned tick subtraction from the prior
audit is at least 10,000 ticks; the stored tick changes only for an audit.

An audit requests a read from IQS7211E address `0x56`, register `0xE3`. The
recovered 7x3 layout reads 21 little-endian UInt16 values (42 bytes); the 8x3
layout reads 24 values (48 bytes). The clean policy reports these parameters
but performs no bus operation.

For each channel, a missing configuration map includes every value. With a
map, byte `0xFF` excludes the corresponding channel. Included values retain
their source order and determine the active count, minimum, and maximum. An
empty active set produces minimum and maximum zero. The recovered formatter
uses exact literal `%u ` and labels `7x3` / `8x3`; formatting and publication
remain with the logging provider.

## Provider boundary and verification

The closure does not recreate Azoteq register transport, CMSIS tick retrieval,
the existing R1 I2C port, or either logging backend. The pinned IQS7211E
references corroborate the ATI-error and compensation vocabulary; register
`0xE3`, cadence, layout selection, channel mask, and summary behavior are
recovered R1 configuration and policy.

Host tests cover first-call scheduling, 9,999/10,000-tick boundaries, UInt32
sequence and tick wrap, both layouts and read lengths, null/all-disabled maps,
stable value order, min/max, and invalid-input immutability. The same routines
are compiled freestanding for Cortex-M4 and retained in the unsigned Nordic SDK
image at `0x000366B4` and `0x0003670C`. The image contains 90,956 bytes of
text, 236 bytes of data, and 132,456 bytes of BSS; its 91,192-byte BIN has
SHA-256 `31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`
and its HEX has SHA-256
`0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81`.

Reproduce the evidence with:

```sh
python3 scripts/firmware/summarize_r1_iqs7211e_ati_audit.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```
