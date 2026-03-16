# Even G2 Charging Case — Hardware Specification

The G2 Charging Case houses and charges the G2 glasses. It contains a small ARM microcontroller for battery monitoring and charge state reporting, but has **no BLE radio** — all communication with the phone is relayed through the G2 glasses via a wired link.

---

## 1. Product Identification

| Property | Value |
|----------|-------|
| **Product Name** | Even G2 Case / Smart Glasses Case |
| **Communication** | Wired link via G2 glasses (NOT direct BLE) |
| **FCC ID** | None (no RF transmitter, part of G2 FCC listing) |
| **App ID** | `UX_GLASSES_CASE_APP_ID` |

---

## 2. Microcontroller

| Property | Value | Confidence |
|----------|-------|------------|
| **Architecture** | ARM Cortex-M (likely M0/M0+ or small M3 profile) | HIGH |
| **Flash Base** | `0x08000000` (STM32 convention) | HIGH |
| **Reset Vector** | `0x08000145` (Thumb entry) | HIGH |
| **SRAM** | ~11 KB (stack at `0x20002C88`) | MEDIUM |
| **MCU Family** | STM32 or STM32-compatible (likely F0/L0/L1-family profile) | MEDIUM |
| **SDK/toolchain lineage (inferred)** | STM32 family bootloader conventions; exact family/SDK not confirmed | LOW-MEDIUM |

The STM32-like flash base address (`0x08000000`) plus vector and stack layout strongly suggest an STM32-family microcontroller, with firmware wrapped for dual-bank updates. The exact part number and SDK variant are still unconfirmed (no direct vendor symbol map for STM32Cube/StdPeriph lineage is present in this binary).

Evidence of **dual-bank firmware** support: `running_bank` and `swap_bank` string references in the case firmware suggest A/B slot switching for reliable updates.

---

## 3. Communication Architecture

```
Phone (Even.app)          G2 Glasses (Apollo510b)        Case MCU
    │                          │                             │
    │  BLE connection          │  Wired (UART/I2C)           │
    │  ─────────────▶          │  ────────────────────▶      │
    │                          │                             │
    │  glasses_case proto      │  GlassesCaseDataPackage     │
    │  ◀─────────────          │  ◀────────────────────      │
    │                          │                             │
```

The case MCU communicates ONLY through the G2 glasses:
- **No BLE**: The case has no wireless capability
- **No direct phone link**: All data flows through the G2 BLE connection
- **Protocol**: `GlassesCaseDataPackage` protobuf with `eGlassesCaseCommandId` enum
- **Protobuf module**: `glasses_case` (library ID `@1415496902`)
- **G2 service**: Routed through the G2 control channel (0x0D-00 via `ProtoBaseSettings`)

---

## 4. Capabilities

| Capability | Detail |
|-----------|--------|
| **Battery level** | Reports case battery percentage via `GlassesCaseInfo` model |
| **Charging status** | Indicates when glasses are charging in case |
| **Docking detection** | Senses when glasses are placed in/removed from case |
| **USB-C charging** | Charges case battery; case charges glasses via contact pins |

---

## 5. Firmware

| Property | Value |
|----------|-------|
| **File** | `firmware/box.bin` in EVENOTA package |
| **EVENOTA type** | 6 (Box/Case) |
| **Wrapper** | `EVEN` magic, big-endian length + additive checksum |
| **Size** | 55,296 bytes (v2.0.7.16) |
| **Update path** | Phone → G2 glasses (BLE) → Case MCU (wired relay) |

The case firmware is bundled in the same EVENOTA package as the G2 glasses firmware. During OTA, the Apollo510b extracts `box.bin` and relays it to the case MCU over the wired inter-eye/case link. The case is the **first** sub-component updated in the OTA sequence.

See [box-case-mcu.md](../firmware/box-case-mcu.md) for the full binary structure.

---

## Related Documents

- [../firmware/box-case-mcu.md](../firmware/box-case-mcu.md) — Case firmware binary structure
- [../firmware/firmware-files.md](../firmware/firmware-files.md) — EVENOTA container, update protocol
- [g2-glasses.md](g2-glasses.md) — G2 glasses that relay case communication
