# R1 GoMore sleep-stage refinement in C, 2026-11-10

The locked R1 application has a sleep-stage refiner at `0x81040`. The native
entry in `r1/src/application/runtime/native_gomore_sleep_stage_refine.c`
passes its three configuration words, mutable stage array, interval duration,
and count to the consolidated GoMore C primitive. No stock executable bytes
are retained in this implementation.

The initial primitive differed from the stock function. Paired Cortex-M4
execution localized the first difference to the final deep-stage cap. The
stock loop subtracts 0.5 minutes from the deep count for each rewrite, but
does not add that time to the light count. It then recomputes statistics before
the REM-stage cap, which also subtracts without adding to light. The native
calculation truncates the target stage count before subtracting the observed
count. The C primitive now follows those operations. The proportion-adjust
primitive also processes its first run for positive adjustments of 7 or more,
then stops subsequent runs when 12 or fewer stages remain; the earlier C
boundary differed.

The ignored ARM replay is under `build/r1-sleep-stage-refine-adapter-20261110/`.
It executes the locked stock function and the actual manifest Clang objects
for the native adapter and revised primitive, comparing the full stage array
and count. The initial 54 cases and expanded 312 cases all match across six
recovered configuration records,
several stage counts, patterned stages, and seeded random stages. The replay
also compares the shared proportion-adjust primitive directly over 896
target/run/adjustment cases using its manifest Clang object; all match the
stock function at `0x64cc8` in return value and the full stage buffer. These
cases include the 12-stage positive boundary and both target stages. The replay
does not establish all input behavior, firmware byte identity, or board
operation. `build/sources-r1-sleep-stage-refine-c-20261110/report.json` records
976 compiled R1 units with no duplicate strong symbols. Its strict application
link has 23 unresolved functions and uses 605,192 of 696,320 flash bytes; its
strict bootloader link passes. The full application remains unlinked.
