# G2 2.2.6.0 hardware validation and recovery handoff

Date: 2026-08-23 (America/Chicago)

> Historical record: the current hardware-qualification status is superseded by
> [`hardware-validation-policy.md`](hardware-validation-policy.md). This report is
> retained unchanged below as chronology, not as the present device-health premise.

## Authorized hardware

- Glasses serial: `S211GBBC180304`
- Left temple: `EVEN G2_32_L_4FB39E`, `F0:F1:0C:4F:B3:9E`
- Right temple: `EVEN G2_32_R_1412E0`, `E0:EC:B6:14:12:E0`
- Case USB: `/dev/cu.usbserial-210`, B200 `1.2.57`

No other nearby glasses may be connected to or written.

## Stock baseline

Both authorized temples were first downgraded over exact-name BLE to official
G2 `2.2.6.10`, hardware revision 5. The pinned official package is:

- `SybilSight-WebFlasher/public/firmware-updates/source-files/2.2.6.10/e28738432d7b612d625331b00383149b.bin`
- SHA-256: `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`

## Source-built candidate

The deterministic release command produced:

- `g2/build/release/g2-openCFW-s200_v2.2.6.0-core-source.evenota.bin`
- package version: `s200_v2.2.6.0`
- package bytes: `4,493,456`
- package SHA-256: `755e25c3f1685749918e84c1f0af64cbe1635d5f5a4b73e294cab0a517b8c95b`
- Apollo main bytes: `3,714,962`
- Apollo main SHA-256: `c8275de8f328c3dd86ed74d9ebee4e37aff02c5959e4a56af9305eebd9a592f0`
- Apollo main CRC32C: `0x9AFD9FF9`
- nested Apollo CRC32: `0xE8533FEC`

This artifact passed structural validation and the available offline tests. It
is not hardware-qualified.

Post-failure comparison against stock established that the Cortex-M vector
table, initial stack pointer (`0x2007FB00`), and reset handler (`0x005E4233`)
are unchanged. The candidate nevertheless changes 145,986 bytes in the common
stock-sized portion of Apollo main. Its exact build report recorded 1,118 patch
sites; the retained flash plan independently exposes at least 135 low-level
runtime entry replacements (FreeRTOS, CMSIS-RTOS, RTOS utilities, IAR
memory/runtime, scheduler, kernel, and watchdog code). The current source tree
has since advanced to 1,131 sites and is not hash-bound to the flashed payload;
the qualifier rejects using that newer metadata as if it described the older
artifact. This breadth, rather than the package header or vector table, is the
leading no-boot hypothesis. It remains a hypothesis until the right temple can
be observed under a debugger.

## Staged qualification artifacts

Two narrower `2.2.6.0` rungs now prevent another full-overlay-first test:

1. Stock-code control:
   `g2/build/hardware-validation/g2-stock-code-control-s200_v2.2.6.0.evenota.bin`,
   SHA-256
   `71994df70775d3bd4680d8b79e37330bdcc7fac938e970c31b9a1bc35c79ec6a`.
   Its Apollo payload is the reviewed stock payload byte-for-byte except for
   the nested CRC and the two runtime version fields: eight changed bytes in
   three runs. It is offline-eligible as the recovery/control rung.
2. Minimal source hook:
   `g2/build/hardware-validation/g2-openCFW-s200_v2.2.6.0-minimal-name-hook.evenota.bin`,
   SHA-256
   `4d96a47effbde6ec3029cdaf79dd2b52a1ecaa8af4acaddf24328dd4e8387cdb`.
   It contains one pinned 412-byte C function and one four-byte BL hook for the
   advertised-name suffix, with no critical-runtime patches. Its vector table
   matches stock and it is offline-eligible only after the stock-code control
   boots on the recovered right temple.
