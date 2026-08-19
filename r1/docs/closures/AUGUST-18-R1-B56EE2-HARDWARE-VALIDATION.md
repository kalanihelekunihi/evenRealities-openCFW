# August 18 owned-R1 BLE validation

## Continuation status

### Destructive BLE transition result

The owner explicitly designated B56EE2 as a sacrificial development unit and
authorized firmware writes. The iPhone debug probe re-established the direct
phone role, sent the recovered 244-byte ACE DFU request, and independently
observed the Secure DFU advertisement `B210_DFU_B56EE3`. Nordic Secure DFU
then verified and installed the owner-signed 24,576-byte temporary transition
bootloader: every progress callback from 0 through 100 percent completed and
the terminal DFU state reported success.

The device did not advertise after the activation reset. Neither a filtered
iPhone CoreBluetooth inventory nor a broad macOS CoreBluetooth scan observed
the application, Secure DFU, or transition advertisement for more than the
expected reset interval. The second, source-boot staging archive was therefore
not transmitted. B56EE2 is presently non-advertising and requires a physical
power cycle or SWD recovery before it can provide further evidence.

The ring had been paired to and connected through this Mac before the write,
and the retail application permits only one host connection. That explains the
earlier Mac/iPhone contention but not the post-activation silence: after the
DFU reset, `system_profiler` listed no connected R1, and CoreBluetooth returned
no already-connected peripheral for either the exact BAE8 service or Nordic
`FE59`. The transition activation terminated the prior host connection and no
new connection is currently suppressing its advertisements.

Postmortem comparison against the SHA-pinned live bootloader found a concrete
hardware configuration defect in the first transition build. The retail
`nrf_sdh_enable_request` loads the exact `nrf_clock_lf_cfg_t` bytes
`00 10 02 01` from `0x000FDC68`: internal LFRC, calibration interval 16,
temperature interval 2, and 500-ppm accuracy. The source reconstruction had
inherited the PCA10056 example's external LFXO selection. The corrected build
pins all four recovered values, restores MBR-address population as the first
boot operation, and changes the preflight settings load from mutating
`nrf_dfu_settings_init(false)` to read-only `nrf_dfu_settings_reinit()`.
Those corrections are source/build verified but are not yet physical proof;
the failed unit cannot receive them over BLE while it is non-advertising.

After the read-only campaign below, the owner-authorized ACE path captured all
216 live flash pages at `0x27000..<0xFF000` plus the exact 0x308-byte UICR
extent. Those records now pass the page-by-page mixed-provenance recovery-basis
and offline deployment verifiers. The owner-signed source build also now
contains a source-built `OPENR1-RECOVERY` GATT loader below slot 0, so later
application interruption is recoverable without the retail bootloader.

Before the destructive continuation, the ring was observed advertising again
on the same CoreBluetooth UUID after the build work. The paragraph above now
supersedes the earlier no-mutation/withheld decision: the first transition
write was attempted and completed, while the following reset failed before
the page-zero source image was staged.

A final post-build read-only preflight repeated the same authenticated route.
The ring advertised at the same CoreBluetooth UUID, exposed exactly the BAE8
and Secure DFU services, returned unchanged application/hardware identity, and
completed three of three status requests with zero drops at
96.131...118.594 ms (105.908-ms mean) after the v11 FDS-transition,
owner-state-hardening, dispatch-arena, and linked-RAM-gate bundle was
verified. The unchanged retail identity was application `2.2.8.0002` and
hardware `603MV1.9.3`. The host still enumerated no SWD/J-Link,
CMSIS-DAP, Nordic, or serial debug probe and no compatible programmer command.

## Scope and safety boundary

An owner-authorized R1 advertising as `EVEN R1_B56EE2` was exercised from
macOS through CoreBluetooth. The probe was limited to advertisement and GATT
discovery, notification-CCCD setup, the recovered ephemeral `pairAuth` phone
role selector, fixed read-only `deviceInfo` and `deviceStatus` requests, and a
later bounded channel-coexistence test. That test used only the seven-byte
legacy opcode-`0x89` frame with byte 3, its recovered command-valid flag, set
to zero; consequently none of the wear, secondary-mode, touch, regulator, or
radio-policy actions could be selected. No arbitrary write interface exists
in the probe. No DFU, advertising-control, power, storage, sensor-control,
factory/eAT, NFC, or flash operation was sent.

The checked-in C utility generates the three allowed channel-2 frames through
`r1_model_encode` and `r1_fragment_message` and emits the fixed non-mutating
channel-1 frame. The Swift transport refuses to start unless its independently
implemented framing is byte-identical to those C vectors. Every received
channel-2 model is accepted only after the non-reflected outer Castagnoli CRC,
declared length, and direction-specific inner MODBUS CRC pass. A channel-1
reply is counted only if it exactly equals the recovered seven-byte
acknowledgment; unrelated channel-1 notifications are reported but not
misclassified.
Manufacturer contents, the device address, the provisioned serial, protocol
payload values, and bond keys are not retained in this record.

