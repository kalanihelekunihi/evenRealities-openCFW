# R1 application reset entry in C

`r1/src/application/runtime/reset.c` supplies the missing `Reset_Handler`.
Stock reset at `0x27488` calls Nordic `SystemInit`, then branches to the
scatter-loader entry at `0x27200`. The C entry calls the existing source
`SystemInit` and `r1_native_scatterload` in that order. An ignored host fixture
at `build/r1-current-20261110/application_reset_test.c` checks the handoff
under AddressSanitizer and UndefinedBehaviorSanitizer.

The 951-unit R1 source build at `build/r1-reset-c-20261110/report.json`
compiles and composes both payloads without failures or duplicate strong
symbols. The strict application link now finds `Reset_Handler`, then reports
55 unresolved references and 211,104 bytes of FLASH overflow. Four additional
CmBacktrace linker symbols became reachable through reset. The earlier
51-reference/189,584-byte diagnostic lacked an entry point and therefore
understated the reachable image.

The later [application vector review](application-vector-c-review.md) records
the full 128-word C table and CmBacktrace linker-boundary aliases. The source
scatter table still names stock flash/RAM addresses and is not a complete
final-layout initializer. Unresolved providers, code size and physical boot
remain open.

## Source-layout reset, 2026-11-10

The reset entry now initializes the relinked image from linker bounds. After
`SystemInit`, it copies initialized RAM bytes from `__etext` through
`__r1_data_init_end__`, zeroes `__bss_start__` through `__bss_end__`, then calls
the C application runtime entry. It no longer calls the old scatter dispatcher
whose table refers to absolute stock flash addresses. The existing scatter
decoder and table remain source units for reconstruction review; they are not
the source-built reset path.

The linker defines the data-copy endpoint after the dynamic log registry and
asserts that the FDS and log registry load addresses follow their RAM offsets
from `__data_start__`. In the direct-link map, `.data` starts at `0x200064a8`
with flash load `0x106b58`; `.fs_data` starts at `0x2002d090` with flash load
`0x12d740`; `.log_dynamic_data` ends at `0x2002d12c`, before `.bss` at
`0x2002d130`. Both placement assertions pass. The reset object imports the
expected linker bounds and runtime entry, with no scatter-dispatch import.

The 952-unit build at `build/r1-source-reset-c-20261110/report.json` passes
with no compile failures or duplicate strong symbols. The bootloader strict
link passes. The application strict link still fails with 50 unresolved
functions. At that checkpoint ld reported 219,992 bytes of output-section
overflow; the full initialized flash load image exceeded the configured span
by 378,848 bytes. The later size-focused vendor build reduces full overflow
to 179,536 bytes. No board execution is claimed;
see the [direct-link review](application-source-link-review.md).

The later BSS cleanup moves uninitialized heap, worker stacks, model pool and
scratch storage out of the flash load image. In the current direct-link map,
the copy endpoint and BSS start are both `0x20009af8`; BSS is `0x28aa0` bytes
and ends below the stack limit. The linker data-placement assertions pass.