3. Earliest critical hook:
   `g2/build/hardware-validation/g2-openCFW-s200_v2.2.6.0-name-memcpy-hook.evenota.bin`,
   SHA-256
   `c0cff1069a6ed9eaa2be61acb532ed2c66125393468e2a2bb983cec766e9a174`.
   It adds only the source-built public IAR `memcpy` provider to rung 2: two
   total patch sites, one critical-runtime site, 564 appended source bytes,
   and a stock-identical vector table. This is the first focused boot-failure
   discriminator and must be attempted only after rungs 1 and 2 boot.

The unchanged startup enters `0x005CE01E`, which immediately delays, calls
`0x005BF0BC`, and only then reaches the first startup log. Function
`0x005BF0BC` calls public `memcpy` at `0x00439BE4` to populate and execute an
initializer table. The flashed full image redirected that call to the
source-built provider, making `memcpy` the earliest observed nontrivial source
replacement on this boot path. This does not prove it caused the failure, but
it makes rung 3 the highest-value single-hook test.

`tools/qualify_hardware_candidate.py` enforces these offline gates and always
rejects a full-source image as a first-stage candidate. The full source image
remains the target, but it must be reached by bisecting hardware-qualified
hook groups rather than installing all 1,131 sites at once.

## Hardware result

The stock case application/product-test route rejected the right-temple START
at the zero-byte boundary. A subsequent exact-address BLE full-package install
to the authorized right temple completed all six components, 1,099 blocks,
with zero resends and an `UPDATING` acknowledgement from every component END.
After reboot, the right application did not return:

- the case still reports the right physical contact present;
- the right application UART returns no complete frame;
- `EVEN G2_32_R_1412E0` no longer advertises;
- a fresh bilateral `DEB0` did not restore right application liveness.

The authorized left temple was not flashed with openCFW and remains on stock
`2.2.6.10`.

## Read-only recovery experiments

The recovery experiments used a separately hash-pinned case-SRAM bridge that
accepts only the exact eight-byte Ambiq Apollo5 wired-update HELLO
`14559de900000800`. It has no data, erase, OTA, or arbitrary-byte command.

1. `right-apollo-sbl-hello.json` stopped before bridge launch because the case
   reset acknowledgement gate reopened the case console and sent `DEB0` while
   B200 was rebooting. No SBL request reached a temple. The regression is fixed
   by performing presence preflight and `DEB0` in one console session.
2. `right-apollo-sbl-hello-attempt2.json` accepted all eight host bytes but an
   inverted validator return rejected the request. Retained SRAM proved
   `temple_tx_count=0`, complete route masks, and byte-identical YHM restoration.
   The validator now returns zero only for the exact HELLO and one for every
   other input.
3. `right-apollo-sbl-hello-attempt3.json` stopped at bridge setup on the
   non-allowlisted post-reset YHM state `810104ffa603c10522ff`. Retained SRAM
   proved a complete ten-register baseline read, zero YHM writes, zero temple
   bytes, and no UART errors. This transient must not be allowlisted.

The normal case application subsequently returned as B200 `1.2.57` and again
reported both physical contacts present. Its logs continue to report no reply
from the right temple.

## Remaining recovery gate

Do not run another case-USB or BLE write attempt. Ambiq's Apollo5 SBL wired
update mode depends on per-device INFOC/INFO0 provisioning. The stock case
cannot read those regions from an application-dead temple, and no SWD/J-Link,
CMSIS-DAP, or other debugger is currently connected.

The next authorized step is read-only debugger acquisition of:

- INFOC: 0x400 bytes beginning at `0x400C2000`
- the selected active INFO0: at least 0x6c bytes beginning at offset zero

Decode the dumps with
`SybilSight-WebFlasher/src/lib/recoveryConfig.js`. Continue only if the dump
proves all of the following for this exact right temple:

- wired UART enabled and mapped to the pogo UART module/pins;
- exact baud, framing, and pin-function words;
- a nonzero wired receive window;
- a usable INFOC boot-override condition or an actual SBL boot error;
- any required MRAM-wired-recovery enablement;
- an image format authorized by the device lifecycle/security configuration.

