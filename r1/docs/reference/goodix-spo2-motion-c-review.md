# Motion accumulation and optical/motion dispatch in C

`native_spo2_motion_accumulate.c` recovers the318-byte motion stage and54-byte signed16 window. It preserves wrapped integer squares, live input/baseline reloads, native encoded math, signed saturation/status and window averaging. No writable owner or inline assembly is added; the existing errno cell is reused.

**63,648 native/C function-call comparisons pass:**27,904 expanded motion cases,33,504 direct/window/alias cases,160 independent finite geometry/control oracle cases and2,080 calls in eight actual-constructor optical+motion sessions. A further9,408 isolated signed-conversion instruction pairs agree with an independent integer oracle; those snippet cases make no ABI claim.

All372 new native instruction bytes execute. Root sessions also cover all1,068 existing rolling/optical/root bytes. Math, memory and algorithm functions execute as actual C/native code; only constructor allocation is modeled. Tests compare full public RAM, active FPSCR, saved registers, stack and masks. Twelve compiled defects are rejected. Nonzero histories expose missing-copy samples; an unobservable overwritten over-copy control was replaced and preserved as a test correction.

All908 R1 units compile and compose without failures or duplicate strong symbols. All897 prior nongenerated objects are unchanged. Of their sources,896 remain unchanged; the one API-only signature correction matches the existing caller and produces its previous object exactly. The new tested motion object equals normal build. Imports fall88 to87 application; boot stays22. Source-plan and cache-layout files remain unchanged.

Default nontrapping division, positive mapped capacities and selected aliases form the tested contract. Arbitrary faults/private aliases, actual allocator lifecycle, cold FPU, interrupts/concurrency, stack budget/throughput, physical sensors and final startup/layout remain unverified. Ten later processing boundaries remain unfinished. Relocatable composition is not bootable firmware.

[Machine-readable evidence](goodix-spo2-motion-c-review.json) records contracts, profiles and hashes.
