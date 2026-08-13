# G2 product BLE startup recovery

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Bounded surface

The stock startup boundary contains twelve product BLE bodies and one
interposed Apollo510 vector body. They total 3,236 code bytes; concatenating
the thirteen exact bodies in address order gives SHA-256
`60845b967cc5c6fb4c87f827d863defa45504ff642966e07aad9e2f4a284c025`.
The mixed physical interval `[0x004B7478,0x004B8122)` is 3,242 bytes, SHA-256
`1c36c8ffbc29b94e18b2a4f1804c30ac5389805a4833bb3c9e5d4b48bc0d7090`.
Its only non-body bytes are the six-byte product callback island at
`[0x004B7F5E,0x004B7F64)`.

| Body | Interval | Bytes | SHA-256 | Ownership |
|---|---:|---:|---|---|
| inferred `bleSubsystemInit` | `[0x004B7478,0x004B748C)` | 20 | `b529b3076887949ac84df08976923e9d53df48b66764981aa23f67f24c82cace` | product `app_ble.c` |
| inferred `bleDmCback` | `[0x004B748C,0x004B74F0)` | 100 | `c42104d9fbd403f96a82c1e9f9b06567474c3f5f95a45d7abcacc8b6d4734b48` | product `app_ble.c` |
| inferred `bleAttCback` | `[0x004B74F0,0x004B7532)` | 66 | `eea170364368727843c726dac5496fa6df1f525b7cca74734b7409ae112f3b64` | product `app_ble.c` |
| inferred `bleCccCback` | `[0x004B7532,0x004B758A)` | 88 | `dec2c7a12b6b88b99305d465897833e214e6e9d0cf5e741c8ba0500725645ddc` | product `app_ble.c` |
| inferred `bleDelayedStartCback` | `[0x004B758A,0x004B75CE)` | 68 | `46b02a8b71ff48612cfb06ac374699765f76bd268c35c342e3f2276a55cfed0a` | product `app_ble.c` |
| inferred `bleProcMsg` | `[0x004B75CE,0x004B7D32)` | 1,892 | `290c49050b08712613a10833f5324507a57545cf3e0e353210d0adb0a41d1580` | product `app_ble.c` |
| `_bleCommHandler` | `[0x004B7D32,0x004B7E74)` | 322 | `e96438d98f7a3156379eff4a0754c7bdb412e5d1daf23b0e0e99355c6dc260df` | product `app_ble.c` |
| inferred `bleCommHandlerInit` | `[0x004B7E74,0x004B7EC2)` | 78 | `a88d973c00cd747ae07c0b1a69183efa88d11236ad10033bd971ed30007f722b` | product `app_ble.c` |
| inferred `bleStackRegister` | `[0x004B7EC2,0x004B7F5E)` | 156 | `8144beef1f6329ae2b67117d2ce3ecc81e09a9764a7770fa7b5f8a19e3896c0d` | product `app_ble.c` |
| `_bleExactleStackInit` | `[0x004B7F64,0x004B80BE)` | 346 | `74c187e6005693748a5b71bea5ec6f2e53a5e10d11a6eb01c3b880a8f384e5de` | product `app_ble.c` |
| `GPIO0_607F_IRQHandler` | `[0x004B80BE,0x004B80EA)` | 44 | `853386f3b04b6575390704f2a8a5defabe043bcf472e4dc6487b83ca973ae685` | Apollo510 vector/HAL |
| inferred `APP_BleAddressGet` | `[0x004B80EA,0x004B80F0)` | 6 | `e0d2205ad9c05970be9337ba53e6c455f19c88ae85c20cbfae1d5a4188d83fbd` | product `app_ble.c` |
| inferred `appBleStart` | `[0x004B80F0,0x004B8122)` | 50 | `ece886f3aa5074e050e6949a234dd80215ebf46126d5ef5d78690e6fc19d8faa` | product `app_ble.c` |

