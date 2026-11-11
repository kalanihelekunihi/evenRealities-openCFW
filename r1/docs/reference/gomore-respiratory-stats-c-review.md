# R1 respiratory statistics in C

`native_gomore_respiratory_stats.c` supplies encoded counting `0x967a0`, descending
argmax `0x760ec` and thresholded mean `0x76120`, declared in its shared header.
The [receipt](gomore-respiratory-stats-c-review.json) binds production source/object,
REA bytes, replay, defect controls, checked-wrapper comparisons, consolidation,
qualification and composition. No assembly or persistent RAM is added.

Encoded counting retains the wrapped inclusive raw-word interval and signed loop
bound. Argmax scans backwards from length-1 with positive-zero maximum and strict
signaling comparisons. Mean writes zero before reading comparisons, reads live
weights/samples, preserves addition operand order and divides even for zero
included count. Native pointers use pointer-width integer addressing; on the
firmware target the ABI remains three integer pointers plus threshold in S0.

The old generic exports become explicitly named checked wrappers and delegate to
these native implementations. Count processes positive signed-sized chunks to
retain its size_t API; argmax retains null/zero/oversized guards. Mean uses a
temporary result and publishes only after processing, retaining the old generic
utility's alias behavior while the native API retains immediate writes.
**15,168 finite/null/length/alias host comparisons** against exact prior function
bodies pass. Huge host counts and nonfinite utility FP flags are not covered.

The production object passes **3,583 direct native/C cases**, including NaNs,
infinities, signed zero/subnormal values, FP modes and output aliases. Memory,
raw return, FPSCR, SP and saved integer/high-FP registers agree. Independent
expectations cover 768 encoded-count/argmax returns and fifteen finite mean alias
cases. **102 boundary cases**, including 76 faults, match invalid access address/size,
partial writes, memory, return and FPSCR. Seven defects compiled from the production
source are rejected. Some emitted sections differ from the earlier raw-word
prototype after pointer interfaces are introduced; production replay, rather than
assumed object equality, supplies the behavior evidence.

The actual native respiratory routine passes **840 paired executions** with these
three C substitutions. Encoded count is reached 840 times; argmax and mean 560
times each. Record/output, return, estimator arguments, helper sequence, FPSCR,
SP and preserved registers agree. Optical estimation is modeled; native math,
history and clearing execute. This does not establish a fully C respiratory root
or estimator, whole-source execution or physical device behavior.

The normal build compiles **687 units** (613 application, 74 bootloader), with
**179 application and 34 bootloader imports**, unchanged. All **685 preceding
units outside the consolidated generic owner** retain identical source/object
hashes. Source checks and relocatable composition pass without new failures or
duplicate strong symbols. Full respiratory update remains unresolved.

Qualification selects no new replacement and the canonical source plan remains
unchanged. Hybrid raw equality still uses executable stock pull-through. Physical
execution, concurrency/private stack behavior, final source-only linking and
byte identity remain unproven. Reproduction artifacts are under
`build/goal-r1-gomore-respiratory-stats-c/`; the normal report is
`build/sources-goal-r1-gomore-respiratory-stats-c/report.json`.
