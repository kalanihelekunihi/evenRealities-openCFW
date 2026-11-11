# Motion refresh selection and typed operations in C

`r1_motion_refresh_selection` now uses ordinary C, leaving
`native_motion_selection.c` free of inline assembly. The new
`native_motion_operations.h` describes the six-word, 24-byte operation
table with asserted offsets. Configuration/probe and FIFO fields use
their known call types. The interrupt slot represents void notification
or status-returning entries explicitly; auxiliary slots remain pointer
contracts with unowned argument ABIs.

Stock entry `0x5025c` reads the selected-provider word at `0x200076ac`
once. A null value or null probe field at offset four tail-calls provider
selection. Otherwise it tail-calls that probe. Both return the full
callee result. A volatile typed table view preserves the field read and
allows the direct C call without function-pointer signature casts.
REA/Ghidra recovers the branches, but infers a void return and repeats
the global expression in pseudocode. Instructions and execution establish
the actual single read and R0 result.

Stock/source comparison passes 1,048 scenarios. These cover null global
and probe fields, full-width results, masks, global/table mutations during
the probe-field read, and mutations by callbacks. Exactly one global read
and at most one probe-field read occur. Nonnull direct calls and isolated
fallbacks preserve the original SP and LR, verifying tail behavior.

The actual unchanged selection routine executes in 487 scenarios. Its
LIS-first, Bosch-second, QMA-third priority, stored table identity, release
ordering and return value match stock, including when release changes the
stored selection. Bus acquisition/release and identity probes are modeled,
clobber caller-saved registers/flags and require eight-byte alignment.
Callee-saved registers, restored stack and masks match throughout.

The C entry is 22 bytes versus 16 stock bytes. Every other function body
in this source retains its compiled bytes. All three operation tables
retain their bytes, alignment and relocation targets after the type
change. No pointer-table entry or provider priority was changed.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-motion-refresh/report.json`; imports remain 227
application and 34 bootloader. Probe placement of the selected word is
controlled, not final layout proof. Physical operation, timing, complete
fault state, final linking and byte identity remain unverified. No
source-plan selection or G2 workflow gate changed.

[Machine-readable evidence](motion-c-refresh-review.json) binds source,
header, manifest, build/native hashes, REA observations and ignored probes
under `build/goal-r1-motion-refresh/`.