`_bleCommHandler` and `_bleExactleStackInit` have exact retained names. The
other product names are conservative semantic labels derived from their
registration and callback ABIs. The retained path is
`D:\01_workspace\s200_ap510b_iar_git\platform\ble\app_ble.c`; the GPIO body
is not assigned to that source file. Consequently, the enclosing address
range is not modeled as one exclusively owned `app_ble.c` translation unit.
The product cluster begins immediately after the closed `dm_conn.c` pool and
the next unrelated body begins at `0x004B8122`, which closes both ends.

Nine direct calls enter exact body starts and the thirteen bodies issue 267
direct calls. Seven stored entries root the vector, DM/ATT/CCC callbacks,
delayed callback, and WSF handler. Two odd-address raw byte windows in unrelated
packed data happen to equal body-interior addresses; both are explicitly
rejected as unaligned non-pointers. Exhaustive BL and wide-branch scans find
no strict-interior ingress.

## Product handler and registration

The prefix supplies the callbacks registered later in the object.
`bleDmCback` uses `DmSizeOfEvt`, preserves the variable-length data of event
`0x26`, and posts the copy to the product WSF handler. `bleAttCback` copies the
fixed ATT event plus its value payload. `bleCccCback` updates product
connection state before posting its ten-byte event. The delayed callback posts
product event `0xBC`; allocation failure changes its rearm delay from 10 to
20 seconds. `bleProcMsg` is the downstream product DM/ATT/profile state
machine, while `bleSubsystemInit` initializes four product managers.

`bleCommHandlerInit` stores the WSF handler ID at product control block
`0x200727F0 + 0x56`, changes `pSmpCfg` at `0x200004B8` to the already-audited
runtime configuration `0x00774D44`, installs another product application
configuration pointer, and initializes three application-framework branches.

`bleStackRegister` installs the product DM callback, connection client 3,
ATT and connection callbacks, and the six-entry CCC set at `0x007518C0`. It
then registers discovery/profile callbacks and initializes the active product
service groups. `_bleCommHandler` is the registered WSF callback. It forwards
ATT events to discovery/server processing, routes DM messages through the
product/application frameworks, and contains the product ring-connection
suppression for advertising-stop processing. Retained diagnostics identify
the exact function name and source lines 651 and 666.

## Stack construction and startup order

`_bleExactleStackInit` initializes WSF OS and timers, then calls
`WsfBufInit(0x2940, 0x2004FA98, 4, 0x200003B0)`. The 10,560-byte pool and its
four descriptors are already independently bounded by the WSF buffer/message
audit; this recovery records the startup call site without claiming duplicate
ownership. A shortfall logs retained line 781 from `_bleExactleStackInit`.

The function then initializes security and installs eight WSF handlers in
this order:

1. HCI
2. DM
3. L2CAP
4. ATT
5. SMP
6. application
7. product BLE
8. HCI driver

Between those handler allocations it initializes the active Cordio
components: HCI, advertising, scanning, PHY, master/slave connection,
security/LESC/privacy, L2CAP master/slave, ATT client/server, SMP initiator and
responder, and the product application. `HciSetMaxRxAclLen(251)` pins the host
ACL receive limit. This call topology agrees with the separately bounded DM,
ATT, SMP, L2CAP, HCI, and WSF objects; it does not by itself transfer their
ownership to `app_ble.c`.

The inferred startup wrapper first runs a product CCB initializer, shuts the
radio down, delays 100 microseconds, boots radio mode zero, initializes the
Cordio stack, registers the product BLE application/profile, and requests
`DmDevReset`. It finally schedules callback `0x004B758B` after 10,000 ms. Its
sole direct caller is the system-start wrapper at `0x004D0A68`; the surrounding
system task subsequently dispatches WSF.

The six-byte getter returns SRAM `0x200737BF`. Three direct callers use it;
one formats exactly six octets as a BLE address, which closes the inferred
object extent and purpose.

## Clean-room candidate coverage

