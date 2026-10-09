# I2C slave dispatch and reached helper closure

Unchanged public SlaveInterrupt matches `[0x9B0C,0x9C38)`300bytes after
linkage. All reached source/helper/assembly sections also match. One new selected
extent/300bytes awaits independent review. Six newly matched private helpers
total1,456bytes outside the54entrydenominator; they are separately reported.

Helper extents: HsMode `0x9344`128bytes; Stop `0x93C4`332bytes;
Ack `0x9510`168bytes; Address `0x95B8`400bytes; DataReceive `0x9748`180bytes;
DataTransmit `0x97FC`248bytes. Each location was first identified by unchanged
non-relocated source bytes, then every reached direct BL was independently
checked against the original instruction target before linking.

The slave interrupt frontend dispatches receive, high-speed mode, stop,
address and transmit handling. Receive drains through the matched FIFO read
wrapper; transmit uses matched data/default write wrappers and critical helpers.
Address and high-speed/stop paths adjust RX FIFO trigger levels through the
authentic inline body. ACK processing is shared by address handling. These are
source-backed handler/context interfaces, not opaque injected providers.

Reusable implementation/pseudocode is the unchanged Apache-2.0 public
`drivers/source/cy_scb_i2c.c` in the pinned PDL input; it includes the six named
handlers and their context accesses. `results.json` records exact bytes/hashes
and all original calls; `link.py` reproduces closure without source rewrites.
No I2C bus event fixture, concurrent state, interrupt delivery, physical transfer
or whole-firmware/source-completion claim is made.
