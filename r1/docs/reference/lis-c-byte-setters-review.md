# LIS single-register setters C extraction

Sixteen stock setters now share C read/modify/write logic in
`native_lis_call_frames.c`: block-data update, FIFO mode and watermark,
filter bandwidth, full scale, reset, three tap-axis enables, tap duration,
mode, quiet, shock and three thresholds. The existing attributed ST C field
helpers remain the implementations of their byte calculations. REA analysis
was completed at each of the sixteen native entry addresses.

Each entry retains a 12-byte assembly bridge that captures incoming R3 at
entry SP-16 and restores its modified word. Four literal bytes identify an
eight-byte constant descriptor containing the register and field helper.
The common C body is 54 bytes with the current compiler; each original stock
routine is 46 bytes. These are partial C extractions, not byte-identical
replacements or assembly-free entries.

The C body requests one byte, returns any nonzero read status immediately,
updates the explicit volatile scratch byte using the full incoming value,
then writes the same byte and returns that full status. Successful reads
that leave the output untouched retain the incoming R3 seed. Callback changes
to the full saved word also survive its restoration. No scratch initialization
or additional error policy is introduced.

The ignored `build/goal-r1-lis-byte-setters/verify.py` probe passes 33,280
stock-versus-C scenarios: 2,080 per setter. Actual transport wrappers and C
field helpers execute. An independent mask/shift oracle checks byte results.
Coverage includes all 256 low-byte values, all scratch seed bytes, full-width
values and statuses, read/write failures, non-writing reads, callback changes
to the whole scratch word, and live callback/handle replacement. Checks cover
context-read and scratch-access order, bus pointers and bytes, full return
values, R1/R2 callback results, restored R3, callee-saved registers, SP,
interrupt masks and eight-byte callback alignment.

The six other function bodies in this compilation unit remain unchanged.
The complete R1 source build compiles 562 units without failures or duplicate
strong symbols. Imports remain 227 application and 34 bootloader. Exact
source, manifest, stock spans, REA analyses, integrated sources and probe
bindings are in [the machine-readable review](lis-c-byte-setters-review.json).

Final bus callbacks are modeled. The shared C body changes callback stack
depth while preserving the native request byte address. Physical sensor
configuration, timing, complete fault-state equivalence, final linking,
provider qualification and byte identity remain unproven. The outer tap
enable/disable sequences remain assembly pending their own extraction;
their cross-call scratch dependencies require separate treatment. No G2
workflow gates or provider selections change.
