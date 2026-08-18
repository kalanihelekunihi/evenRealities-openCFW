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
virtual file, allocates a payload, delays a task, or sends bytes. The separately
audited `r1_log_export_snapshot_*` implementation supplies the exact bounded
EP/log/cache/crash virtual-file source behind independent owner authorization;
see `DIAGNOSTIC-EXPORT-CORRELATION.md`. FreeRTOS allocation, queueing, delay,
logging, fragmentation, and the undocumented BLE sender remain external. In
particular, openR1 still exposes no live raw private-log export sender or
command.

The Nordic SDK 17.1.0 image retains `r1_export_plan_command` at `0x00035E04`
through the storage API table at `0x0003CADC`. The verified unsigned image
contains 94,804 bytes of text, 236 bytes of data, and 132,544 bytes of BSS;
its 95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`, and
the HEX SHA-256 is
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_export_state_machine.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
