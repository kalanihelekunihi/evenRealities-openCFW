# August 18 physical-validation blocker

## Continuation update: recovery evidence and source recovery are complete

This section supersedes the earlier backup/key statements retained below as a
chronology of the first audit. Owner-authorized ACE reads subsequently captured
all 216 exact live 4-KiB pages at `0x27000..<0xFF000` and the complete live
0x308-byte architected UICR extent. The accepted mixed-provenance 1-MiB
recovery basis is explicit about the pinned official reconstruction below
`0x27000`, source-proven MBR words, live pages, and the CRC-valid settings-page
mirror. The live application and owner bootloader matched their authenticated
reference images byte-for-byte. `prepare_zephyr_deployment.py` accepts that
evidence and emits the exact install/readback/recovery plan.

An owner-controlled P-256 key is now configured through macOS Keychain and the
owner bundle verifies with `development_key: false`. Its 156-KiB source-built
boot partition contains a 121,492-byte BLE recovery loader; the application is
642,871 signed bytes in the `0x27000..<0xD1000` application partition. The loader accepts bounded
sequential application writes, resumes after disconnect, never writes its own
partition or product data, and relies on MCUboot's owner signature before
execution. The install contract erases `0..<0xD1000` and the former retail
settings pages `0xD1000..<0xD4000` plus the former retail bootloader/settings
window `0xF8000..<0x100000`, preserving only product data at
`0xD4000..<0xF8000`. Preflight recognizes the live settings layout as exactly
two Nordic FDS data pages and one swap page, retains their page-exact recovery
copy, rejects unknown/torn layouts, and requires fresh owner pairing rather
than importing retail credentials into Zephyr NVS.

The remaining first-install blocker is narrower but fundamental: replacing
nRF52840 page zero over BLE requires erasing the only reset vector/MBR before
the replacement can be made durable. Neither the SoC nor the retail Secure DFU
bootloader provides immutable ROM recovery if power or radio is lost in that
window. A staged copier can reduce the window but cannot make it recoverable.
No SWD/debug probe is attached, so the first opaque-free installation has not
been attempted. Attach an SWD/J-Link-class path for the initial program and
exact readback; after that one transition, application recovery is available
over the source-built BLE loader.

## Decision

Owner-authorized BLE evidence is now available and is recorded in
[`AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md`](AUGUST-18-R1-B56EE2-HARDWARE-VALIDATION.md).
It closes discovery, GATT-layout, role-response, retained-bond, read-only
channel-2 timing, and bounded status-burst questions on retail application
`2.2.8.0002` / hardware `603MV1.9.3`. This is not a functional-completeness
claim: the analyzed application is `2.2.6.0009`, the source-built image has not
been installed, and no debug/read-back path is present. The current
capability ledger contains 97 rows: 52 implemented, 40 partial, two withheld,
two separate deployment rows, and one excluded fixture. All 3,326 inventoried
functions are source-gated and the source-built MCUboot/Zephyr bundle contains
no S140, retail bootloader, or opaque executable member.

Every remaining partial row already names a compiled source implementation and
an acceptance criterion that depends on an owned R1, authorized debug access,
physical instrumentation, reference measurements, or persistent-state evidence.
The two withheld rows additionally require a licensing/key-custody or explicit
product-policy decision. Guessing those inputs, enabling destructive commands,
or treating host simulation as physical proof would weaken rather than complete
the firmware.

## Evidence now available

The owned ring physically confirmed:

- connectable `EVEN R1_B56EE2` advertising with company identifier `0x5245`;
- the exact BAE8 four-characteristic GATT layout and Nordic Secure DFU control
  point;
- `pairAuth` success, asynchronous role/status notifications, and a retained
  macOS My Devices relationship across reconnects;
- the read-only application/hardware identity `2.2.8.0002` / `603MV1.9.3`;
- three sequential status replies at 37.975...69.351 ms with zero loss; and
- twenty queued status replies at 59.740...478.024 ms with zero loss;
- channel-2 CCCD disable/re-enable followed by three successful replies;
- intentional disconnect after four of twenty queued replies, immediate
  advertising recovery, retained-bond reconnect, and three successful replies;
