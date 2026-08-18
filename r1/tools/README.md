# R1 tools

The R1 evidence toolchain: the scripts that pin recovered behavior to the stock
image, the models that check it, and the gates that keep the documentation
honest.

## Entry points

| Script | What it does |
| --- | --- |
| [`verify_openr1.py`](verify_openr1.py) | **the gate** — capability ledger, source ownership, every subsystem summary, and the host/sanitizer/ARM builds. `make -C r1 verify` |
| [`build_r1_source_ownership.py`](build_r1_source_ownership.py) | regenerate the function-ownership records; `--check` fails if they are stale |
| [`verify_r1_decompilation.py`](verify_r1_decompilation.py) | authenticate the decompilation corpus |
| [`verify_r1_bootloader_reconstruction.py`](verify_r1_bootloader_reconstruction.py) | authenticate the bootloader reconstruction |
| [`verify_sdk_image.py`](verify_sdk_image.py) | check a built nRF52840 image against the recovered layout |
| [`prepare_zephyr_deployment.py`](prepare_zephyr_deployment.py) | verify the source-built bundle against a required 1-MiB internal-flash recovery basis and complete 0x308-byte architected nRF52840 UICR backup, validate optional mixed-provenance evidence page-by-page, hash every preserved product partition, and emit separate canonical recovery HEX files, an exact expected post-install image, and a deployment plan; it never accesses or flashes hardware |
| [`verify_zephyr_deployment.py`](verify_zephyr_deployment.py) | independently reconstruct the install result and require exact internal-flash and UICR readbacks after installation and optional recovery |
| [`assemble_r1_ace_recovery.py`](assemble_r1_ace_recovery.py) | assemble a one-MiB recovery basis from exact-version live ACE page reads at `0x27000..<0xFF000`, source-proven MBR words at `0xFF8..<0x1000`, a source-proven mirror of the ACL-protected primary settings page from the CRC-valid live backup, and the pinned official S140 7.2.0 image for the remaining retail memory-isolated extent; verify the live application and owner bootloader byte-for-byte and emit explicit mixed-provenance JSON |
| [`r1_ble_probe_frames.c`](r1_ble_probe_frames.c) | generate the three fixed, non-destructive channel-2 frames used by the macOS hardware probe through the production C encoder |
| [`probe_r1_ble.swift`](probe_r1_ble.swift) | macOS CoreBluetooth discovery and bounded owned-hardware validation for GATT layout, advertisement host-observation cadence, CCCD cycling, `pairAuth`, application-route silence without `pairAuth`, `deviceInfo`, sequential/burst status timing, and intentional disconnect recovery; startup self-tests require byte identity with the C vectors |
| [`upload_zephyr_recovery.py`](upload_zephyr_recovery.py) | verify a source-built bundle, refuse development trust by default, extract only its signed application to a mode-0600 temporary file, compile the bounded CoreBluetooth client, and upload/resume through `OPENR1-RECOVERY`; it cannot write the bootloader or product storage |
| [`upload_openr1_recovery.swift`](upload_openr1_recovery.swift) | sequential offset-checked recovery transport used by the verified wrapper; reads the loader status to resume after disconnect and finishes only after all declared bytes are acknowledged |
| [`r1_macos_ace_read.swift`](r1_macos_ace_read.swift) | exact-version, read-only macOS ACE client for one bounded prefix, one 4-KiB internal-flash page, or the complete architected 0x308-byte UICR extent on an owner-authorized R1; every mode is address-constrained and contains no NVMC write operation |
| [`export_r1_decompilation.py`](export_r1_decompilation.py) | regenerate the decompilation corpus |
| `run_r1_*.sh` | headless-Ghidra drivers for decompilation and BSim correlation |
| [`openr1_sim.c`](openr1_sim.c) | the host protocol/device simulator (`make -C r1 sim`) |

## `evidence/` — 197 scripts

Where a claim comes from. Each one reads the reconstructed image, proves
something about one subsystem, and emits pinned JSON that a correlation document
quotes.

| Family | Count | Purpose |
| --- | ---: | --- |
| `summarize_r1_*` | ~150 | pin one subsystem: exact addresses, sizes, record layouts, provider edges |
| `emulate_r1_*` | ~45 | executable models of recovered behavior, used as oracles |
| `analyze_r1_*`, `build_r1_227_*` | 2 | cross-cutting analysis and probe construction |

They import each other by bare module name, so they live in one directory. The
entry points above put `evidence/` on `sys.path`; running a script directly
works because Python adds its own directory.

Every correlation document ends with the command that regenerates its numbers:

```sh
cd r1 && python3 tools/evidence/summarize_r1_bae8_event_router.py
```

## `probes/` — 21 assets

On-device runtime probes: Cortex-M assembly (`r1_227_*.S`) that dumps
bootloader, UICR, APPROTECT, NFCT, and ST25 state from a running device, plus
one DFU decode audit in C. These are inputs to physical validation, not part of
any build.

## `ghidra_scripts/` — 53 scripts

Ghidra headless scripts for the nRF52840 target: function seeding, boundary and
callsite evidence, BSim comparison, and whole-image export.

## Prerequisites

Everything here needs the reconstructed images, built from byte arrays you
supply locally:

```sh
make -C r1/research/decompilation/rebuild verify
```

See [`../research/decompilation/rebuild/PROVENANCE.md`](../research/decompilation/rebuild/PROVENANCE.md).
The R1 firmware itself builds and passes its full test suite without them.

The BLE probe is deliberately not a generic write console. Discovery is the
default; its only transmitting modes are the recovered ephemeral phone-role
selector and fixed read-only device-info/status requests. It redacts the
manufacturer payload by default, validates both wire checksums on every model,
and contains no DFU, power, advertising, storage, sensor-control, or raw-command
operation. Advertisement callback gaps are labeled host observations because
CoreBluetooth coalesces radio events. The disconnect option requires the
fixed status-only burst and performs a normal central disconnect. Build and run
it on macOS with:

```sh
xcrun swiftc -warnings-as-errors -framework CoreBluetooth -framework Foundation \
  r1/tools/probe_r1_ble.swift -o /tmp/openr1_ble_probe
/tmp/openr1_ble_probe --timeout 180 --pair-role-phone --device-info \
  --status-count 20 --status-burst B56EE2
```

## Scope

This is a firmware repository. Scripts that audited the companion phone
application — its decompiled Dart AOT and Swift protocol controllers — are not
here: they analyze a different product and cannot run against this tree. The
firmware-side evidence they cross-checked is covered by the correlation records
under [`../docs/correlation/`](../docs/correlation).

The read-only ACE evidence client is included here so physical recovery evidence
does not depend on a separate checkout. Bootloader rekeying remains outside this
firmware repository; it is unnecessary when the reviewed owner-optional
bootloader is already installed.

Compile the ACE reader on macOS with `-parse-as-library` and always supply the
reported firmware version plus the exact cached CoreBluetooth UUID:

```sh
xcrun swiftc -parse-as-library -warnings-as-errors \
  -framework CoreBluetooth -framework Foundation \
  r1/tools/r1_macos_ace_read.swift -o /tmp/r1-macos-ace-read
/tmp/r1-macos-ace-read --identifier DEVICE-UUID \
  --firmware-version 2.2.8.0002 --address 0x27000 --page \
  --output /tmp/r1-27000.bin
```
