# Export state-machine correlation

The 364-byte function `0x0004E740..<0x0004E8AC`, SHA-256
`f07a98de9703b681ffa54275f49699297d438fad52e4eeb1e049eb4f3e4e40d3`,
is the R1-owned generic virtual-file export command/chunk state machine. Its
sole direct caller is the queue consumer's `BL` at `0x00045114`. The handler is
also the `generic_handler` already pinned by the static `log.bin` composite
export audit. Its disposition is `r1_product_specific` /
`clean_room_behavior_only`.

Command 0 with result 1 queries descriptor metadata, resets the virtual offset,
starts the selected provider, sends a 10-byte status/length/checksum control
record, waits 50 milliseconds through an external delay provider, and requests
the first data chunk. Other command-0 results return control status 1. Command
1 advances the transfer in chunks capped at 4,096 bytes. Result 2 resets the
offset for retry. Completion invokes the descriptor finalizer; a redundant
post-completion request can return status 3.

The clean-room `r1_export_plan_command` exposes only this bounded state policy.
It produces typed control/chunk/start/finalize decisions and never reads a
virtual file, allocates a payload, delays a task, or sends bytes. The already
audited composite `log.bin` provider, FreeRTOS allocator, queue, delay, logging,
fragmenter, and Nordic BLE transport remain external. In particular, openR1
still exposes no live raw private-log export sender.

The Nordic SDK 17.1.0 image retains `r1_export_plan_command` at `0x00035E04`
through the storage API table at `0x0003CADC`. The verified unsigned image
contains 90,956 bytes of text, 236 bytes of data, and 132,456 bytes of BSS;
its 91,192-byte BIN has SHA-256
`31f3a97de9805239b03c51297f1de2ea9eaeff6fee372f1ea1f0c0a5c2f7bc91`, and
the HEX SHA-256 is
`0954a9375874ee4f88139ba6243e20e1afba122e67afccba9d410e638053fa81`.

Reproduce with:

```sh
python3 scripts/firmware/summarize_r1_export_state_machine.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```
