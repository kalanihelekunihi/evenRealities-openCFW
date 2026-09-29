# STMicroelectronics ST25DVxxKC (ST25DV04KC / 16KC / 64KC)

**Used in:** R1 ring, dynamic NFC tag on the 13.56 MHz charging/dock link.
Tags: [vocabulary](../README.md#confidence-vocabulary).

## Identification

| Evidence | Tag |
|---|---|
| ST25DVxxKC BSP functions (`ST25DVxxKC_WriteData` 0xA6, `ST25DVxxKC_WriteRegister` 0xAE, `ST25DVxxKC_RegisterBusIO`), accepted IC references 0x50 / 0x51, mailbox and energy-harvesting control | FW High (`r1/docs/correlation/ST25DVXXKC-CORRELATION.md:34-42,160-168`) |
| Exact density (04KC / 16KC / 64KC) | Not established |

## Documents

| Document | URL |
|---|---|
| Datasheet (DS13519) | https://www.st.com/resource/en/datasheet/st25dv04kc.pdf |
| Product page ST25DV04KC | https://www.st.com/en/nfc/st25dv04kc.html |

## Key specifications (DS)

ISO/IEC 15693 (NFC Forum Type 5) tag with I2C interface; 4 / 16 / 64 Kbit
EEPROM; fast-transfer-mode mailbox; configurable GPO interrupt; energy
harvesting output (V_EH) from the RF field; low-power mode.

## R1 use (FW)

Software TWI `i2c_5` (P1.11 / P1.14, shared with YHM2710), GPO P0.03
(rising edge), dock enable P1.10; 20-byte application mailbox; all-zero I2C
password presentation to open the security session; GPO1 `0x21`.

## Relevance to decompilation

Matches ST's `st25dvxxkc` BSP (X-CUBE / fp-sns-stbox1 lineage); use it to
label the NFC driver cluster.
