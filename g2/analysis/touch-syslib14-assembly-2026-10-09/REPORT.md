# Authentic SysLib assembly emission

The three absent C-object sections are implemented in the authenticated public
PDL's `COMPONENT_CM0P/TOOLCHAIN_GCC_ARM/cy_syslib_gcc.S`, unchanged and Apache-2.0.
GNU14.2.1 emits exactly the stock 32-byte contiguous text region:

- `Cy_SysLib_DelayCycles` `0x4480`, 18 bytes.
- `Cy_SysLib_EnterCriticalSection` `0x4492`, 8 bytes.
- `Cy_SysLib_ExitCriticalSection` `0x449A`, 6 bytes.

All comparisons pass without relocations, wrappers or forced stubs. Symbol
sizes are absent; the extents come from the predeclared historical rows and
source labels, whose offsets exactly match 0/18/26. Hashes, actual emitted
bytes, source path and compiler invocation are in `results.json`.

Delay adds 2 with uint32 wrap, shifts right by 2, skips the loop if zero,
otherwise repeatedly increments then subtracts 2 until zero, executes the
source NOP padding and returns. This is the genuine source instruction
sequence, not a wall-clock timing validation. Enter reads PRIMASK, disables
interrupts and returns the saved value; Exit restores PRIMASK from its argument.
These are three new selected candidates/32 bytes awaiting independent review.
No unique toolchain/source producer, live interrupt timing or whole-image
completion is established.