The decoder now reports `firmwareWriteAuthorized: false` for dump-only input,
even when every known pogo field matches. It records separate blockers for
device-identity binding and a live CRC-correct SBL STATUS frame. This prevents
the UI's positive provisioning match from being mistaken for permission to
write. The WebFlasher test suite passes 391/391 and its production UI build
passes with this gate.

If those checks fail, recovery requires manufacturer service or physical
debug access beyond the connected stock case. Preserve the left temple on
stock `2.2.6.10` and do not use another nearby G2 as a substitute.

## Current protobuf Ring-service evidence block

The production-routed `pb_service_ring.c` software tranche has not been
validated on either authorized temple. Its offline host, target-link,
component, package, and deployment-plan gates are green, but live validation
requires a booting source-divergent temple, a paired Ring peer, observable BLE
service-`0x91` relay traffic, and known nanopb event vectors. The right temple
is application-dead after the earlier full-image experiment, the left temple
must remain on stock, and the recovery gate above prohibits another write.
No authorized live Ring peer or captured physical event evidence is available.

Accordingly, paired-G2 relay, nanopb interoperability, and physical Ring-event
behavior are explicitly blocked by unavailable physical evidence. This block
does not weaken the software closure and must not be reported as hardware
validation or overall firmware completeness.

## Current protobuf glasses-case-service evidence block

The production-routed `pb_service_glasses_case.c` software tranche has passed
its host RX/TX/notify oracle, target selector builds, strict-relocation audit,
component assembly, package, and deployment-plan gates. Physical validation
requires a booting source-divergent temple, the authorized case, a live BLE
service-`0x81` peer exchange, and independently observed battery, charging,
lid, presence, error, and notification-sequence transitions.

That evidence cannot be collected now: the authorized right temple is
application-dead, the left temple must remain on stock `2.2.6.10`, and the
recovery gate prohibits another write without debugger evidence. No equivalent
authorized temple/case capture exists. Service interoperability and physical
case-state behavior are therefore explicitly blocked by unavailable physical
evidence, not validated, and do not establish overall firmware completeness.

## Current protobuf conversate-service evidence block

The production-routed `pb_service_conversate.c` software tranche passes its
host buffer/RX/replay/envelope/role/transport oracle, all eight target selector
builds, 33-relocation audit, component assembly, package, and deployment-plan
gates. Physical validation requires a booting source-divergent authorized
temple, its paired peer, live BLE service-`0x0B` traffic, timing around the
3,000-ms replay boundary, and observable conversate UI state transitions.

That evidence is unavailable: the authorized right temple is application-dead,
the left temple must remain on stock `2.2.6.10`, and the recovery gate forbids
another write without read-only debugger evidence. No equivalent authorized
peer capture exists. Master/peer transport, BLE timing, and UI integration are
therefore explicitly blocked by unavailable physical evidence, not validated,
and do not establish overall firmware completeness.

## Current protobuf teleprompt-service evidence block

The production-routed `pb_service_teleprompt.c` software tranche passes its
host buffer/RX/replay/six-envelope/role/transport oracle, all nine target
selector builds, 39-relocation audit, component assembly, package, and
deployment-plan gates. Physical validation requires a booting
source-divergent authorized temple, its paired peer, live BLE service-6
traffic, timing around the 3,000-ms replay boundary, and observable teleprompt
file-selection, page-request, status, and scroll-synchronization transitions.

That evidence is unavailable: the authorized right temple is
application-dead, the left temple must remain on stock `2.2.6.10`, and the
recovery gate forbids another write without read-only debugger evidence. No
equivalent authorized peer capture exists. Master/peer transport, nanopb
interoperability, BLE timing, and teleprompt UI integration are therefore
explicitly blocked by unavailable physical evidence, not validated, and do
not establish overall firmware completeness.
