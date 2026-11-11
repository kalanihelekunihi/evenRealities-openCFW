# R1 GoMore activity-window stage in C

`r1/src/application/runtime/native_gomore_activity_window_adapter.c` supplies
stock application `0x6138c` through the source-owned activity-window state,
conditioning, classification, and peak-statistics functions. The hard-float
call boundary passes quality in S0 and the state, axis record, sample record,
and output pointers in R0-R3. The adapter preserves the packed sample-count
and channel fields, the three axis pointers, and the alternate-conditioning
flag. It returns the stock zero status.

The paired replay found an existing owner defect: stock `0x9403e` compares the
encoded positive variability against `200.0f`, while the C owner truncated
it to an integer first. The canonical `gomore_primitives_activity_score_variability_adjust`
now uses the raw signed float-word comparison. Seed 1778, with round-up mode,
exposed a score difference of approximately 0.1 before the correction.

The ignored probe in `build/r1-activity-window-adapter-20261110/` links the
candidate adapter and current vendor object against the SHA-pinned official
`r1-2.2.6.0009` image. It binds only the stock lower `sqrtf`, `powf`, and Arm
EABI math helpers for this diagnostic ELF. **2,048 paired cases pass**, varying
all seven state values, scores, input quality, alternate conditioning, sample
counts around the 23-27 acceptance window, accumulated samples, threshold
counters, rounding modes, FP control and sticky bits. They compare return,
all 1,028 state bytes, two output bytes, FPSCR, saved core and high-FP
registers, SP, BASEPRI, and PRIMASK. The cases visit 269 stock instruction
starts, including both positive and negative state transitions. This is
replay evidence, not a proof for every 32-bit input or physical-device timing.
The diagnostic ELF permits unresolved code outside the exercised closure;
the production application link remains strict and reports its own imports.

The production adapter and probe objects have identical allocated section
bytes and relocations; the production vendor object is byte-identical to the
probe vendor object. The R1-only source build compiles **975 units in 762
files**, with 893/893 application and 82/82 bootloader units, no failures or
duplicate strong symbols. Strict bootloader link and vector verification pass.
The strict application link drops from 25 to **24 undefined functions**;
the full flash load exceeds the configured span by **29,224 bytes**, 128 more
than the preceding checkpoint. No stock executable region is linked, and
byte identity or hardware behavior is not claimed.
