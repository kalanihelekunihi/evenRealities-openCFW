# Touch shared-power C wrapper qualified against stock bytes

The canonical source plan now includes the exact six-byte C body of
`delayed_touch_release` at `0x46f88`. Despite the historical name, this wrapper
does not delay internally: it sets shared-power client two and tail-branches
to native `r1_shared_power_client_release` at `0x50758`.

The official qualifier compiles all five Clang configurations and all four
supported pinned GCC 9 configurations. Both independently select the same exact
six-byte span after binding the native target and checking full linked bytes.
Only candidate source inputs are filtered; native anchors, matching, binding
recovery, linked equality and selection logic remain unchanged. None of the
other six touch device wrappers qualifies under these tested options. Their
[bounded behavioral evidence](touch-device-c-ops-review.md) remains separate.

The new span does not overlap the prior canonical plan. A merged candidate plan
passes a complete R1 hybrid build before the exact merged plan is promoted.
The generated 646,408-byte application is byte-for-byte equal to the locked
official application, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The hybrid report binds the promoted plan's exact hash and expected C provider.

Source-built accounting rises by six C instruction bytes to 3,827 stored bytes:
396 compiled C instruction bytes, 154 source-assembly instruction bytes and
3,277 compiled non-executable bytes. Resource files supply 248 bytes. The
remaining 642,333 bytes are unclassified binary pull-through. The accepted
wrapper still calls retained native shared-power code in this partial hybrid;
source completeness remains explicitly false despite exact output.

[Machine evidence](touch-device-c-byte-qualification-review.json) binds both
qualification runs, scope, selections, plan before/after, sources, hybrid report,
coverage and application output. The build is
`build/hybrid-goal-r1-touch-qualification`. Normal composition remains the
separately verified 572 R1 units with 197 application and 34 bootloader imports.
`make sources-check` and diff whitespace checks pass. Firmware C was unchanged
during qualification.

Complete source-only linking and byte coverage, unqualified C implementations,
physical IRQ/power/timing validation, concrete method behavior/concurrency and
G2 corpus gates remain outstanding.
