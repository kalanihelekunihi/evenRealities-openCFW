# R1 motion classifier in C

`native_motion_classifier.c` supplies stock `0x94c74` through C state and callback
logic, retaining one `VCVT.s32.f32` instruction for log conversion. The
[review receipt](motion-classifier-c-review.json) binds REA stock bytes, production
source/object hashes, differential checks, initialization and qualification.

The classifier gates on eight ring samples, compares signed raw float bits and
preserves the stock threshold ordering. The lower comparison is 0x3d4ccccd and
the second is 0x3e051eb8: the apparent decrement branch is unreachable with these
constants. Negative NaNs increment the wrapping halfword counter; positive NaNs
reset it. Crossing 600 sets the flag, while wrapping the count preserves its
previous flag. These details are retained rather than replacing the routine with
conventional floating-point hysteresis.

An installed callback receives every eligible invocation, including unchanged
states. State changes trigger fresh log-mode queries and one conversion of the
original input after the first mode query, even with logging disabled. The callback
is reloaded after logging; there is no second null check. Tests preserve callback
replacement and the native fault if a log provider clears it. The owned callback
cell is four bytes at `0x20006ef0`; native RW/ZI execution on poison with guards
and an independent RW decoder confirm its cold zero value. Adjacent padding and
the existing counter are not newly owned.

There are 3,000 direct paired stock/C comparisons and 1,897 integrated comparisons
executing the actual C sampler, ring, square root and classifier. They compare
public state, provider arguments, logical faults and FPSCR, and check preserved
registers, stack and interrupt masks on normal returns. Eight compiled defects
are rejected: floating-point comparison, threshold equality, lost halfword wrap,
change-only notification, second null check, stale callback, skipped disabled-log
conversion and clearing the flag below 600. Logging and notification bodies remain
modeled. Native log-provider stack depth is 32 bytes versus C 40; callbacks tail
call after frame restoration. Caller-clobbered registers, APSR and private stack
residue are excluded; physical and concurrent sensor behavior remain unproven.

All 638 units compile and both relocatable compositions succeed without duplicate
strong symbols. The previous 637 objects are unchanged. The classifier import is
resolved, leaving application/bootloader imports at 171/34. Manifest validation
passes. Exact qualification rejects this body, so the canonical source plan stays
unchanged at 4,339 source-built bytes. A fresh hybrid matches the locked application
with 641,821 executable pull-through and 248 resource bytes. Complete source-only
linking, byte identity from C and physical hardware validation remain unfinished.
