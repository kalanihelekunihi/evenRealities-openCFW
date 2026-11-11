# Profile update callback body in C

Stock event callback `0x425b0` validates a 12-byte profile record, reads its
cached predecessor, logs old and new fields, and applies the validated update.
`r1/src/application/board/native_event_profile_update.c` now implements that
behavior in C. Its public event-table entry remains
`r1_event_callback_000425b0`, a single tail-branch veneer in
`native_event_callbacks.c`. The veneer preserves incoming R0 through R3:
stock uses R2 and R3 as fallback words when the cached KV read does not fill
the predecessor record. A normal two-argument C callback could not name
those ambient register values. The C body has a private four-word interface.
At this historical checkpoint the public veneer was handwritten assembly;
the current C tail transfer is described below.

The ignored probe `build/r1-event-profile-c-20261111/verify.py` executes the
locked stock callback and the linked C callback on Cortex-M4 Unicorn. It
models the getter, updater and log sinks, then compares provider call order,
arguments, format strings, signed field values, forwarded fallback words,
ordered payload read offsets and widths, payload state, restored SP and
callee-saved registers. All 768 paired cases
pass. They cover rejected and accepted lengths, all eight combinations of
log-mode bits, two incoming R2 values, two incoming R3 values, three payload
patterns, and filled versus fallback cached records. Getter, updater and log
sink implementations are modeled boundaries; their full composition and
physical-device behavior are separate checks. Private stack bytes and
caller-clobbered return registers are outside this callback's C contract.
The first C version used two byte loads for each signed halfword. A packed
volatile C view now compiles to `LDRSH`, matching stock's three halfword
reads at offsets 8, 6 and 4 in each signed-field log branch. The strengthened
probe rejects the earlier linked object on this read-shape difference and
passes the corrected object.

`build/sources-r1-event-profile-readshape-c-20261111/report.json` compiles 962/962
application and 82/82 bootloader units without failures or duplicate strong
symbols. `build/r1-link-event-profile-readshape-c-20261111/report.json` strictly links
the application with zero undefined symbols, a complete 512-byte vector at
`0x27000`, and 693,896 of 696,320 flash bytes used. The strict bootloader
receipt is `build/r1-boot-link-event-profile-readshape-c-20261111/report.json`.
`./make.sh sources-check` lists all 1,044 R1 units and `git diff --check`
passes. The branch veneer is still assembly; the larger stock behavior body
is C. Full image byte identity and device execution remain unverified.

## Dispatcher register preservation, 2026-11-11

The stock event dispatcher at `0x8d888` loads the event record and callback
directly, then calls the profile callback with R2 holding the callback word
and incoming R3 unchanged. The earlier C dispatcher used four `memcpy` calls
before its indirect call. Its linked `memcpy` path changed incoming R3 to
zero and entered the callback eight bytes deeper than stock. When the cached
profile read left fallback bytes intact, this changed the record passed to
the update service.

`r1/src/application/board/native_event_dispatch.c` now uses volatile packed C
halfword/word views for the three record fields and callback table entry.
The current R1 Clang profile emits direct `LDRH`/`LDR` loads in stock
ID/payload/length order, no intervening
calls or R3 writes, and a 16-byte dispatcher frame. The 32-case callback
entry replay at `build/r1-event-dispatch-direct-20261111/receipt.json`
compares stock with both old and new source ELFs. The new ELF matches R0,
R1, normalized callback R2, ambient R3 and SP in every case; the old ELF
misses all 32 cases. Live R4/R5 contents at the callback differ between stock
and source, so this does not assert full register or stack-byte identity.

A second replay under
`build/r1-event-dispatch-direct-20261111/verify-integrated.py` executes the
real stock and source dispatchers and profile callback bodies for 768 paired
cases. It models the cached-record getter, updater, log sinks and final free;
the traces, payload reads, fallback record, final payload and return state
match. The previous ELF fails the same fixture when incoming R3 is nonzero
and the getter leaves fallback bytes. This is an integration check across
the dispatcher and callback; it does not execute those modeled providers or
the physical device.

The current source receipt is
`build/sources-r1-event-dispatch-ordered-20261111/report.json`; the strict
application and bootloader receipts are
`build/r1-link-event-dispatch-ordered-20261111/report.json` and
`build/r1-boot-link-event-dispatch-ordered-20261111/report.json`. All 1,045 R1
units compile. The app uses 694,120 of 696,320 flash bytes and links with no
undefined symbols or archive members. The existing single tail branch from
the public two-argument profile callback to its private four-word C body
remains necessary for the ambient fallback arguments.

## C tail transfer, 2026-11-11

The public entry now declares the observed R2 and R3 fallback words as two
additional C parameters and makes a Clang `musttail` call to the existing
four-word C body. In the current R1 profile this compiles to the same
four-byte `b.w` and `R_ARM_THM_JUMP24` relocation as the prior naked veneer.
The event table and dispatcher retain their two-argument declarations; the
extra values are an explicit ARM ABI observation rather than a portable ISO C
call contract. The old 768-case integrated stock/C replay and 32-case entry
replay remain machine-code applicable because the full linked application
raw image is byte-identical before and after this source change.

Fresh `./make.sh r1-source-link` receipts under
`build/r1-source-event-tail-c-20261111/`,
`build/r1-app-event-tail-c-20261111/`, and
`build/r1-boot-event-tail-c-20261111/` compile 963/963 application and 82/82
bootloader units, then link both regions without undefined symbols. The
application image SHA-256 remains
`2c3bf3d374eb1df387c8bf0ae942e983420065b69c814d7de8460c4f26c579ab`;
the bootloader image remains
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.
No stock byte identity or physical-device result follows from this source
image identity.
