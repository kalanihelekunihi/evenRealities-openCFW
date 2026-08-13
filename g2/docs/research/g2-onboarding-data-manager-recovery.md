# G2 onboarding data-manager recovery

The five-anchor / 692-byte retained-path census view expands to seven linked
functions / 826 body bytes plus a 106-byte literal pool, for 932 physical bytes
at `[0x0047E2D0,0x0047E674)`. Both pathless helpers are already present in the
authenticated Ghidra corpus: the common-data state handler before the first
path-anchored function and the flag-update/event-post helper between two
anchored functions. The analyzer pins all 343 instructions, 52 calls, 11
direct entries, both physical boundaries, and the absence of stored pointers
or executable strict-interior ingress.

One whole-image halfword scan decodes bytes at `0x005FE13C` as if they were a
BL to `0x0047E512`. That address lies in compressed string/dictionary data, not
an executable function; its raw window and exact false-positive pair are pinned
separately so the exception cannot hide a future code reference.

The object owns a three-byte onboarding process record at `0x200F4800`, accepts
common-data message types one through three, updates type one under an admitted
CMSIS mutex, and uses event bit four to defer a dirty one-byte flag save. Its
peer protocol is bounded to service `0x10`, role five, and message IDs `0x09`,
`0x0D`, and `0x0E`. Wear status is sent to the phone through the already closed
command-three/tag-five onboarding protobuf encoder.

The complete reusable/provider graph is:

- 35 EasyLogger calls from the selected `a596b264…` source-equivalent core;
- exact `osEventFlagsSet`, `osMutexAcquire`, and `osMutexRelease` wrappers from
  CMSIS-FreeRTOS v10.5.1 commit `d213f261…`, over FreeRTOS-Kernel commit
  `def7d2df…` and CMSIS_5 commit `2b7495b8…`;
- three bounded IAR DLIB `memset` calls;
- four calls into the closed one-byte onboarding KVDB leaf, downstream of the
  selected FlashDB 2.1.1 commit `714d6159…`;
- one call into the closed first-party onboarding protobuf encoder, downstream
  of the nanopb 0.4.7-0.4.9.1-compatible runtime with selected 0.4.9 commit
  `98bf4db6…`; and
- six first-party role/display and peer-transport calls.

No third-party definition is embedded, no new dependency version discriminator
or private G2 generating commit is recoverable, and the object is not currently
production-routed. The remaining work here is first-party state/protocol
reconstruction and eventual integration testing, not unidentified utility code.
