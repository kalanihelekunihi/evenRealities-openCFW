# GX8002 SNPU ISR boundary recovery

Stock package0xf26c / runtime0x10205ce0 reads the state word at0x20027350.
If it is2, it returns with r0=2. Otherwise it calls process_status at
runtime0x10205bd8 (package0xf164), preserving that helper's observed r0.
The pinned SDK snpu.o names the local snpu_isr and snpu_process_status.

C uses the public IRQ callback shape, ignoring IRQ/private arguments and
explicitly retaining observed return behavior. This does not assert knowledge
of the original private return type. The unqualified process_status helper
remains a separately tracked dependency, not a claimed recovery.

GCC's default shrink wrapping produced24 bytes with a branch-specific stack
frame. The native build uses -fno-shrink-wrap, yielding the original20 bytes
with a four-byte frame on both paths. Qualification checks 14,700 combinations
of state, helper results and caller-register seeds plus six mutation tests.
It covers one state read, exact gate, helper target, return register and ABI.
Physical interrupt timing remains unqualified.

The ISR is qualified and registered. Files use snpu_isr / snpu-isr;
reviewed report gx8002-snpu-isr-verification.json; artifact snpu-isr.elf.

Integrated macOS candidate passes all 494 tests. Remaining helper recovery
is tracked separately; this does not establish complete source-only firmware.
