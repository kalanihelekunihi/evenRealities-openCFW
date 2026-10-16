# Formatted output with RTT

`build_native_formatter_stdio.py` links `printf`, `sprintf`, `snprintf` and
`vsnprintf`, their source parser/arithmetic/output helpers, and the native RTT
write wrapper over pinned SEGGER RTT 6.18a source and source memory providers.
The combined object has no undefined symbols. This is four formatted-output
entrypoints, not all standard I/O APIs or a complete firmware image.

The unbounded/stdout layer passes 4,212 direct cases, including 343 matching
faults and 3,978 backend observations per side. The 10-byte compiled C buffer-putc
section matches the native instruction bytes and has no code relocations;
image placement and complete instruction identity remain unproven. The RTT
write wrapper passes 3,538 cases, covering native initialization, actual pinned
ring writing, all BASEPRI byte values and emulated CONTROL states.

The 972-case end-to-end printf test executes this combined object and actual
source RTT operations, with 9,900 ring writes per side and no backend fixture.
Return count, output buffers/control block, BASEPRI and callee-saved state
match. Printf r1 differs in 108 cases; other caller-saved/private-frame details
remain gated. Live debugger drain, blocking without free space, physical
privilege/interrupt timing, all remaining firmware components and byte/image
identity remain separate requirements.