Four independently authored GPL-3.0-only files now represent all twelve
product bodies, totaling 3,192 of 3,192 product code bytes (100%).
`app_ble_callbacks.c` covers subsystem initialization, DM/ATT/CCC event-copy
callbacks, and delayed startup. `app_ble_startup.c` covers handler/runtime
configuration, stack registration, complete Cordio/WSF construction order,
the address getter, and the startup wrapper. `app_ble_handler.c` covers the
registered WSF handler's ATT/DM range dispatch, connection-role routing,
ring-connection advertising-stop suppression, recovered product-processor
handoff, and two downstream application frameworks. `app_ble_processor.c`
covers the complete `bleProcMsg` event switch, connection/CCC teardown,
notification mapping, security forwarding, reconnect backoff, tick state, and
delayed-start control path.

The candidate uses address-pinned injectable provider seams rather than
copying unavailable product source. Its host fixture verifies variable DM and
ATT payload relocation, CCC update gating, 10/20-second delayed-start paths,
all runtime configuration writes, the complete registration sequence, eight
handler allocations, buffer-pool arguments, security/DM/L2CAP/ATT/SMP
construction order, ACL length 251, address access, radio startup, and all
registered-handler routing branches. Processor tests additionally exercise
every action-bearing event family, all eight notification values, both feature
branches, role-sensitive disconnect handling, timer releases/rearms, the
200/1,000/2,000-ms retry sequence, and the 10-second delayed-start branch. All
four files also compile for `thumbv7em-none-eabi` with exactly the twelve expected
global text symbols, and their source hashes are test-pinned.

This completes the behavioral candidate for the product-owned surface. The
interposed 44-byte GPIO vector remains a separate Apollo510 ownership unit. No
candidate body is routed in the production overlay, so package ownership
remains unchanged; absolute placement, retained logger bindings, and redirect
installation remain separate integration work.

## Vector correction

The complete vector table begins at `0x00438000`. Slot 75 is external IRQ 59
and contains Thumb entry `0x004B80BF`. The Apollo510 CMSIS enum identifies IRQ
59 as `GPIO0_607F_IRQn`. The wrapper reads the group and IRQ-specific GPIO
status, clears that status, and services the GPIO handlers.

It is not a BLE-controller interrupt wrapper and does not call
`HciDrvIntService`. This corrects the earlier HCI-driver note that placed an
assumed hardware-vector caller outside the OTA payload. The retained
`HciDrvIntService [0x004B4A98,0x004B4AB2)` has no direct caller, vector/stored
pointer, or otherwise proven static ingress in the complete OTA. Its possible
runtime ingress remains unresolved.

## Source qualification

AmbiqSuite R2.5.1 `ble_freertos_fit/src/radio_task.c` (9,001 bytes, SHA-256
`f5bf90bb48d888cb147efc3143675f565ebcb0c8fb469b0da9f49dddfa2f5d8d`)
is a topology oracle: it shows the same WSF/security/handler/radio/application
startup pattern. It is not the product source and is not a whole-file match;
stock enables both roles, more host components, product registration and
runtime configuration. The vendored Apollo510 CMSIS header (SHA-256
`b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797`)
is used only to identify IRQ 59.

The exact historical product source and generating commit remain unresolved.
No vendor implementation bytes are copied into production and no stock bytes
are replaced by this audit or the current partial candidate.

The complete body ledger is
[`g2-app-ble-startup-function-map.tsv`](../../tools/manifests/g2-app-ble-startup-function-map.tsv).
[`analyze_g2_app_ble_startup.py`](../../tools/analyze_g2_app_ble_startup.py)
pins both evidence manifests, every body and retained string, the handler
literal block, all direct calls, vector identity, and entry/interior closure.

```sh
python3 tools/analyze_g2_app_ble_startup.py --json
python3 -m unittest \
  tests.test_analyze_g2_app_ble_startup \
  tests.test_app_ble_candidate
```
