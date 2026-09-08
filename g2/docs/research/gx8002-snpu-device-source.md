# GX8002 SNPU hardware shim recovery

The complete 76-byte `.sram_text` section of the pinned NationalChip
`drivers_lib/snpu/grus/snpu_hw.o` matches stock at package offset 0xeb34,
except its one authenticated branch relocation. The decoded stock branch
resolves to the already recovered `gx_request_irq` at 0x1002553c. Matching
the whole section, including adjacent register primitives, establishes more
context than searching for isolated return instructions.

The SDK commit is 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. Object bytes
are comparison evidence only; emitted instructions come from compiling
`runtime_gx8002_snpu_device.c` with the native macOS C-SKY compiler.
The authenticated public `include/driver/gx_irq.h` defines the IRQ callback
as `int (*)(int, void *)` and the request helper's void return.

| Routine | Package offset | C bytes | Envelope |
| --- | --- | ---: | ---: |
| snpu_device_init | 0xeb34 | 2 | 4 |
| snpu_device_exit | 0xeb38 | 2 | 4 |
| snpu_request_irq | 0xeb3c | 14 | 16 |

Init and exit are empty returns in the original. Their C definitions preserve
that authenticated behavior; they do not stand in for unresolved work.
The forwarding routine takes a handler and opaque data pointer, then calls
`gx_request_irq(12, handler, data)`. The private wrapper signature is inferred
from observed argument forwarding; the callback/helper types are grounded in
the public header. Original observable registers are preserved for the empty
hooks. The request wrapper's four-byte frame and callee-saved registers are
checked under conservative helper clobbers.

Qualification covers 11,664 stock/source cases and eight tests, including
wrong IRQ numbers, swapped data, wrong helper targets, incorrect return frame,
and a state-changing mutation of an empty hook. Arbitrary pointer encodings
only test forwarding; they are not declared valid handler addresses. Callback
registration behavior belongs to the separately qualified IRQ helper.

The three functions are qualified and registered in the integrated build. Reviewed evidence is `gx8002-snpu-device-verification.json`. Physical
hardware timing and the complete SNPU driver remain unqualified.

Caller recovery established that device_init receives the register base in
r0. Its C signature now accepts an ignored void pointer. Requalification
passes the same 11,664 cases and eight tests, with unchanged target bytes.
