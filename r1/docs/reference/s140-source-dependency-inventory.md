# R1 Nordic S140 and MBR source dependency, 2026-11-11

The strict C links cover the application and Secure DFU bootloader, but they
still call the pinned Nordic S140/MBR binary through supervisor calls. This
is a separate whole-device source-completeness boundary. The sparse
[source-region HEX](source-region-hex-review.md) deliberately excludes that
binary.

An instruction inventory of the current linked ELFs finds **74 SVC sites in
the application** and **35 in the bootloader**. Together they use 55 distinct
SVC numbers. The two `SVC 0` sites are the DFU service interface and FreeRTOS
first-task start; the other 54 numbers map to these SDK header enums:

| Interface | Distinct SVC numbers | Numbers |
| --- | ---: | --- |
| BLE common, GAP, GATTC and GATTS | 41 | 96, 97, 98, 100, 101, 102, 103, 105, 108, 109, 114–122, 124–127, 134, 143, 144, 147, 160, 161, 165, 168, 170, 173–181 |
| SoC flash, power, clock, event and ECB | 9 | 40, 41, 51, 60, 61, 63, 65, 70, 75 |
| SoftDevice manager | 3 | 16, 17, 19 |
| Master Boot Record | 1 | 24 |

The application uses 53 distinct numbers, including `SVC 0`; the bootloader
uses 34. Their union adds bootloader-only numbers 24 and 108 to the
application set. The full site-to-function and SDK enum mapping is in the
ignored receipts `build/r1-s140-svc-inventory-20261111/inventory.json` and
`bootloader-inventory.json`. These were extracted from application ELF
SHA-256 `60370c8c7dccfbc7ee9e0e5cb32e4b1250ec9da22d38154170cc24e29c7c2cf8`
and bootloader ELF SHA-256
`113d7c6ce6ce53ff05ffdafb673c1f3e6ce004512abe45d811cde30822c2b70a`.
The enum names come from the pinned nRF5 SDK S140 headers, including
`ble_ranges.h`, `ble.h`, `ble_gap.h`, `ble_gattc.h`, `ble_gatts.h`,
`nrf_soc.h`, `nrf_sdm.h` and `nrf52/nrf_mbr.h`.

This is a static instruction inventory, not a reachability claim or an
implementation plan. A replacement built from C would also need the
underlying BLE radio, scheduling, flash, security and interrupt behavior;
matching SVC numbers alone would not make the existing application work.
The current SDK supplies declarations and SVC wrappers, not S140/MBR C
implementation. The application and bootloader source links remain valid,
but an entirely C-built, installable R1 image is not established.
The [normal-function probe](s140-normal-function-surface.md) compiles the
current linked R1 callers against ordinary C declarations and lists the 62
distinct source implementation interfaces required across both payloads.
Subsequent source C providers reduce that union to 49 unresolved `sd_*`
interfaces in the current normal-function build. The separate
[Cordio RTC integration](cordio-nrf52840-source-candidate.md) compiles with
the R1 application, resolves the shared RTC1 IRQ, and uses the pinned Nordic
clock driver's direct nrfx path, but does not implement the BLE, flash or
MBR services behind those calls.
The pinned Cordio [nRF52840 source candidate](cordio-nrf52840-source-candidate.md)
builds as a standalone BLE sample. Its 236 C units also compile and compose
with the R1 application in an opt-in manifest variant. The Nordic API bridge,
runtime bootstrap and source-only final image remain incomplete.

## 2026-11-12 source profile update

The opt-in Cordio RTC0 profile has since closed the **application** normal
function imports. The strict receipt at
`build/r1-cordio-flash-lifetime-strict-20261112/report.json` links a
source-built lower Cordio region and upper application region with zero
undefined references and no archive members. This does not replace the
first 4 KiB MBR or prove runtime BLE and flash behavior. The same
normal-function source build still leaves bootloader Nordic/MBR services
unresolved, including `sd_mbr_command` and its BLE transport calls.
The default stock-profile application and bootloader continue to link at
`build/r1-default-converged-strict-20261112/report.json` and
`build/r1-boot-default-converged-strict-20261112/report.json`, respectively;
those builds still depend on stock S140/MBR behavior at runtime.
