# R1 sleep sync packet and ACK chain in C

The R1 sleep sync chain now has C implementations for stock application
functions `0x8da24` (packet builder), `0x8f780` (ACK callback), `0x836ba`
(direct event post) and `0x83704` (module 6 event post). The packet and ACK
functions are in separate files under `r1/src/application/runtime/` and
listed in `r1/src/sources.json`. The two event-post wrappers extend the
existing `native_health_event_post.c` implementation.

The packet builder allocates and zeroes a 32-byte header plus three bytes
per source stage. It copies the stock header fields, calculates the UTC
offset only after the stock timestamp threshold, compresses consecutive
stage kinds into three-byte runs, and skips posting if no runs remain. It
applies the current sync block as a range limit under the stock conditions.
A zero-valued source kind requests the ACK-context path; absent or nonzero
source kind uses the direct post path. The ACK context carries the source
head and original report range. Both paths free the temporary packet.

The ACK callback posts event `0x2001` with its twelve-byte context, logs
null, send failure or success according to the live log modes, and frees a
non-null context. The direct post wrapper uses caller-supplied flags and
sequence without ACK registration. Module 6 uses the existing shared
ACK registration, payload send and failure cleanup path with opcode
`0x601`.

Paired stock/C emulator checks passed:

- 1,436 cases across the event-post wrappers and shared send path, including
  the new direct and module 6 entries.
- 1,480 packet-builder cases covering empty and 255-stage inputs,
  run compression, allocation failures, both transport paths, logging,
  timestamp threshold, and sync-block variation. Packet bytes and provider
  calls match.
- 84 ACK callback cases covering null context, send outcomes, changing log
  modes and provider mutation of context fields.

Probes and receipts are under
`build/r1-event-post-module6-probe-20261110/`,
`build/r1-sleep-sync-packet-probe-20261110/`, and
`build/r1-sleep-sync-ack-probe-20261110/`. These compare the pinned stock
application with compiled C; lower providers are modeled at the call
boundary.

The strict R1 build compiles 886 application and 82 bootloader units with no
failures or duplicate strong symbols. The strict bootloader links with a
valid 512-byte vector. The packet builder replaced its unresolved import
with the ACK callback import, which this step then closed. The application
therefore has 36 unresolved functions, one fewer than before the chain,
but still does not link. Full flash load exceeds the configured region by
30,232 bytes; the ld output-section diagnostic is 23,304 bytes. Build and
link receipts are under `build/r1-sleep-sync-chain-final-20261110/`.
The full `make sources` build also passes at
`build/sources-sleep-sync-chain-20261110/report.json`. Neither manifest
changed during that run; both device trees have zero compile failures and
zero duplicate strong symbols. `make sources-check` and `git diff --check`
pass.

The provider model does not establish real event delivery, allocator
ownership under asynchronous ACKs, physical health transfer or stock byte
identity. The application still requires its remaining source providers and
flash fit.
