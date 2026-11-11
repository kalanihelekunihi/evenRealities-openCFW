# NADT initialization in C

The [soft-ADT execution review](goodix-soft-adt-execute-c-review.md) adds the C sensor adapter and shared green/IR event reporters, reusing the existing selector, timeout counter and capacitor flag. Timeout advancement on core errors is preserved; the `goodix_nadt_calc` computation core remains unfinished.

The native constructor and its separate configuration tail now use C. The existing state and workspace share one reset implementation; a 120-byte configuration owner represents the native configuration RAM.

- Stock ranges: 0x6e664–0x6e75d (250 bytes) and0x73e2c–0x73ff9 (462 bytes). The earlier 712-byte inventory entry combined both.
- 3072 configuration comparisons cover all rounding modes, signed extremes, negative unsigned saturation/IOC and aliases.
- 512 constructor/deinit comparisons check guards, full nonstack RAM, allocation/free boundary snapshots and FPSCR.
- 512 actual C/native allocator lifecycles call no function ports and recover all free capacity after deinit.
- Nine compiled defects are rejected. Tested constructor/reset objects equal normal build objects.
- R1 source check and 893-unit composition pass; 881 prior nongenerated source/object pairs are unchanged. Application imports drop 75 to 74; boot imports remain 22.

Invalid rate/mode values return 3 after allocation/reset, preserving native defaults and ownership. No allocation-null or existing-owner guard is invented. Scaling and exception flags use C without inline assembly; padding and input reloads remain visible.

This is relocatable composition, not a bootable firmware image. Final executable startup/linking, physical hardware/FPU behavior and remaining sensor calculations are unverified. Byte identity and a paid compiler are not completion requirements.

See [the machine-readable receipt](goodix-nadt-initialize-c-review.json) for pinned evidence, exact contracts and limitations.
