# Optical accumulation and root dispatch in C

`native_spo2_optical_accumulate.c` recovers the354-byte optical accumulator,104-byte decimated signed16 window and68-byte accumulation wrapper. It executes the recovered rolling features, preserves native float-bit ratio gates and uses defined unsigned float conversion/status semantics. No writable owner or inline assembly is added.

**15,176 native/C function-call pairs pass:**11,136 direct cases,320 independent finite Fraction ratio-oracle cases,520 calls in two actual-constructor optical sessions and3,200 calls in20 root sessions. Root tests include raw-sequence aliases and motion-boundary mutation. A further9,408 isolated conversion-instruction pairs agree with an independent integer oracle; those snippet cases make no ABI claim.

All526 new native instruction bytes execute. Root sessions also cover all542 shared rolling-feature bytes. Constructors, rolling features, filters, windows and memory helpers execute as real C/native code. Allocation is modeled; root motion processing remains modeled. Public RAM, full active FPSCR, saved registers, stack and masks match. Twelve compiled defects are rejected.

A noinline ordinary C divide helper keeps division conditional. The initial inline expression caused speculative VDIV and changed DZC where stock skips division; the test rejects that version. Compiler/profile changes require rechecking branch and FP operand ordering.

All907 R1 units compile and compose without failures or duplicate strong symbols. The tested object equals normal build;896 prior nongenerated source/object pairs are unchanged. The accumulation import becomes explicit `r1_goodix_spo2_motion_accumulate`; totals stay88 application/22 bootloader. Source-plan and cache-layout files remain unchanged.

Default nontrapping division, positive mapped capacities and selected aliases are the tested contract. Arbitrary faults/private aliases, real allocator lifecycle, cold FPU, interrupts/concurrency, throughput, physical sensors and final startup/layout remain unverified. Eleven processing boundaries, including motion, remain unfinished. Relocatable composition is not bootable firmware.

[Machine-readable evidence](goodix-spo2-optical-c-review.json) records contracts and hashes.
