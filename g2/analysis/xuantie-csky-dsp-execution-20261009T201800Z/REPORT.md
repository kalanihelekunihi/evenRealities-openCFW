# CK804EF DSP execution: finite passes and localized inverse-split difference

**Official pinned XuanTie QEMU builds and executes standalone CK804EF DSP code.** Seven arithmetic/lane/saturation baseline probes, guarded copy/loop/shift/fill/zero complex+real FFT smoke paths,230 C-versus-assembly helper cases,3 bitreversal comparisons and a separate55-case abs-max assembly oracle pass. The289-case corpus stops after256 passes at its first numerical difference: inverse real FFT512 constant32767, output index1, C-20868 versus assembly-20866.23 FFT cases passed;32 FFT cases remain unexecuted after that stop. Case counts are not instruction/path coverage or whole-firmware admission.

## What is newly understood

The first discrepancy is already present in inverse real split, before complex inverse/doubling. An explicit DC/Nyquist-imaginary-zero, conjugate-mirrored spectrum reproduces it, correcting the unconstrained original fixture endpoint shape. A bounded seven-step input-prefix reduction512..8 retains a diagnostic difference; the prefix fixture is a kernel diagnostic, not an assertion of physical received spectra.

The first valid-spectrum split imaginary lane is C0 versus assembly1. Authentic assembly uses `pneg.s16.s` on a32-bit cross-product while authentic C uses scalar32-bit negation. Directed probe: product1fffc000 -> packed-neg e0014000, scalar-neg e0004000; adding the next product yields10000 versus0. See inverse-split-pseudocode.md and pneg-execution.json. This supplies a concrete reason to retain licensed exact-reproduced assembly for bit-stable DSP rebuilding; a compilable C alternative is not automatically a bit-identical numerical replacement. No firmware/app patch is proposed from these model results alone.

## Simulator and harness provenance

Source is registered XuanTie QEMU pin3287d345c7f5d60d5c8774d90752f5f710744f85. Native arm64 official Ubuntu container build uses two jobs, cskyv2-softmmu only and official package sources plus exact QEMU wrap pins. It reports8.2.94 despite the named9.0 branch. Binary hash/path, complete build logs, dependency versions and wrap revisions are retained; the53MiB binary is in ignored build scratch rather than this knowledge packet.

Initial shared-filesystem tar symlinks failed; the receipt remains. Registered source was then mounted read-only and copied only inside container scratch for pinned subproject resolution. No registered source/index change was made. The first UART-reporting run crashed in QEMU at the first write; source inspection found UART calls an unregistered C-SKY CPUClass get_pc callback (consistent with location, not a native-backtrace proof). Failed ELF/log are preserved. All successful runs use existing smartl memlog instead; no QEMU code was patched.

Standalone code/data link at10000 in declared RAM0; explicit stack20010000 in declared RAM1. This replaces the earlier standalone library's invalid-for-smartl10003000 code placement.10003000 here is only the declared virtual memlog device; no CPU IRAM/DRAM alias or GX8002 device is assumed. Original C/assembly objects are unchanged; only generated symbols are prefixed to permit side-by-side linking. Exact original tables are hash-verified fixtures. Assembly core/split/bitrev/helpers are the prior byte-reproduced source objects; dispatch/RFFT wrappers are identical authentic compiled C on both sides, binding alternate kernel families. Added assembly radix4by2 source supports the dispatcher dependency;256-point cases use radix4.

## Limits and stopping boundary

All-min-negative direct probes confirm QEMU mulca/mulcax return7fffffff while mulaca/mulacax return80000000. These source-predicted backend corner values remain authoritative-ISA-unverified. The localized first valid split difference uses32767/16384 operands and does not require that corner; it still remains emulator/source evidence, not hardware validation.

No unsupported instruction, mapping or guard failure was reported in the successful smoke/corpus logs. Translation logs do not establish every stock opcode path executed. Bitreversal tests compare C/assembly; they are not a separately executed permutation oracle. Abs-max has no named C counterpart and is explicitly assembly-versus-scalar-oracle. No physical clock/loop timing, IRQ behavior, startup choice, audio response, universal numerical equivalence, whole-image source or byte equality is claimed.

Stop reached: first numerical discrepancy is localized and bounded. Further action needs authoritative packed-negation/complex arithmetic ISA evidence or actual hardware trace to evaluate physical semantics; remaining corpus may be resumed as explicitly model-only work if requested. No arbitrary flag sweeps, source patches, device access, canonical changes or Git/Pigweed mutations. Prior preservation receipt verifies seals,110inputs and four checkpoints; observed index is recorded, not equated to a historical baseline.
