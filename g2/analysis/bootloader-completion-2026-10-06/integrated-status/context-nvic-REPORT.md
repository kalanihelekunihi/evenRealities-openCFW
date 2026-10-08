# NVIC provider0x430470

Locked bootloader SHA256 f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5, load0x410000. Function interval0x430470..0x43048e is30 bytes. The LDR at0x430480 reads literal0x43063c =0xe000e100.

Reconstructed C: `g2/components/bootloader/initializer_callbacks/context_nvic.c`. Platform finish calls it with10. For low16 bits0..32767, issue one32-bit volatile store to0xe000e100+4*(low16>>5) with value1<<(argument&31); otherwise no store. High16 bits have no effect. There is no read/modify/write, interrupt-count validation, barrier or status return. Source preserves the issued-write semantics; adding a range guard would be a behavior change.

Integration removes the whole NVIC cut only when the native export is present and records actual ordered register writes. The direct comparator tests all65536 low-halfwords with three high-halfword patterns. RAM-backed MMIO compares issued writes, not actual NVIC W1S register effects or IRQ delivery. Large positive halfwords address unrelated or unimplemented registers; they do not represent valid supported hardware IRQs.

All seven fresh19ff0c cases PASS (normal2/malformed3/interruption2), both stop/reboot observables and persistence match, and both reboot sides reach the fixture application reset entry without exception.573 frozen files/142 objects remain unchanged. Native provider closes only the NVIC wrapper; semaphore creation416762, descriptor registration430280, ADC/service children and asynchronous IOM publication/service remain open. No hardware execution, flash or compiler authentication occurs.
