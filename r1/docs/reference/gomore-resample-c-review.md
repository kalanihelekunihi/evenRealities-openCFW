# R1 ACC and PPG resampling adapters in C

`native_gomore_resample.c` implements ACC `0x60990` and PPG `0x60a14`.
The [receipt](gomore-resample-c-review.json) binds the normal source object,
REA evidence, replay, defect controls, qualification and composition checks.
The [investigation](gomore-resample-c-investigation.md) records the FP mismatches
found before promotion. No inline assembly or persistent RAM owner is added.

ACC retains the three ordered 100-byte clears, live destination/source pointer
loads, three axis kernel calls, status/flag publication and final log. PPG retains
the signed channel conversion, early reciprocal computation, at-most-one kernel,
25 ordered accumulations and 25 scaling operations with live output pointers.
Both discard lower return values. Count-zero behavior remains distinct from
negative signed channel words passed directly to PPG.

The strict GCC profile uses a volatile reciprocal and a non-inlined C addition
helper. These preserve FPSCR visibility at kernel entry and native NaN operand
selection. The compiled helper contains `vadd.f32 s0,s0,s1; bx lr`; no opcode
array or executable data supplies it. An explicit 112-byte C frame plus 32 saved
register bytes puts PPG scratch at entry SP minus 140, matching stock. Numeric
scratch addresses are compared without normalization. ACC saves 24 bytes versus
stock's 32; provider entry SP equality is not claimed.

The production object passes **1,072 direct native/C cases**, including **60 fault
pairs**, preserved integer/high-FP register checks, rounding/NaN modes and aliased
provider mutations. Thirty cases additionally check independent expected status,
kernel arguments/count and finite PPG output. Nine compiled defective controls
are rejected. The direct fault comparisons remain emulator observations, not
physical alignment/trap proof.

Actual native/C host adapters and resamplers pass **442 integration cases** with
**2,700 modeled kernel/logger/algorithm calls**. The stock memory-clear function
executes on both paths. This fixture compares the host's 420-byte scratch view,
context and packet effects, exact PPG scratch pointers, kernel arguments, FP
flags, preserved registers and return. The outer sensor-update caller is outside
this fixture; its previously observed eight-byte frame difference remains open.

The normal build compiles **680 units** (606 application, 74 bootloader), with
**167 application and 34 bootloader unresolved imports**. All 679 preceding
source/object pairs are unchanged. The two adapter imports are resolved and two
lower imports are exposed: ACC kernel `0x8245c` and PPG kernel `0x8247e`.
The logger and final algorithm remain existing unresolved providers.
Source checks pass, with no composition failures or duplicate strong symbols.

Qualification selects no new source replacement. The canonical source plan is
unchanged. Hybrid raw equality still includes 641,791 bytes of executable stock
pull-through; it does not prove fully C firmware, a complete source-only link,
physical device behavior or byte-identical source reconstruction.

Reproduction scripts and snapshots are under `build/goal-r1-gomore-resample-c/`;
the production report is `build/sources-goal-r1-gomore-resample-c/report.json`.

The subsequent [kernel-wrapper review](gomore-kernels-c-review.md) supplies both
wrappers in C and replays the host/resampler chain. Interpolation and filtering
remain modeled there; whole-chain stack equality remains open.