## Observed target

The advertisement was connectable, used the expected complete local-name
prefix, reported manufacturer company identifier `0x5245`, and carried a
23-byte manufacturer element. The read-only device-info response identified:

| Field | Value |
| --- | --- |
| Application | `2.2.8.0002` |
| Hardware | `603MV1.9.3` |

The hardware revision therefore matches the reconstructed target, but the
installed signed retail application is later than the analyzed
`2.2.6.0009`. These results are cross-revision compatibility evidence, not a
claim that the two application images are identical.

Eight raw CoreBluetooth callbacks initially exposed sub-0.1-ms
advertisement/scan-response pairs, proving that raw callback deltas cannot be
treated as the advertising interval. A corrected six-sample run coalesced those
pairs. Distinct host observations ranged from 1.006 to 15.052 seconds with a
9.447-second mean. The minimum is consistent with a slow-advertising regime,
but macOS scan coalescing prevents an on-air interval claim without HCI/radio
capture.

## GATT inventory

CoreBluetooth discovered exactly two primary services:

| Service | Characteristic | Properties | Descriptors |
| --- | --- | --- | --- |
| `BAE80001-4F05-4503-8E65-3AF1F7329D1F` | `BAE80010-...` | write without response | none |
| same | `BAE80011-...` | notify | CCCD `0x2902` |
| same | `BAE80012-...` | write without response | none |
| same | `BAE80013-...` | notify | CCCD `0x2902` |
| `FE59` | `8EC90003-F315-4F60-9FB8-838830DAEA50` | write, indicate | CCCD `0x2902` |

This confirms the recovered four-lane BAE8 layout on `2.2.8.0002` and the
Nordic Secure DFU control point. No readable flash, UICR, memory, or backup
characteristic exists.

CoreBluetooth reported maximum write-value lengths of 512 bytes with response
and 20 bytes without response on every continuation connection. The latter is
useful host-API evidence for the active link bound, but it is not promoted to
an exact ATT-MTU or data-length claim without raw HCI capture.

## Raw-HCI capture attempt and evidence gate

Apple PacketLogger 26.0 is installed with both GUI and command-line capture
paths. An authorized capture was started before a repeated bounded 20/20
coexistence run. The live ring run itself again completed all twenty channel-2
responses with zero loss, but PacketLogger produced only one note record:
`Disconnected from OS X Device`. The `.pklg` is exactly 260 bytes with SHA-256
`f0c2c2f96a0e1c67471032379e53ad265dc64af81933c505c59a05f119a419e4`.
PacketLogger's live GUI likewise remained at zero HCI/ACL packets. The macOS
unified log provides the decisive cause after successful PacketLogger
authentication: `Bluetooth Profile Required`. No diagnostic configuration
profile was installed or system security setting changed. Apple's official
Profiles and Logs page identifies the required macOS download as
`Bluetooth_macOS.mobileconfig` with separate logging instructions; both require
an Apple Developer sign-in and installing the profile remains a separately
confirmed system-security action.

`tools/analyze_r1_hci_capture.py` now independently parses the Apple
PacketLogger record envelope, HCI event/ACL records, fragmented L2CAP, and ATT.
It omits addresses, keys, and ATT values and can require exact capture hash,
connection interval, MTU exchange, data-length change, PHY, encryption,
Number Of Completed Packets, channel-2 write/notification traffic, and ATT
Prepare/Execute Write rejection. Six synthetic tests cover complete evidence
and every relevant fail-closed boundary. The actual 260-byte capture is
correctly reported as `note: 1`, with all eight evidence gates false; therefore
it closes no raw-HCI capability row and records a precise external prerequisite
instead of being mistaken for a valid trace.

## Paired-iPhone continuation

The paired iPhone 17 Pro Max running iOS 27.0 was also exercised through nRF
Connect for Mobile. A name-filtered scan displayed `EVEN R1_B56EE2` as
connectable, decoded company identifier `0x5245`, and independently classified
the advertisement as `DFU: Yes (nRF5 SDK)`. One connection reached the iOS
Bluetooth pairing prompt; owner approval briefly produced a connected state
and CoreBluetooth service discovery. Later attempts disconnected during
service discovery. At the end of the bounded run nRF Connect showed a cached
last value of -94 dBm and no new packet after 18:21, so the later failures are
recorded as stale/weak-radio evidence rather than a firmware rejection.

