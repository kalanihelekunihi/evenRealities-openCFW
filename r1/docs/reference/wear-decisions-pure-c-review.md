# Pure C wear-on and wear-off decisions

The [machine-readable receipt](wear-decisions-pure-c-review.json) pins the stock REA bytes, source changes, compiler route, normal build and fixtures. The two wear-decision units now contain no inline assembly. This supersedes the explicit signaling-compare and conversion boundaries retained in their original admissions.

The existing license-free GCC9 FP profile emits native signaling `VCMPE` from ordinary C `value > 2000.0f` and `value < 40.0f`. Signaling, rounding and trapping flags are enabled, contraction and if-conversion are disabled, and small noinline comparison helpers keep the operations observable. This preserves invalid-operation flags for quiet/signaling NaNs, input-denormal flags under FZ, comparison condition bits and preset FPSCR flags. No manual FPSCR model or write intrinsic is introduced.

Wear-off calls the existing C `r1_native_float_to_signed32` provider for the native truncation result and FPSCR effects. There is no second conversion implementation. The call remains before logging decisions and executes even when logging is disabled, including when an unregister provider has changed the mean to a NaN. Optical thresholds, wrapping counters, live state/log reads, release timing and mode transitions retain their existing contracts.

Verification passes 7,011 full wear-on and 7,503 full wear-off stock/C comparisons. The existing C range provider executes, while clock/stream/log boundaries are modeled. Public state and write widths/order/values, provider arguments and snapshots, logical invalid accesses and complete FPSCR match. All 774 native decision instruction bytes execute.

Another 1,688 comparisons execute actual C motion coordination, statistics, both decisions, range and conversion. Added quiet-motion packets cover signed and fractional means, sleep/handle conditions and FP modes; an entry counter confirms the conversion helper executes on those paths. Clear, multicast, clock, stream registration/release and logging remain modeled. Modeled ports return through real BX LR stubs. Source execution cannot enter stock code.

The focused matrix passes 131,712 native-VCMPE/C-helper comparisons: 2,058 binary32 patterns across 32 FPSCR configurations for both thresholds. It executes the actual compiled helper bodies, comparing their boolean result to an independent native NZCV predicate and comparing the complete FPSCR. Fourteen compiled defects are rejected, including quiet comparison, inclusive thresholds, stale history, omitted/unsigned conversion, early release clear and lost byte wrapping.

Cortex-M4 is selected explicitly. The FP context is primed before assigning FPSCR; cold-FPU/task-context behavior, physical execution and concurrency remain unverified. Preserved integer/FP registers, SP, masks and caller guards are checked on normal returns. Caller scratch, APSR, void return values, fault PC and private frames are excluded.

The fresh serial R1 build compiles all 877 units (795 application,82 bootloader), with no duplicate strong symbols and unchanged 61/22 imports. Both tested objects equal the normal objects. The other 865 nongenerated objects, including the range, statistics and conversion providers, remain identical. Two existing generated objects differ with build directory paths. Only the two compiler/profile selections change in the manifest; writable sections/initializers, source plan and existing cache linker layout remain unchanged. No RAM ownership is added.

Remaining hardware dependencies, sensor delivery, final executable linking/startup and boot remain open. Relocatable composition is not bootable firmware; byte identity is not required or claimed here.
