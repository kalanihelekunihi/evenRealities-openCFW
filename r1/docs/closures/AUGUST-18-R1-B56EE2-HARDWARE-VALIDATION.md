# August 18 owned-R1 BLE validation

## Continuation status

After the read-only campaign below, the owner-authorized ACE path captured all
216 live flash pages at `0x27000..<0xFF000` plus the exact 0x308-byte UICR
extent. Those records now pass the page-by-page mixed-provenance recovery-basis
and offline deployment verifiers. The owner-signed source build also now
contains a source-built `OPENR1-RECOVERY` GATT loader below slot 0, so later
application interruption is recoverable without the retail bootloader.

The ring was observed advertising again on the same CoreBluetooth UUID after
the build work. No firmware mutation has occurred. A BLE-only first install is
still withheld because replacement of page zero has an unavoidable
nonrecoverable power-loss window without SWD. This is distinct from the now
closed backup, owner-key, and subsequent-update recovery gaps.

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
role selector, and fixed read-only `deviceInfo` and `deviceStatus` requests.
No arbitrary write interface exists in the probe. No DFU, advertising-control,
power, storage, sensor-control, factory/eAT, NFC, or flash operation was sent.

The checked-in C utility generates the three allowed frames through
`r1_model_encode` and `r1_fragment_message`. The Swift transport refuses to
start unless its independently implemented framing is byte-identical to those
C vectors. Every received model is accepted only after the non-reflected outer
Castagnoli CRC, declared length, and direction-specific inner MODBUS CRC pass.
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
channel-1 interference, raw HVN completion counts, or the four-slot Zephyr
notification pool because the source-built image was not installed.

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

## Channel-1 decision

No channel-1 diagnostic command was sent. The repository records a demonstrated
244-to-36-byte channel-1 parser overwrite on retail `2.2.7.0005`; the available
ring runs `2.2.8.0002`, for which no authenticated image or proof of repair is
available. Exercising even an intended read-only command on a primary device
without flash/UICR recovery would not meet the project's safety boundary.

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

The first-install gate nevertheless remains closed. No debug probe enumerates,
and none of `nrfjprog`, `JLinkExe`, `pyocd`, `openocd`, or `probe-rs` is
installed. ACE executes through the retail application and cannot remain alive
after page zero is erased. Nordic Secure DFU can update its signed application
slot but cannot atomically replace the MBR/retail boot chain with the
source-built boot partition. A BLE-only page-zero transition therefore has an
unavoidable nonrecoverable power/radio-loss interval. No flash or erase was
attempted; the next permitted installation is sector-bounded SWD programming
followed by exact one-MiB and UICR readback, with mass erase forbidden.

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
```