iOS 27 did not expose the Bluetooth packet logger service through the prepared
developer-device tunnel, so the phone added no raw ATT/HCI evidence. The
source-only companion under `tools/ios/R1PhoneDiagnostics` nevertheless builds
for generic iOS with signing disabled. It contains only exact-vector-checked
phone-role, device-info, status, and command-invalid opcode-`0x89` operations;
physical installation was unavailable because this Mac has no development
provisioning profile for its bundle identifier.

nRF Connect was not given either build artifact. The Nordic
`openr1-owner-signed.zip` is an application-only package rooted at `0x27000`,
declares SoftDevice requirement `0x0100`, and necessarily retains the opaque
S140 and retail bootloader. The opaque-free source bundle instead installs
source-built MCUboot/BLE at page zero and is an
`openr1-transparent-full-flash` archive, not a Nordic Secure DFU ZIP. Treating
the former as completion would violate the source boundary; feeding the latter
to the retail DFU client would violate both its format and the verified
first-install recovery contract. During this initial nRF Connect pass, no
erase, DFU transition, or firmware write was attempted. The later dedicated,
hash-pinned debug-probe write is the separately recorded destructive
continuation at the top of this document.

## Role, bond, and reconnect evidence

Before `pairAuth`, a valid status request sent after channel-2 notification
setup produced no response during the bounded run. The C-vector-checked
phone-role request then produced:

- a success response with one zero payload byte;
- a separate checksum-valid unsolicited type-2 `pairAuth` model;
- a subsequent unsolicited type-2 device-status model; and
- successful solicited status responses with the requested serials echoed.

Observed role-response round trips were 57.887, 61.151, and 92.894 ms across
separate connections. macOS subsequently placed the ring under **My Devices**,
and later connections reused that retained relationship without another user
prompt. This physically distinguishes application role selection from the
persisted SMP relationship. CoreBluetooth does not expose the LTK, negotiated
encryption procedure, or a definitive application-level authorization bit, so
key/replay/repair claims remain out of scope.

After the relationship was retained, a separate connection subscribed to
channel-2 notifications and sent one C-vector-checked status request without
`pairAuth`. The exact request serial received no response during a bounded
three-second observation. A following connection with `pairAuth` immediately
restored requested responses. This confirms that the retained transport
relationship alone does not restore the stock application phone route.

## Channel-2 timing and backpressure

A sequential three-request run used unique serials and a 250-ms delay after
each reply. All three responses were checksum-valid and ordered:

| Sent | Received | Drops | Minimum | Mean | Maximum |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 3 | 0 | 37.975 ms | 55.581 ms | 69.351 ms |

A separate bounded burst queued twenty non-mutating status requests without
waiting for replies. All twenty responses were checksum-valid and ordered:

| Sent | Received | Drops | Minimum | Mean | Maximum |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 20 | 0 | 59.740 ms | 293.226 ms | 478.024 ms |

The monotonic latency growth is physical queue/backpressure evidence for the
retail channel-2 plane. It does not validate source-built scheduler tick units,
raw HVN completion counts, or the four-slot Zephyr notification pool because
the source-built image was not installed.

## CCCD and disconnect recovery

A dedicated run completed the following channel-2 lifecycle on one connection:

1. enable notification CCCD;
2. disable it and receive the disabled-state callback;
3. wait 250 ms, re-enable it, and receive the enabled-state callback;
4. complete `pairAuth`; and
5. receive all three uniquely serialized status replies.

The post-cycle status latencies were 57.783, 157.711, and 99.893 ms. No stale
notification from the disabled interval was accepted.

A separate disconnect-under-load run queued twenty fixed status reads and
requested a normal central disconnect after 100 ms. Four replies arrived before
the disconnect, in order, at 55.139...83.026 ms. The remaining sixteen were
classified as interrupted by the intentional disconnect, not transport drops.
The ring returned to connectable advertising. The immediate recovery run then:

- connected in 3.123 seconds;
- reused the retained macOS relationship without a pairing prompt;
- returned `pairAuth` success in 91.452 ms;
- returned the unchanged application/hardware identity; and
- completed three of three status reads at 40.101...97.778 ms.

This closes later-revision CCCD toggle and clean disconnect/reconnect behavior.
It does not expose the stock raw HVN credit counter or prove the source-built
runtime's disconnect cleanup until that image can be installed safely.

## Interleaved channel-1/channel-2 load

After the exact recovery basis and fail-closed SWD rollback tooling existed, a
new fixed probe mode exercised cross-lane receive load without invoking a
diagnostic or state-changing route. It subscribed to both notification lanes,
completed the phone-role selector, and alternated each channel-2 status request
with the seven-byte channel-1 opcode-`0x89` frame whose command-valid byte is
zero. The probe caps this mode at twenty channel-1 writes, requires a bounded
channel-2 burst, and forbids combining it with CCCD cycling or intentional
disconnect.

