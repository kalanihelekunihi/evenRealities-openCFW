# G2 `pb_service_onboarding.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Nine exact-named functions and three owned alignment/literal regions occupy
`[0x004A78D0,0x004A8560)`. The bodies contribute 3,024 bytes with SHA-256
`56f0c2d54aa65832669d28bcaa24d022886fd11224595881009f2feb0a0503a6`;
the 192 gap/pool bytes have SHA-256
`0c9793e2789ea9c94675bec3252590ce396ea6c1e0e544034112e119f4b5dbfa`.
The complete 3,216-byte object has SHA-256
`3c62388010aee013633ecdb222617b023ae9a831c82eb1c5860ac8856f6c9cb5`.
An unrelated allocation wrapper begins at `0x004A8560`.

Nine exterior calls enter exact starts and the bodies contain 181 calls.
Direct and `B.W` strict-interior ingress are zero, and there is no stored exact
entry pointer. Three all-byte interior-looking values are unaligned
instruction/data collisions. Eight standard 20-byte assertion records pin the
retained path, the eight command-specific function names, and source lines
103, 117, 152, 188, 201, 240, 254, and 294. The dispatcher has an exact
retained diagnostic name but no assertion record.

## Message behavior

`APP_PbRxOnboardingFrameDataProcess` returns 2 for null input, `0x2B` for
nanopb decode failure, and dispatches commands 1 (configuration), 2
(heartbeat), and 3 (event). Unknown command IDs return 1. Each known command
runs its receive processor first; a nonzero processor result returns 1,
otherwise the matching transmit wrapper supplies the final status.

The object uses a 16-byte decoded message at `0x200F622C`, a 16-byte transmit
message at `0x200F623C`, the 256-byte buffer at `0x200F612C`, and route 1 /
service `0x10`. Configuration uses command 1/tag 3. Heartbeat uses command
2/tag 4 and reports state zero only when both readiness predicates succeed,
otherwise 8. Events use command 3/tag 5; event 1 normalizes its parameter to a
boolean derived from the current onboarding state. Transmit wrappers return 2
for null input, `0x2B` for encode failure, and zero for success.

Notification variants increment the shared byte at `0x20074FFB` and use the
notify transport rather than the response transport. The historical source
tree and license remain unavailable, so source-only functions are not
inferred. No clean-room candidate exists, the service is absent from
`overlay.json`, and OpenCFW claims zero production ownership bytes. The next
retained protobuf-service frontier is `pb_service_notification.c`.
