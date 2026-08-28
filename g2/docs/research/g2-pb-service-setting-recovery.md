# G2 `pb_service_setting.c` recovery

Status: software-closed and production-routed from independently authored,
selector-isolated C; live service-9 qualification is deferred by project
direction. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Eleven exact-named functions and five owned gap/pool regions occupy
`[0x0049B198,0x0049C070)`. The bodies contribute 3,466 bytes with SHA-256
`ee22c4e8bb16352019d0cc8462f5522ee026ba29ccd334d90e366a2ce3b23d87`;
the 334 gap/pool bytes have SHA-256
`a888b97fd501039b114ffe1897120215496bc9cdbd5137b4c8fc4644a513acc2`.
The complete 3,800-byte object has SHA-256
`af57ba66a30263a8e01d0975696d760f93ebe403f8988af911f811dad72f5268`.
An unrelated allocation wrapper begins at `0x0049C070`.

The nine corpus anchors omit two valid source-order functions:
`setting_respond_with_local_data_serialize` at
`[0x0049BA58,0x0049BBB0)` and
`setting_notify_recalibration_status_to_app` at
`[0x0049BEAC,0x0049BF16)`. Both have exact-start exterior callers, retained
diagnostic names, valid Thumb prologue-to-return reachability, and fit between
their public-facing siblings and owned pools. The complete object has 23
exact-start entries and 221 body calls. Direct and `B.W` strict-interior
ingress are zero. Thirteen all-byte address collisions are instruction/data
windows rather than stored entry pointers.

## Message behavior

`setting_parse_data_package` rejects null inputs, decodes the protobuf package,
and suppresses a repeated 32-bit magic value. On first receipt it records the
command and magic globals and returns 1; null, decode failure, and duplicate
input return zero.

The response path uses a 104-byte setting message, a 256-byte encode buffer at
`0x200706EC`, and the shared nanopb field descriptor at `0x0077772C`.
`setting_respond_to_app` emits command 1 using the parsed magic.
`setting_build_full_status_package` emits command 2 / tag 4 and gathers the
brightness, left/right version, head-up, battery/charging, silent-mode, and
unread-message state. The two serializer wrappers are master-role gated and
transmit on route 1 / service 9. Invalid command zero returns 1, encoding
failure returns `0x2B`, and success returns zero.

`setting_notify_common` copies a 104-byte package, increments the notification
magic at `0x2007486C`, encodes it, and notifies route 1 / service 9. Null input
returns 1, encode failure `0x2B`, and success zero. The device-status wrapper
uses command 2/tag 4. Recalibration and silent-mode wrappers share command 3 / 
tag 5 and use nested selectors 1 and 2 respectively.

The retained source path has two literal references but no standard assertion
record. Eleven retained diagnostic strings provide the exact source names.
The historical source tree and license remain unavailable, so source-only
functions are not inferred. The independently authored MIT
`components/apollo_main/core_overlay/pb_service_setting.c` provides 13
selector-isolated functions: the 11 recovered entries plus bounded buffer and
zero helpers. They compile to 1,650 Thumb text bytes plus 14 alignment bytes;
38 strict relocations terminate only at recovered nanopb, BLE, role/config,
runtime-status, request, unread-count, or sibling-source interfaces. Eleven
guarded redirects replace all 3,466 stock body bytes while the 334-byte
authenticated gap/pool set remains official.

Host tests cover bounds, duplicate filtering, decode statuses, full-status
field construction, local/remote response paths, role gates, transport
arguments, monotonic notification magic, and both status selectors. The
component, manifest, 4,510,208-byte package, 2,218,642-byte flash plan,
complete-service ledger, and origin accounting are pinned. Live service-9
peer BLE, full-status, recalibration, silent-mode, and nanopb interoperability
qualification is blocked by unavailable physical evidence. The prior nonresponsive-fault
inference is superseded: the charging case was accidentally bumped during
lunch and caused the disconnect, rather than a device or flashing fault.
Future acceptance still requires authorized peer BLE, recalibration,
silent-mode, full-status, and nanopb interoperability evidence; none is a
remaining setting software gap or a software-routing blocker.
