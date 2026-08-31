# G2 `pb_service_onboarding.c` recovery

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: complete linked-object census, clean-room C implementation, production
routing, and fail-closed software verification. Live hardware validation is
explicitly blocked by unavailable authorized responsive-device evidence. Run
addresses use `run = file_offset + 0x00437FE0`.

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
tree and license remain unavailable, so no historical source-only functions
are inferred.

## Production closure

`components/apollo_main/core_overlay/pb_service_onboarding.c` is an
independently authored MIT implementation containing the nine linked
entries plus bounded buffer-write, zero-fill, and common-encode helpers. Its
12 selector-isolated functions compile to 878 Thumb bytes plus eight alignment
bytes. Nine guarded `B.W` redirects replace all 3,024 stock body bytes; 22
strict relocations bind only to recovered providers, globals, transports, and
redirected sibling entries. The 192 official gap/literal bytes remain retained.

The Apple-clang overlay/component/package are pinned at 204,372 / 3,727,768 /
4,506,262 bytes with SHA-256 values
`913b0418cdff1bedaebd49647b9efc28f44f652267dd24d9ff746cec46d82889`,
`a2f291046d44466f561b871a7fe96c2308620f13990f08878629941bc0e6d284`,
and `33c00464d8a201df3330cb520194cd16c377dca824bb36d55d6cf53f4fdd24bb`.
Host behavior, selector compilation, component assembly, manifest ownership,
package assembly, deployment-plan generation, and aggregate closure tests are
green.

No hardware was accessed. Live service-`0x10` peer BLE, display-ready,
onboarding-control, response, notification-sequence, and peer nanopb behavior
cannot be validated because the authorized right temple is nonresponsive and
the left temple must remain stock. This is an explicit physical-evidence
blocker, not a software-completeness claim for the wider firmware. The next
software protobuf-service frontier is `pb_service_notification.c`.
