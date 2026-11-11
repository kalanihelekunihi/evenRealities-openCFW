# RTT output wrapper through CMSIS C intrinsics

`runtime/native_rtt_write.c` now uses the pinned Nordic/CMSIS __get_BASEPRI
and __set_BASEPRI intrinsics instead of handwritten MRS/MSR strings and fixed
R0/R1 variables. Architectural instructions remain necessary and are emitted
by CMSIS. This is not an assembly-free CPU-register operation. The source
still initializes RTT before saving BASEPRI, writes mask 32, calls the existing
SEGGER writer and restores the low byte of the saved value. It does not change
the critical-section policy to BASEPRI_MAX or alter PRIMASK.

Normal C, previous compiled wrapper and locked stock entry 0x319e0 match in
17756 cases (53268 executions). The 3072 modeled-provider cases vary cold/warm
initialization, all 256 byte mask encodings under emulation, PRIMASK and return
statuses. Initialization deliberately changes the mask before it is saved,
and the writer deliberately changes it before restoration, verifying both
ordering and use of the saved value. Emulator acceptance of arbitrary mask
bytes is not a claim about implemented physical NVIC priority bits.

The 14652 warm initialized-ring cases execute the actual SEGGER ring writer
and memcpy; 32 cold cases additionally execute the initializer and memset.
The stock path executes stock implementations, and C paths execute their
normal source-built implementations. Ring tests vary buffer index, size,
read/write offsets, mode flags, zero/short/overlength writes and wraparound.
Blocking mode is exercised only with sufficient initial free space. Ring
bytes, control-block state, source-data guards, results, mask restoration,
PRIMASK, final saved registers and SP match. No stock instructions may execute
in source paths. There are no modeled providers in the actual-ring cases.

Five compiled defects are detected: wrong mask, omitted restoration, saving
after masking, omitted initialization and wrong return status. A clean final
baseline runs afterward. Fresh REA entry bytes match the locked application;
the companion JSON records their evidence identifier, hashes, test results
and composition audit.

The proof uses privileged thread-mode emulation. Physical interrupt delivery,
unprivileged restrictions, debugger attachment, host-driven draining progress,
concurrent writers, malformed rings/pointers, faults, private frames and
caller-clobbered registers/flags are outside its scope. Compiler portability
beyond the selected pinned Clang/CMSIS profile is not established.

All 785 R1 units compile without failures or duplicate strong symbols. Imports
remain 107 application and 22 bootloader linker metadata; strict source
bootloader linking succeeds. The 782 unrelated nongenerated objects are
identical, including the RTT initializer, ring and memory providers. The two
generated bootloader objects retain identical allocated bytes and relocations.
Global source checking retains the unrelated unlisted G2
resident_rom_thumb_set.S failure. Full application linking remains unfinished;
no source-plan qualification or byte-identity claim is added.
