# Touch identity probe uses ordinary C

`native_touch_identity.c` now has no fixed-register declarations or inline assembly. The local ID word starts at zero, and the public C operation returns its low byte. The probe still sequences power and GPIO operations, polls at most 100 ready reads, reads two ID bytes from register zero, and performs final stop/power cleanup regardless of bus status.

This retires the incidental full-word R3 return described in the [earlier probe review](touch-probe-c-review.md). Both requested ID bytes already began at zero in stock. Untouched upper scratch bytes are not inputs to the low-byte result. The separate ready-reader helper remains unchanged, including its existing raw register contract.

The [receipt](touch-probe-pure-c-review.json) records 2,592 complete stock/C probe comparisons and 928 unchanged ready-reader comparisons. Cases include early readiness, the last permitted read, exhaustion, partial/absent/full ID updates, provider errors, changing cached handles and late cleanup writes to the live ID buffer. Production C request and ready-reader helpers execute. Provider order, request bytes/length, delays, polling count, low-byte return, shared handle state, stack balance, callee-saved registers and masks agree. Three controls with 99 polls, a one-byte ID request or missing power cleanup are rejected.

REA returned all 126 bytes through the stock entry's final POP. No fresh function-dossier coverage is claimed for this entry. Replay uses no memory-read hooks. GPIO, power, delay and final registry boundaries remain modeled. Electrical response, physical touch identity, timing, arbitrary aliases/faults and concurrency are unverified. Probe caller-clobbered registers and unused upper scratch bytes are excluded from the C API proof.

The normal report is `build/sources-goal-r1-touch-probe-pure-c/report.json`: 727 units compile without failures or duplicate strong symbols. Application/bootloader imports remain 178/34. Only the touch identity object changed; 726 objects remain unchanged from the PMIC checkpoint. Both manifests pass `make sources-check`. No byte identity or completed firmware image is claimed.
