# G2 bootloader chunked source-comparison closure

The authenticated entry `[0x0042DA1E,0x0042DAD0)` is a 178-byte bounded
source-reader and comparison service. It processes at most 4,096 bytes per
iteration, invokes the reader through the supplied context, compares the
staging buffer against the expected source, logs successful chunks and the
first failure, and returns the comparison status. Its sole caller is
`0x0042DC2A`; no interior or stored entry exists.

`runtime_chunked_source_compare_42da1e.c` is first-party MIT clean-room source.
Apple clang 21 and Homebrew clang 22 reproduce every stock byte after strict
prepare, logging, memory-comparison, and failure-logging calls. Relocated
SHA-256 is
`4addc6bfb9023df944da168fed7deb268b2de24817dd19865719e37f4131216b`;
unrelocated SHA-256 is
`bb1588dad52910df21eed899b2baeca89620ce541261e8e511fecd04f539e471`.
Portable tests cover zero, one-byte, exact 4 KiB, boundary-crossing,
multi-chunk, second-chunk mismatch, and invalid-input behavior.

No hardware operation occurred. Live storage, memory-controller,
DMA/coherency, concurrency, reset, and cold-boot qualification is blocked by
unavailable physical evidence. Firmware-wide completeness is not claimed.