- retained-bond status silence without `pairAuth`, confirming transport and
  application-role separation; and
- coalesced CoreBluetooth advertisement observations, explicitly insufficient
  to claim the actual radio interval.

The probe and its C-generated fixed frame vectors are checked in under
`tools/probe_r1_ble.swift` and `tools/r1_ble_probe_frames.c`.

## Evidence still unavailable in this workspace

The blocking audit on 2026-08-18 found:

- no R1 serial/debug endpoint; the BLE GATT surface has no flash/UICR read-back
  operation, and only macOS `/dev/cu.Bluetooth-Incoming-Port` and
  `/dev/cu.debug-console` exist;
- no enumerated USB J-Link, Nordic, CMSIS-DAP, or other debug probe;
- no `nrfjprog`, `JLinkExe`, `pyocd`, `openocd`, or `probe-rs` executable;
- no captured one-MiB internal-flash backup, separate 4-KiB UICR backup,
  deployment plan, post-install readback, or post-recovery readback;
- no raw HCI/ATT capture, logic-analyzer capture, calibrated sensor trace,
  electrical rail measurement, or synchronized biometric reference dataset;
  CoreBluetooth observations alone cannot expose HVN-completion counts,
  negotiated interval/PHY, keys, or source-built scheduler ticks; and
- no owner production signing key configured for this bundle, algorithm-key license/custody authorization,
  NFC activation policy, private-diagnostic export consent/redaction policy, or
  normal-protocol OTA/power-control authorization.

The checked-in `rebuilt-uicr.bin` is reconstruction evidence, not an owned
device's UICR backup, and cannot satisfy deployment recovery requirements.

### Repeated external-state audit

After completing the owned-ring discovery, pairing, channel-2 timing, burst,
CCCD, disconnect/reconnect, and application-role separation campaign, the
deployment prerequisite was checked again across three consecutive goal turns.
The final audit still found:

- no USB J-Link, Nordic debugger, CMSIS-DAP, DAPLink, Black Magic, or ST-Link
  interface in either `system_profiler` or the macOS IORegistry;
- no `nrfjprog`, `JLinkExe`, `JLinkGDBServer`, `pyocd`, `openocd`, `probe-rs`,
  `cargo-embed`, `nrfutil`, or `adafruit-nrfutil` executable;
- no R1 serial endpoint beyond the generic macOS Bluetooth/debug-console
  devices; and
- no owned-device one-MiB internal-flash or 4-KiB UICR backup artifact.

The standard `FE59` Secure DFU control point remains install-only and cannot
replace either read-back. All safe CoreBluetooth validation available through
the fixed, non-generic probe has been completed. Further progress now requires
an external debug/read-back state change; entering DFU would not remove this
blocker and was not attempted.

## Residual acceptance map

| Ledger area | Rows still partial | External evidence required |
| --- | ---: | --- |
| Platform | 7 | boot/RAM negotiation, scheduler saturation, advertising/MTU captures, bus timing, and YHM/software-I2C electrical traces |
| Protocol | 3 | later-revision BAE8/status timing, bounded burst, CCCD cycle, and intentional disconnect/reconnect are captured; exact-version/source-built HVN counts, channel-1/channel-2 interference, resource retry, and raw-tick timing remain |
| Security | 3 | later-revision pairing, retained macOS bond, reconnect, and bond-versus-application-role separation are captured; raw HCI encryption, queued-write rejection, repair/replay, source-built owner revocation across reboot, and authorized NV-recovery adoption remain |
| System | 4 | two-target advertising lifecycle, REG1/radio coexistence, owner-authorized OTA recovery versus withheld advertising/power controls, and retained fault/reset behavior |
| Storage | 4 | the deterministic retail-FDS reset policy is software-closed; physical first-boot, power-cut, endurance, reboot, and rollback evidence for NVS, KV, FlashDB, sleep, and prior state remains |
| Sensors | 9 | installed-part identity, axes/channels, transfer functions, calibration, rail timing, optical frames, touch geometry, and continuous production |
| Hardware services | 2 | dock/NFC activation, mailbox/GPO behavior, TWIM handoff, and shared-rail coexistence |
| Health | 8 | synchronized physical inputs and reference outputs for HR, SpO2, HRV, activity, temperature, stress, retained recovery, and database lifecycle |

