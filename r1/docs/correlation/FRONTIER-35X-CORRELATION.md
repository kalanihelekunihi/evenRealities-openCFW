# 348...354-byte frontier correlation

The five largest remaining functions after the 364-byte tier are now source-routed from exact
body hashes and complete direct/tail-caller scans:

| Recovered function | Bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x00033DBC..<0x00033F1E` | 354 | `52c100f23a936a8344170aed0c63d53b3f3ede79b9e7c2aee01e59f21b6a5176` | R1 BLE-to-thread envelope policy |
| `0x0008216C..<0x000822CC` | 352 | `a858402f6e9667b3cce7992510f8497101c7560a09a3c3ba87d08a22c1c01368` | R1 Peer Manager diagnostic, LTK output redacted |
| `0x000425B0..<0x00042710` | 352 | `dc30b28db92809ab9c15f66cc5e01ad9d59e0b8e84dd73d8c569f5df0602fc39` | R1 user-profile transition policy |
| `0x00094384..<0x000944E2` | 350 | `bd4728f0616cfce144cbe113dc5c4583fbe7481fd3cdf036146edad24176c214` | owner-authorized transparent GoMore sensor-update orchestration |
| `0x0006A714..<0x0006A870` | 348 | `eb3d69ee62b4c1d8d73a8d8da8d4b1d82d80c5c9a77cbc89fee1cf1b5c4fa6fe` | R1 glasses-status lifecycle policy |

`0x00033DBC` is called only by the already product-routed BAE8 callback at `0x0005D650`. It
allocates `(payload + 15) & ~3` bytes, zeroes the allocation, writes three little-endian UInt32
fields (message type, context, payload length), copies the payload after the 12-byte header, and
hands ownership to an RTOS queue. `r1_ble_thread_message_encode` implements only the deterministic
envelope. Allocation, FreeRTOS queue locking/put, wake flags, logging, and cleanup remain external.

`0x0008216C` is reached from the Peer Manager policy at `0x0007F488` and tail-call `0x0007F632`.
It validates the peer id, calls Nordic `pm_peer_data_bonding_load`, and prints the 16-byte LTK.
The security audit already excludes this secret-bearing output. The clean-room
`r1_peer_bond_diagnostic_plan` preserves invalid/load-failed/success classification but maps every
successful load to `REDACTED`; it accepts no key bytes and cannot log or export them.

`0x000425B0` is the indirect event-`0x100A` consumer already pinned by the static user-profile
audit. It accepts exactly 12 internal bytes, obtains the prior profile, and delegates validation,
persistence, significance thresholds, and optional GoMore reinitialization. The clean-room
`r1_user_profile_plan_transition` owns only validation, full-record change detection, exclusive
2-year/9-cm/9-kg thresholds, and typed persist/reinitialize decisions. KV persistence and the
GoMore engine stay external. The public command remains hardened: it validates before success and
does not reproduce the stock uninitialized tail, truncation, gender-map mismatch, or premature ACK.

`0x00094384` has two direct callers, `0x0006ACAE` and `0x0006C2A2`, both within GoMore processing
paths. Its complete orchestration is now reconstructed as
`gomore_primitives_sensor_update_orchestrate`: diagnostics, input application, and snapshot
production are typed providers, while runtime/version validation, nearby timestamp substitution,
stale rejection, commit order, and the high-bit-preserving update counter are transparent C. Its
formerly opaque descendants at `0x00094590` and `0x00059D9C` are already local as the typed host
input adapter and output-snapshot copier.

`0x0006A714` is reached by the legacy command dispatcher at `0x0004E368` and tail-call
`0x0006267E`. Status bits 7 and 6 independently drive wear and secondary-mode transitions. The
clean-room `r1_glasses_status_plan_command` preserves the recovered 7-byte response, cancellation,
`0x96000` slow-event delay, `0x7800` DCDC delay, touch-open, DCDC, BLE-slow, and touch-fast
decisions. CMSIS/FreeRTOS delayed events, SoftDevice connection changes, power control, touch,
logging, and response transport are provider seams in the portable model. The source-built Zephyr
target now binds the bounded opcode-`0x89` route only after encrypted, bonded, independently
authorized glasses-role admission; its delayable work executes touch open/release and REG1
immediate-disable/delayed-enable actions and emits the exact seven-byte channel-1 response.
Secondary-mode entry requests the recovered `{16,16,2,600}` BLE profile immediately; exit applies
the recovered `{72,84,4,600}` profile after exactly `0x2800` ticks, with disconnect cancellation
and glasses-role revalidation. Physical radio timing and electrical behavior remain open.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_35x.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

The linked Nordic SDK image retains the four clean-room product APIs at `0x00035F9C`,
`0x00036234`, `0x00037F3A`, and `0x00038002`, respectively. The current unsigned application
build is 95,040 bytes (`text=94,804`, `data=236`, `bss=132,544`), with HEX SHA-256
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and BIN SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.
