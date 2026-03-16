# Device Firmware Ownership Model

This document is the clean-room model for which firmware files belong to which physical devices in the Even Realities ecosystem, and which of those image domains `openCFW` can safely target first.

## Device Matrix

| Device | State | Confirmed Firmware Files | Update Ingress | openCFW Posture | Remaining Gaps |
|---|---|---|---|---|---|
| G2-L | Identified | `ota_s200_bootloader.bin`, `ota_s200_firmware_ota.bin`, `firmware_ble_em9305.bin`, `firmware_codec.bin`, `firmware_touch.bin` | EVENOTA over G2 BLE file lane | Same image family as G2-R; runtime-selected identity | exact persistent left/right role provisioning path |
| G2-R | Identified | `ota_s200_bootloader.bin`, `ota_s200_firmware_ota.bin`, `firmware_ble_em9305.bin`, `firmware_codec.bin`, `firmware_touch.bin` | EVENOTA over G2 BLE file lane | Same image family as G2-L; runtime-selected identity | exact persistent left/right role provisioning path |
| G2 Charging Case | Partial but executable | `firmware_box.bin` | Relayed through the glasses over case/UART paths | Compatibility boundary first, not an initial rewrite target | exact MCU part and full UART grammar |
| R1 Ring | Partial / blocked | Separate Nordic runtime family; current corpus contains `B210_ALWAY_BL_DFU_NO`, `B210_BL_DFU_NO_v2.0.3.0004`, and `B210_SD_ONLY_NO_v2.0.3.0004`, but not the standalone ring application image | FE59 buttonless DFU + SMP/MCUmgr, outside EVENOTA | Protocol-compatibility only until the ring application image exists | standalone app image, exact distribution route, exact production SoC SKU |
| R1 Charging Cradle | Identified | none | none | No firmware target | none |

## Identified Ownership Contracts

### G2-L and G2-R Are One Firmware Family

- The left and right glasses do not use separate vendor builds.
- Both eyes consume the same Apollo bootloader, Apollo main app, EM9305 patch, codec payload, and touch payload from the EVENOTA package.
- Left/right differentiation is runtime-selected through identity, BLE naming, and role state rather than through different firmware binaries.
- Clean-room implication: `openCFW` should produce one Apollo image family for both eyes, not per-eye forks.

### Apollo Main Runtime Owns the G2 Update Fan-Out

- `ota_s200_firmware_ota.bin` is the executable center of gravity for G2 behavior.
- The Apollo main app owns subordinate update orchestration for:
  - EM9305
  - GX8002B
  - CY8C4046FNI
  - G2 case relay/update
- Clean-room implication: subordinate images should currently be treated as Apollo-owned compatibility domains rather than as first-wave rewrite targets.

### G2 Case Firmware Is Separate and Relay-Only

- `firmware_box.bin` belongs to the charging case MCU, not to the Apollo image family.
- The phone does not reach the case directly over BLE.
- Case status and case OTA reach the case only by flowing through the glasses relay path.
- Clean-room implication: case support should stay a relay-compatibility boundary until the case UART grammar closes further.

### R1 Ring Firmware Is a Separate Product Family

- Ring firmware is not part of the EVENOTA package.
- The ring uses its own FE59 + SMP/MCUmgr + MCUboot-style update domain.
- Current local artifacts close the failsafe bootloader, versioned bootloader, and SoftDevice pieces, but the ring application runtime image itself is still missing.
- Clean-room implication: ring firmware replacement remains blocked even though ring protocol compatibility work can continue.

### The R1 Charging Cradle Has No Firmware

- The cradle is a passive charging accessory.
- It has no MCU, no BLE runtime, and no DFU surface.
- Clean-room implication: it is not a firmware target and should not appear in the custom-firmware platform plan.

## Inferred but Not Fully Closed

### The Bundled Nordic DFU Artifacts Are Auxiliary, Not Apollo-Primary

- The `B210_ALWAY_BL_DFU_NO`, `B210_BL_DFU_NO_v2.0.3.0004`, and `B210_SD_ONLY_NO_v2.0.3.0004` bundles clearly do not target the Apollo main runtime.
- They likely serve ring-side, recovery-side, or legacy/auxiliary Nordic paths instead.
- The exact product deployment split is still unresolved, so `openCFW` should keep them as reference artifacts rather than primary image inputs.

### Runtime Identity Provisioning Is Separate From the Shared Image Contract

- The shared left/right image story is closed.
- The exact persistent source for each eye's local identity, role defaults, and recovery behavior is still only partly closed.
- `openCFW` should therefore keep role/identity provisioning explicit and instrumented instead of baking it into build variants.

### Future Subordinate Rewrites Remain Optional

- Deeper clean-room images for case, ring, codec, touch, or radio may become possible later.
- Current evidence supports Apollo-side host compatibility much more strongly than subordinate-firmware replacement.

## Unidentified Areas

- Exact persistent left/right identity and default-role provisioning flow inside the shared G2 image family.
- Exact deployment target of the bundled `B210_ALWAY_BL_DFU_NO`, `B210_BL_DFU_NO_v2.0.3.0004`, and `B210_SD_ONLY_NO_v2.0.3.0004` packages across ring, auxiliary recovery, or legacy product paths.
- Exact standalone ring application image location and distribution contract.
- Exact future-safe path for replacing the case MCU image without first closing the full case relay grammar and bank-swap policy.

## Clean-Room Rules

- Build one Apollo main-runtime image family for both G2-L and G2-R.
- Keep bootloader compatibility separate from main-runtime replacement work.
- Keep case and ring firmware as separate device domains rather than folding them into the Apollo target.
- Do not assume EVENOTA covers ring firmware.
- Do not allocate any firmware work to the R1 charging cradle.

## Source Documents

- `../firmware/firmware-files.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/ota-protocol.md`
- `../firmware/firmware-updates.md`
- `../firmware/s200-bootloader.md`
- `../firmware/s200-firmware-ota.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`
- `../devices/r1-cradle.md`