These 40 rows and their exact implementation/gate text remain authoritative in
`docs/reference/COVERAGE.csv`; the grouped rationale is maintained in
`docs/reference/RESIDUAL-PROVIDER-AUDIT.md`.

The withheld rows are:

1. algorithm-key provisioning, pending license, owner key custody, durable
   verification, and recovery policy;
2. the private structured-log BLE sender, pending physical ATT behavior plus
   identity/health/diagnostic consent and redaction policy. Its bounded
   owner-authorized virtual-file source is already implemented internally.

Advertising and power controls remain partial under the combined OTA/power
row; `otaStart` itself is now narrowly owner-authorized and recoverable.

The two separate boot/deployment rows now require the physical
install/boot/rollback/recovery campaign; owner P-256 custody is configured. The synthetic health-daily
fixture remains deliberately excluded because it has no recovered production
caller.

## Safe resume prerequisites

Work may resume when the owner supplies or connects, at minimum:

1. the owned R1 plus an authorized SWD probe/debug path capable of bounded
   internal-flash programming and exact flash/UICR read-back;
2. BLE capture capability plus radio, logic, power, and sensor-reference
   instrumentation appropriate to the row being validated; and
3. explicit decisions for algorithm keys, NFC activation, private diagnostic
   export, and advertising/power controls before any corresponding live surface is
   enabled.

The backup/preflight action is complete. The next hardware action must be an
SWD-backed, sector-bounded first installation with exact full-flash and UICR
readback; mass erase remains forbidden.

## Last verified artifact

`build/openr1-zephyr/openr1-source-built-ble-recovery-owner.zip`

- ZIP SHA-256:
  `9d518d0a0a1f748796d591fd561638204e9ac75a59fc7fd98a2b226bd7ccae49`
- source boot/recovery: 121,492 bytes (76.05% of 156 KiB)
- signed application: 642,871 bytes, SHA-256
  `2e4727fde3817c1494a16bf0c9e93dc8417c513c9cf16fb0d40f830b4c6292e5`
- full-flash HEX SHA-256:
  `56072380e98c12f2b13a1b44ec4005e49f5ab05165e0bc0291705d9ae6a92aff`
- owner public-key SHA-256:
  `1a2cc402e13ec04d33efa3535d72c33a76da83a8bf6d593bc6c1df83c2a20f5d`
- source inventory: 174 files, all byte-matched by the bundle verifier
- final offline deployment plan `deployment-preflight-ble-recovery-owner-final-v11`
  SHA-256:
  `1e76d5e5fcf04bb6615856c46d3f949ef4949d2c7c99ee6ef33c7f4b35fc177c`

The v11 plan records the live settings store as two exact FDS data pages and
one swap page, resets all three for fresh Zephyr NVS, preserves only product
data, imports no retail credentials, and requires owner re-pairing.
The rebuilt application also fail-closes malformed owner-setting reloads by
evicting any previously loaded RAM identity; host tests cover exact reboot
reconstruction, every one-bit record mutation, every truncation, revocation,
and stale-state eviction. Physical NVS interruption and rollback replay remain
open hardware gates.

The final linked application uses 642,720 bytes of flash and 233,586 bytes of
RAM. Packing dispatch results into the exact 50-fragment arena reduced RAM from
97.92% to 89.11% without reducing the 32-response, 1,100-byte model, or
50-fragment limits. The remaining 28,558-byte margin still requires physical
stack-high-water and saturation validation; it is not evidence of runtime
stability by itself. The bundle now records that linked extent in its manifest,
and both packaging and independent verification reject less than 16 KiB of
headroom.
