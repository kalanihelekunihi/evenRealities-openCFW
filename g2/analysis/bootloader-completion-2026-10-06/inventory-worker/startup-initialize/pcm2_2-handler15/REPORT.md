# PCM2.2 selector 15 transition handler

This isolated source reconstruction covers the installed SPOT selector-15
Thumb target `0x429525` (function entry `0x429524`) in locked image
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
The authenticated function extent is `[0x429524, 0x429624)`, 256 bytes, with
SHA-256 `b9c0d1de31402701d130b56442cb955fe92c59ce4973cfc4a79652df8a6e23be`.
`verify.py` checks the exact Ghidra body extent and hash plus one-byte-short
and one-byte-long negative controls. `handler15.disasm` is the disassembly of
the authenticated body.

`handler15.c` implements the r0-r3 transition ABI and the stock's two-register
return: the four unpacked low-voltage trim bytes overwrite the saved r2/r3
stack words, so r0 is the packed trim-byte word and r1 preserves the original
fourth argument. It reads target/current profile words, uses the locked
bit-0 timer-enable and bit-30 ready tests, invokes the real timer service when
enabled, then applies the cached profile and VDDF/VDDFL/core fields in stock
order. The pinned public PCM2.2 source remains a semantic reference; fixed
addresses, masks, register writes, and the return contract come from the
locked instructions.

`comparison-final-base.json` passes all 14 direct original-instruction versus
compiled-source fixtures: eight timer-disabled cases with nonuniform profile
words and varied state indices, and six timer-enabled cases covering ongoing
states 2, 7, and 26 with ready and not-ready status. The comparisons include
both return registers, selected SRAM/MMIO state, ordered writes, wait-cycle
calls, callee-saved registers, SP, and PRIMASK. All 256 stock instruction
bytes were visited. The source machine executes the source-only handler addon
and real source segments from the frozen `final-candidate.elf`; execution into
the locked-image address range traps. The only controlled timing edge is the
firmware's ROM cycle-wait service at `0x40`; the actual stock handler and
linked source delay, timer, clock, and service routines execute. This is
offline emulator evidence, not physical hardware behavior or whole-firmware
source completeness/equivalence.

Rebuild the addon and run `make verify`. `BASE_ELF` defaults to
`/tmp/opencfw-root-pcm22/final-candidate.elf`; override it to test a different
base candidate. The addon linker uses that ELF's symbols only and emits only
this handler's source code, keeping the frozen base object unchanged.