A one-channel-1/three-channel-2 preliminary run returned all three status
responses with zero loss. The full run then alternated twenty writes on each
receive characteristic. All twenty channel-2 responses were checksum-valid,
ordered, and lossless:

| Channel-1 writes | Channel-1 replies observed | Channel-2 sent | Channel-2 received | Drops | Minimum | Mean | Maximum |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 0 | 20 | 20 | 0 | 179.724 ms | 772.181 ms | 1,318.105 ms |

The increased latency versus the channel-2-only burst is end-to-end
cross-characteristic coexistence/contended-link evidence on retail
`2.2.8.0002`; CoreBluetooth cannot separate host write queuing, radio
scheduling, and firmware processing in that number.
No channel-1 acknowledgment was observed on the phone-role connection; the
probe did not select the documented fatal-risk glasses-role branch merely to
force a reply. This run therefore proves that twenty host-issued bounded
channel-1 writes did not prevent channel-2 response continuity, but not that
every unacknowledged channel-1 write reached the firmware, nor channel-1 TX
saturation, raw HVN counts, or source-built behavior. A clean reconnect
immediately afterward completed three
of three sequential status requests with zero loss at 44.877...102.975 ms
(70.006-ms mean), confirming normal post-test recovery.

## Deployment decision

The owner-authorized ACE campaign subsequently closed the backup gate: every
live page at `0x27000..<0xFF000`, the complete architected 0x308-byte UICR
extent, source-proven MBR words, and the CRC-valid settings mirror now form a
verified one-MiB recovery basis. The final-v11 deployment package additionally
classifies the live settings store as two exact Nordic FDS data pages plus one
swap page, retains their rollback bytes, clears them for fresh Zephyr NVS,
imports no retail credentials, and requires owner re-pairing. It proves the
full install model, preserved product region, erased settings/legacy executable
regions, byte-identical UICR, and exact internal-flash/UICR recovery images.
The bundle manifest records 233,586 linked RAM bytes, 28,558 bytes of
headroom, and a verifier-enforced 16-KiB minimum so future packaging fails
before a linked-layout regression can consume the required margin.
The rebuilt owner-authorization core also reconstructs the exact persisted
owner after reboot and evicts a previously loaded RAM identity if a later
settings load is malformed. Mutation, truncation, revocation, and stale-state
tests are source-host evidence only; power-cut and rollback replay behavior on
the physical NVS backend remains unvalidated.

The complete first-install gate remains open. The owner-authorized BLE
transition did perform the temporary bootloader flash described above, but it
did not reach the source-boot staging or page-zero copy. A pinned pyOCD 0.45.1
runtime and the fail-closed SWD executor are available; no debug probe is
currently enumerated. The next evidence-producing action is either recovery of
B56EE2 through power/SWD or installation of the corrected transition on a
separate explicitly identified sacrificial R1, followed by source recovery,
application upload, and post-install functional validation. Mass erase remains
forbidden because the exact recovery basis preserves product data and UICR.

## Reproduction

```sh
make -C r1 build/r1_ble_probe_frames
xcrun swiftc -warnings-as-errors -framework CoreBluetooth -framework Foundation \
  r1/tools/probe_r1_ble.swift -o /tmp/openr1_ble_probe
/tmp/openr1_ble_probe --timeout 180 --pair-role-phone --device-info B56EE2
/tmp/openr1_ble_probe --timeout 180 --pair-role-phone \
  --status-count 20 --status-burst B56EE2
/tmp/openr1_ble_probe --timeout 180 --advertisement-samples 6 B56EE2
/tmp/openr1_ble_probe --timeout 180 --cccd-cycle --pair-role-phone \
  --status-count 3 --status-interval-ms 250 B56EE2
/tmp/openr1_ble_probe --timeout 180 --pair-role-phone --status-count 20 \
  --status-burst --disconnect-after-ms 100 B56EE2
/tmp/openr1_ble_probe --timeout 180 --status-count 1 \
  --expect-status-silence-ms 3000 B56EE2
/tmp/openr1_ble_probe --timeout 180 --pair-role-phone --status-count 20 \
  --status-burst --channel1-probe-count 20 B56EE2
python3 r1/tools/analyze_r1_hci_capture.py trace.pklg \
  --expect-sha256 EXACT_CAPTURE_SHA256 \
  --channel2-write-handle 0x15 --channel2-notify-handle 0x17 \
  --require hci --require mtu --require data-length --require phy \
  --require encryption --require completed-packets \
  --require queued-write-rejection --require channel2-traffic
```
