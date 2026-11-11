# R1 cached health profile in C

Stock entries `0x6abf8`, `0x735e0` and `0x6c640` now have ordinary C providers in `native_health_profile.c`. The validator's inline assembly was removed from `native_record_update.c`. The checked GoMore utilities delegate to the shared conversion and validation code, retaining their NULL guards. Lifecycle startup consumes the low status word explicitly and falls back to the existing default profile when validation fails.

The getter uses the existing cached-class handle and class reader. It ignores the reader's status, preserves seeded scratch words on a class-size mismatch, and copies all three words sequentially. Extraction writes all seven floats before validation: gender is one only for encoded one, and signed optional halfwords map zero to minus one. Validation accepts age 11–99, gender 0–1, height 101–219 and weight 31–149. The native validator has no NULL guard.

REA dossiers and stock instruction execution support the reconstruction. The [receipt](health-profile-c-review.json) records hashes and proof boundaries:

- 3,434 direct stock/C pairs cover every byte value for each validated field, signed optional extrema, zero sentinels, arbitrary scratch seeds, NULL getter/profile outputs, rejected class sizes, and callback-time payload/handle changes.
- 689 lifecycle startup/reset/event pairs execute the real C profile provider, cached reader and copy implementation, with valid, invalid and mismatched-size cached classes. Other lifecycle hardware boundaries remain modeled.
- Four deliberate defects are rejected: inclusive lower age bound, unsigned optional fields, incorrect zero sentinel and early abort on a failed cached read.
- The direct subset links from C without stock function bindings. Critical-section callbacks are supplied dynamically by the replay harness. It is not physical lock or flash validation.

The verified normal report is `build/sources-goal-r1-health-profile-verified/report.json`: 725 compiled units, zero failures or duplicate strong symbols, 178 application imports and 34 bootloader imports. Relative to the storage checkpoint, one unit was added, three existing objects changed, and 721 objects are unchanged. Both source manifests pass `make sources-check`.

The event-service spelling `r1_event_service_000735e0` remains unresolved. The stock getter restores scratch R2/R3, which are not part of the C result contract; its assembly callers need separate migration before sharing this provider safely. Authorization and engine initialization remain unresolved lifecycle providers. Full firmware linkage, hardware startup and physical device execution remain unfinished. Byte identity is not required or claimed.
