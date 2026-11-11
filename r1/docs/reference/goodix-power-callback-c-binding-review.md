# Goodix shared power callback setter reconstructed in C

REA confirms stock `0x50998` stores the incoming word at `0x200076c8` without
validation and returns with R0 unchanged. The existing shared C
`r1_goodix_release_callback` already owns that word and is consumed by acquire
and release policies. `r1_health_module_field_set` now supplies the missing
producer, retaining its historical source-mapping name. No second state cell
is introduced. Zero clears the word; odd/even/high words are stored verbatim.

The C declaration returns the observed unchanged R0 word. Ghidra infers void;
this does not establish that external callers use a semantic return value.
Native instructions perform no flag changes, and the compiled C boundary is
tested for the same behavior. Concrete callback validity is not inferred from
acceptance by this setter.

The standalone probe passes 1,536 paired stock/C cases (3,072 executions): eight
input words, all NZCVQ combinations and interrupt-mask variants. It compares
one four-byte callback store, unchanged mask/ten counters/adjacent word, R0,
flags, preserved registers, stack and interrupt masks.

Another 2,080 setter-to-acquire and 2,080 setter-to-release comparisons execute
the actual setter and policy bodies together. The callback cell begins with a
different word; only the setter installs or clears the tested callback. External
hardware/SDK methods and callback targets are modeled. Cases retain the prior
count, selector, mask and callback-mutation matrix, proving that both consumers
read this same C-owned word and preserve their stock reload decisions.

A wrong-cell variant storing into the neighboring active mask is rejected.
An executable-section audit confirms that all pre-existing Goodix policy
sections remain unchanged; only the setter section is added. Both import sets
are unchanged.

The normal report `build/sources-goal-r1-goodix-power-callback/report.json`
compiles 571 R1 units without failures or duplicate strong symbols. Imports
remain 197 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-power-callback-c-binding-review.json) binds REA, shared
source owner, standalone/integrated probes, negative control, section audit and
normal build by hash.

The C setter is twelve bytes versus six native instruction bytes and is not
byte-qualified. The canonical source plan stays unchanged at 3,821 source-built
bytes in the last verified hybrid. Initial placement, concrete callback targets,
caller-clobbered registers except the observed R0 boundary, concurrency, physical
power/reset behavior, complete source-only byte identity and G2 corpus gates
remain unverified.
