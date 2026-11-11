# RTC opener saved configuration frame

`board/native_rtc_lifecycle.c` now gives the C RTC opener the native eight-byte
configuration span at entry SP minus 24. Its two words are saved R2/R3. A
10-byte ABI bridge preserves that frame and restores the complete words on
return. The previous compiler-owned configuration local had a different
provider-visible address and did not preserve the native returned words.

The C kernel loads the caller name before the record name, then performs the
same comparison and opened test as stock `0x56318`. First open copies the
existing eight-byte defaults and overwrites the prescaler with 4095. It calls
the typed RTC initializer, logs nonzero status through the existing returning
error provider, enables ticks/peripheral and marks opened. Missing/already-open
paths retain incoming R2/R3. The defaults and other RTC implementations remain
unchanged. Earlier REA observations and current raw stock execution are bound
in the machine-readable evidence.

All 486 open comparisons and nine registration comparisons pass. Coverage
includes comparison results, opened values, SDK statuses, state changes during
comparison and initialization, and full eight-byte configuration mutation by
the SDK boundary. Tests compare returned R0/R2/R3, the configuration address
and bytes, instance and tick-handler roles, provider ordering/state, R4-R11,
SP, interrupt masks and provider-call alignment. Providers clobber caller-saved
registers. Old C independently reproduces the returned-word mismatch.

All preexisting non-open function bodies and normalized relocations in the
lifecycle object are unchanged. All 562 R1 units compile without failures or
duplicate strong symbols; imports remain 211 application / 34 bootloader,
the other 561 units are unchanged and source checks pass. SDK/strcmp/error/
registration calls are modeled, so physical RTC behavior and interrupt delivery
are unverified. Native byte qualification, complete fault equivalence and final
source-only firmware remain open. The source plan and G2 gates are unchanged.
Exact bindings are in the [machine-readable review](rtc-c-open-frame-review.json).
