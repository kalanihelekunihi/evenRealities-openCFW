# GX8002 internal SNPU resume recovery

Stock package 0xef28 / runtime 0x1020599c matches the role of the pinned SDK
`snpu.o` local `resume` routine. The reconstructed C compiles to the same
76-byte payload, including the literal pool. Qualification additionally
checks its decoded state/call behavior and eight-byte frame.

It clears state offsets 0, 0x5c0 and 0x5d0, then enables the SNPU clock.
It reads the register pointer at state+0x5c4 and queries whether the NPU is
enabled. A nonzero result leads to disable and an unbounded idle poll; every
helper call reloads the live pointer. It then resets using the DIFFERENT
pointer at state+0x5c8, initializes registers and returns zero. State changes
made by helpers are not overwritten by a final state assignment.

The offset-only external struct documents only observed fields. Its opaque
gaps are not claimed as understood or source-owned data. Helper implementations
are separately recovered; this model does not establish hardware timing.
Null and other synthetic pointer encodings test forwarding only.

Qualification covers 3,024 completed traces, 54 noncompletion prefixes, and
ten tests. Models exercise helper mutations of the state fields and both
pointers, full-width nonzero helper results, idle delays through 63, and
never-ready prefixes through 32 polls. Mutations detect wrong reset pointer,
stale poll pointer, wrong clock argument and incorrect return frame.

Files use `snpu_resume_internal` / `snpu-resume-internal`. Reviewed report:
`gx8002-snpu-resume-internal-verification.json`; admission artifact:
`snpu-resume-internal.elf`. The routine is qualified and registered; all 480 integration tests pass.

Further caller evidence: gx_snpu_init starts at package 0xf280 (not 0xf28c),
with a 64-byte instruction body and 12 bytes of local literals through 0xf2cc.
It places 0xa0c00000 in r0 before calling snpu_device_init. The recovered empty hook now accepts an ignored register-base pointer. The original empty hook still leaves r0 unchanged.
The caller writes register pointers at state offsets 0x5c4, 0x5c8, 0x5cc,
clears 0x5b4 and 0x5b0, calls task-control initialization at package0xee60,
registers ISR0x10205ce0 with null private data, stores state2 and returns0.
These caller observations are leads, not yet qualified source.
