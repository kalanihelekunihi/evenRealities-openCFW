# R1 DFU backend C frames, 2026-11-10

`r1/src/application/runtime/native_dfu_backend.c` now implements the
system-event and control-point entry frames in C. The selected Clang profile
saves two registers and allocates eight words for the system-event frame,
placing it at entry SP-40, as in the stock four-register save plus six-word
allocation. It saves two registers and allocates ten words for the
control-point frame, placing it at entry SP-48, as in the stock six-register
save plus six-word allocation. The wrappers retain ordinary C calls to the
existing `sys_kernel` and `control_kernel`. The compiled entry instructions
are different from stock; byte identity is not claimed.

The ignored probes under `build/r1-dfu-control-sys-probe-20261110/` compare
stock and source-linked backend behavior in 72 seeded sequences. They cover
event callback results 0, 8 and 9; SVC 174 results 0 and 17; busy state;
interrupt masks; three stack seed patterns; response payload bytes; frame,
length and data pointer aliases; backend event order; returns; and state.
The existing state-owner replay also passes 1,728 sequences against the C
backend. The authorization replay under
`build/r1-dfu-control-frame-probe-20261110/` passes 6,746 core stock/C cases
and 1,472 integrated control-dispatch cases with the control-point wrapper in
place. Service effects, callbacks and shutdown remain modeled; physical DFU
operation is unverified. The response entry in this backend still contains a
handwritten assembly frame.

The current source build compiles all 959 R1 units without failures or
duplicate strong symbols. The strict bootloader link passes; the application
still has 43 undefined references and a 28,240-byte full flash load overflow.
