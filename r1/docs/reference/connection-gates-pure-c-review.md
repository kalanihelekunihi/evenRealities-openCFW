# Ordinary C connection-presence gates

`native_protocol_connection_gates.c` now implements the phone and peer predicates in ordinary C. Each reads its existing volatile 16-bit handle once and returns whether it differs from `UINT16_MAX`. Register bindings, empty assembly and the unused R1 subtraction result are removed. The historical `r1_authenticated_phone_connection_gate` name checks handle presence; it establishes no authentication or authorization.

REA bytes agree with the official stock entries at `0x4cbb0` and `0x4cb40`. **132,809 stock/C comparisons** pass:

- 65,536 handle values for each predicate, including valid zero and absent `0xffff`.
- 864 actual response-path cases across phone/peer presence, null header, allocation failure, encoder/send results and changing logging modes.
- 768 actual charge-event callback cases spanning every payload byte and phone presence.
- 105 actual notification-throttle cases spanning absent handles, first send, timestamp rollback, the 10,800-second boundary and timestamp extremes.

Results, full modeled service arguments and logs, volatile read order/width, unchanged connection words and throttle timestamp updates agree. The fixture checks stack restoration, saved registers, saved floating-point registers and interrupt masks. External allocation, encoder, send, logging, timestamp and notification services are modeled using real Thumb return stubs; source execution cannot enter the stock image.

A raw halfword-aligned direct-call scan finds the four calls used by these three callers. No aligned Thumb pointer literal matches the gates; dynamically constructed indirect references are not proved absent. The response saves packet inputs before its gate calls; the charge notifier has a void/no-argument contract and the throttle supplies explicit service arguments. The removed R1 residue is outside the public return contract.

Five compiled defects are rejected: inverted presence, treating zero as absent, byte-truncated handles, reading the wrong phone field and widening the volatile load. The normal open-toolchain report compiles all **855 units**, completes both relocatable compositions and leaves **61 application / 22 bootloader imports** unchanged. All **844 other nongenerated objects** remain identical. The probe object matches the normal build. R1 source validation passes; the manifest and source plan are unchanged. No persistent state is added.

Physical connections, transport timing, final linking and boot remain unverified. Private scratch-register residues, APSR and faults/concurrency are excluded. Assembly elsewhere in the three callers is unchanged. Byte identity is not required for this change.

[Machine receipt](connection-gates-pure-c-review.json) binds the source, build reports, REA evidence, call scan and ignored probes under `build/goal-r1-connection-gates-pure-c/`.
