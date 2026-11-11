# R1 LIS2DW12 INT1 route getter in C

The getter at stock `0x756CC` now uses C to read one byte from register
`0x23`, propagating the transport status unchanged. The auxiliary unit now
includes the pinned ST header. The setter's declaration matches the header's
context/route arguments and signed return type; its assembly is unchanged.
The two tap-boundary instruction bodies are also unchanged.

All 2,096 callback comparisons pass: every byte value, four transport
statuses, callbacks that write or leave the buffer untouched, null/all-one
handles and destination offsets 0–3. Callback arguments, returned status,
destination bytes, r4–r11 preservation, entry SP and callback eight-byte
alignment are checked. Five more comparisons cover normal/mutated context
reads, null/truncated contexts and an unmapped callback. Access order and
fault kind/address/size match; complete fault-time register state is not
compared.

REA confirms the register and length setup, though its inferred pseudocode
signature says void. Stock instructions leave the transport's post-call r0
unchanged, and the execution checks verify status propagation. The compiled
C body is 10 bytes versus stock's 14 and tail-calls the transport, changing
private callback stack depth. No byte, private spill or timing identity is
claimed. Physical sensor interrupt routing and I2C behavior remain untested.

All 561 R1 units compile and both compositions pass without duplicate strong
symbols. Actual unresolved sets remain 238 application and 34 bootloader.
`make sources-check` passes for both device trees. No source-plan selection
or workflow gate changed.

[lis-c-route-get-review.json](lis-c-route-get-review.json) binds source/header,
build, native/candidate bytes, REA data and ignored probe hashes under
`build/goal-r1-lis-route/`.
