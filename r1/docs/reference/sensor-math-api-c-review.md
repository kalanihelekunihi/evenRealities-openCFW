# C math entry points for sensor consumers

`runtime/sensor_math_api.c` provides the public hard-float C names atan,
sqrt, sqrtf, floorf, fmaxf, expf and tanhf by delegating to the existing
canonical recovered algorithms. The normal source composition closes these
seven imports without changing their consumers or copying an algorithm.
This preserves recovered behavior, including exceptional encodings and native
errno, rather than claiming generic libm conformance.

A probe links all seven roots directly from the normal application composition
with no unresolved references or modeled providers. A second probe links the
normal participating objects and executes the normal Goodix motion object.
Only the quantized runtime is recompiled from unchanged source with function
and data sections added: its normal monolithic object pulls in unrelated,
unfinished algorithms. That isolated fixture does not prove a full normal
quantized-runtime/application link.

The adapters and canonical providers produce identical returned bits, errno
and FPSCR in 8248 paired comparisons across four selected FP profiles (default,
round-up, flush-to-zero and default-NaN). These are selected profiles, not the
full FPSCR space. Core/VFP saved registers, SP and interrupt masks are checked.
No stock instructions are mapped and no math/provider stubs are used.

The actual normal Goodix object executes 420 samples covering stationary
orientations, first-frame and growing-window behavior and rolling beyond its
125-sample window, with expected directional flags. The isolated quantized
consumer executes four zero-point cases and 24 range-adjustment cases through
fmaxf/floorf. All seven APIs execute, but full recurrent/model inference and
physical sensor input are not claimed. The adapter comparisons establish
canonical equivalence and ABI wiring; they do not independently re-prove the
underlying math algorithms or an accuracy bound.

The companion JSON records the final verification, seven compiled wrong-
adapter defect controls, object audit, build hashes and a fresh REA sqrtf
byte match. Existing provider and consumer object hashes remain unchanged;
the two generated bootloader objects retain identical allocated bytes and
relocations despite metadata changes. No source-plan qualification is added.

R1 now compiles 785 units (703 application, 82 bootloader) without failures
or duplicate strong symbols. Application imports fall from 114 to 107;
bootloader metadata imports remain 22 and strict source bootloader linking
succeeds. The global source check retains the unrelated unlisted G2
resident_rom_thumb_set.S failure. The application remains incompletely linked
and physical sensor/model behavior remains unverified. Probe linker warnings
about mixed enum-size attributes remain; these adapters use no enum arguments.
