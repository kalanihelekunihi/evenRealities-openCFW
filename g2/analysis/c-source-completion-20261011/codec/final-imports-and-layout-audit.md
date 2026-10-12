# Codec image-A remaining import and layout audit

## KWS task words

The retained `image_a_xip/decomp/10206cb0.c` constructs an eight-word
task on its own stack. It assigns words 1, 2, 5, 6, and 7. Words 0,
3, and 4 are not assigned before `LvpSetSnpuTask(auStack_3c)`. The
retained call catalogue has one caller of this loader, `0x10206d90`;
that caller supplies no task pointer or words. The selected C source
represents the three ambient words through the required
`gx8002_xip_kws_ambient_task_words` contract and copies all eight
words to native destination `0x2002e85c` through the selected child
`0x10208c14`. There is no evidenced producer, deterministic value, or
valid C initialization for the three ambient words. This import must
remain external until a native caller or stack provenance establishes
one. A chosen zero/default provider would alter observed native input.

## Floating-point environment

The selected pinned LLVM compiler-rt 20.1.8 `adddf3.c` reaches
`__fe_getround` and `__fe_raise_inexact` in `fp_add_impl.inc`.
Its `fp_mode.c` offers generic nearest-even rounding and a no-effect
inexact hook for architectures without an environment implementation.
No retained GX8002 startup or native FPU-control evidence establishes
that those generic defaults are the image-A contract. Both hooks remain
genuine external interfaces. An FP policy or native environment
producer is required before source-owning them.

## Native loaded layout contract

The authenticated normal BINH-A copy finding gives package bytes
`[87060,101776)` (14,716 bytes) to executable IRAM
`[0x10023400,0x10026d7c)`. The selected reset entry is at
`0x10023500`; it sets stack top `0x2002f7fc`, calls system initialize
then main, and remains in a terminal loop. System initialization calls
the BSS clear only on the native start-mode-zero path. That clear writes
32,620 bytes at `[0x20026d80,0x2002ecec)`. The source-owned console
port word at `0x2002731c` falls inside that conditional span.

The initialized 2,200-byte source-owned tail requires contiguous
native load addresses `[0x100264e4,0x10026d7c)`; the vector requires
`0x10023400` and the flash/API/sample pointer words require relocation
to the selected provider addresses. Native XIP consumers name data
through `0x2002xxxx` addresses corresponding to `0x1002xxxx` load
addresses, a `0x10000000` numerical difference. The observed addresses
constrain final placement and aliasing. They do not establish whether
the hardware maps both windows to the same storage, whether a separate
copy occurs, or how the conditional alternate loader path works.

Current image-A linking is relocatable. The final linker script,
loaded package composition, alias mechanism, alternate loader branch,
and native entry/runtime check remain unsatisfied. The contiguous
source-data and isolated object byte/relocation proofs are narrower
than those gates.

## Reset orchestration crosswalk

The retained native decompilation at `0x10023500` calls system
initialization, calls main, and then loops forever. The selected
`resident_reset_entry_candidate.S` performs those calls in that order,
sets stack top `0x2002f7fc`, and retains the CPU-control instructions.
The native `0x1002354c` decompilation calls clock initialization,
queries start mode, clears BSS only for mode zero, initializes the
board, then writes the interrupt controller. The selected system
initializer preserves that order, with the native CR/VIC operations
expressed as named C-SKY instructions and volatile stores. Native
`0x10023528` clears one 32-bit word per iteration over
`[0x20026d80,0x2002ecec)`, exactly 8,155 word stores; the selected
`resident_clear_bss.c` uses the same bounds and word stride. These
three bodies are already selected; adding another source copy/clear
implementation would duplicate them. The BINH-A package-to-IRAM
copy occurs in a separate loader path, outside this reset body, and
its alternate sentinel branch is not yet source-qualified.
