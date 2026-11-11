# Rejected direct-C charger status frame candidates

The four direct-C status probes in ignored `build/goal-r1-yhm-status-c/` all
reach readiness with a 16-byte frame. Stock `0x3529a` reaches that provider with
an eight-byte frame. Normal `-Os`, explicit frame-pointer omission, `-Oz`, and
`-Oz` plus omission each fail this boundary. Firmware source and compiler
profiles are unchanged; the existing native-frame bridge remains necessary.

[Machine-readable evidence](yhm-status-c-boundary-review.json) includes execution
observations and hashes. Execution stops at the first readiness call; this is
a concrete stack counterexample, not a complete behavior test. Ordinary return
agreement cannot justify replacing the bridge or changing the saved-word address.

An additional local `-mstack-alignment=4` probe also reaches readiness with a
16-byte frame, versus stock eight. Executed boundary evidence is in
`build/goal-r1-yhm-status-frame-c/boundary-results.json`; firmware source and
manifest flags remain unchanged.
