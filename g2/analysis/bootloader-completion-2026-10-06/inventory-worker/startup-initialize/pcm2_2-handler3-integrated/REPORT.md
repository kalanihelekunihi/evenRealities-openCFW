# Selector 3 integrated DATA relocation

This is a bounded successor to frozen candidate `687b0a4e…`, not a promoted
firmware image. The frozen base hash is
`687b0a4e3ce6aef856d19738977a8285033a36110c629d73b0b3cc7306da187d`. The new
successor is
`525a8fddaf9ee55ed06ee5b8f13f80aa22ee69612a0e618ee4cc082da59161f1`.
The 203 linker inputs and the frozen-base copy are hashed in
`input-manifest.json` staged under the ignored build tree. The build inputs are
the 202 frozen linker objects, a newly compiled selector-3 object, and the
updated initialized-data object. Only the initializer callback pointer at slot
3 and the matching source-mask bit were added to the recovered DATA source.

`verification.json` passes source/stock initialized-DATA comparison and the
native source-mask check (`0x707c10d`). The source-installed slot 3 points to
the source symbol at `0x326b9` (Thumb pointer `0x326b9`); no callback table
pointer is manually changed during the comparison. All 1371 bytes normalize
to the authenticated stock decoder output after the declared source callback
relocations are normalized. The source machine loads candidate ELF segments
only and checks that it does not execute locked executable bytes.

The integrated candidate passes all seven established direct selector-3
fixtures and one natural event-A callback fixture. The natural stock/source
callback reaches selector 3 with `[19, 7, 6, 6]`, completes with status 0, and
matches tracked state, MMIO writes, arguments, wait input, callee-saved
registers, and SP. It uses initialized stock/source callback tables as
installed. The natural test uses deterministic synthetic profile/peripheral
values and an immediate-return ROM wait at `0x40`; TIMER_A is disabled there.
The direct fixtures include the timer-ready state-26 path and call the linked
native timer service.

Direct selector-3 coverage visits 268 of 292 stock instruction bytes. The
conditional bytes not covered by these fixtures remain unverified. This
bounded proof does not run the full seven-case integration suite or unrelated
startup regressions, does not establish physical-device behavior, and does
not claim byte identity with the locked routine.

`build-integrated.sh` recompiles the two changed objects, checks them against
the staged input copies, links the successor, and reruns this verifier. Durable
ignored copies of the candidate, frozen base, linker inputs, standalone add-on
sources/receipts, integration sources, and verification are stored under
`g2/build/bootloader-completion/startup-pcm22-handler3-integrated/`.
