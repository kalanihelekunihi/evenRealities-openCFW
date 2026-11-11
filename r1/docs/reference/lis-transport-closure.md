# R1 LIS2DW12 transport and FIFO closure

The excluded `native_lis_registers.c` and `native_lis_fifo.c` mixed unique
providers with superseded public wrappers. Eighteen duplicate wrappers were
removed: seventeen register-frame adapters and the FIFO-level adapter. The
canonical implementations remain in `native_lis_call_frames.c`. The two
trimmed units now participate in relocatable composition, providing read and
write transport, burst read, the outer FIFO reader and its context prefix.
Retained assembly statements were unchanged by that consolidation; no new
stock-function body was introduced. The later
[C transport conversion](lis-c-transports-review.md) replaces the read/write
bridges, with its code-generation and fault-state limits recorded separately.

REA/Ghidra checked the locked application's FIFO reader at `0x750E8`
(52 bytes), burst reader at `0x750A0` (24 bytes), and FIFO-level routine at
`0x753AC` (26 bytes). Original read/write transports are at `0x757C4` and
`0x759E6`. The analysis ELF contains the complete unchanged application bytes
at the native load address, with analyst-supplied Thumb seeds for these five
entries. It is an analysis artifact, never a firmware input.

Direct stock-versus-source execution passes 1,023 comparisons: 18 read
transport, 18 write transport, 96 level, 27 burst and 864 outer-reader cases.
Checks include callback order, captured handle, register, length, pointer
position relative to the caller's stack or destination, callback stack depth,
return value, destination bytes, SP and r4–r7 preservation. The test ELF links
the actual canonical call frames and field helpers without unresolved symbols.
No helper is silently replaced by an address-zero linker placeholder.

The native behavior includes several unusual cases that are preserved:

- FIFO level always publishes the scratch byte masked to six bits, including
  failed reads that do not write it. That byte can derive from incoming r3.
- The outer reader ignores transport status and returns the capped sample
  count. A nonzero level with a zero request still invokes a zero-length burst.
- Burst transfer length is `(samples * 6) & 0xffff`, including wraparound.

These are recovered contracts, not claims of ideal device behavior. The
controlled callbacks cover success, nonzero and negative status values, both
writing and leaving read storage untouched, count boundaries and large burst
arguments. Physical accelerometer behavior and startup context installation
remain unverified.

The complete build compiles all 561 R1 units and composes both payloads with
no duplicate strong symbols. Four application imports resolve, reducing 248
to 244; bootloader imports remain 34. No aliases, executable blobs or source
qualification selections were added. These existing ABI bridges still contain
inline assembly, so this consolidation does not establish a pure-C firmware
or byte-identical source build. Full compilation, pseudocode coverage and
byte identity remain separate requirements.

[lis-transport-closure.json](lis-transport-closure.json) binds the report,
source hashes, REA observations, test counts and exact import delta. Probes,
full case results and the neutral REA snapshot remain under ignored
`build/goal-r1-lis-closure/`.
