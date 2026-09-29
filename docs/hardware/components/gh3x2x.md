# Goodix GH3x2x PPG front end

**Used in:** R1 ring for heart rate, HRV, SpO2 and wear detection. Tags:
[vocabulary](../README.md#confidence-vocabulary).

## Identification

| Evidence | Tag |
|---|---|
| Goodix `gh3x2x-v2.23_7ecd2a` driver, democode v1.6, DrvLib v4.3.0.0, Virtual_Reg v3.4; 8-bit device ID 0x28 (`GH3X2X_I2C_ID_SEL_1L0L`); binary-only HBA/HRV/SpO2/NADT algorithm libraries | FW High (family) (`r1/docs/boundaries/goodix_gh3x2x_candidate-ATTRIBUTION-2026-08.md`; `r1/docs/correlation/GOODIX-DEMOCODE-INTEGRATION-CORRELATION.md:58,190`) |
| Exact part (GH3026, GH3220, …) | UNV |

## Documents

| Document | URL |
|---|---|
| GH3026 | https://www.goodix.com/en/product/sensors/health_sensors/gh3026 |
| GH3220 | https://www.goodix.com/en/product/sensors/health_sensors/gh3220 |
| GH3020 | https://www.goodix.com/en/product/sensors/health_sensors/gh3020 |
| GH3x2x driver library | https://www.goodix.com/en/software_tool/gh3x2x_driver |
| GH3x2x algorithm library | https://www.goodix.com/en/software_tool/gh3x2x_algorithm |

Public datasheet PDFs were not found.

## Key specifications (vendor pages)

Multi-channel PPG analog front end with LED drivers and photodiode inputs
for HR / HRV / SpO2; GH3220 has 4 AFEs and up to 32 channels.

## R1 use (FW)

Software TWI `i2c_4` (SCL P1.09, SDA P0.31), 16-bit register addresses;
INT P0.21, emitter P0.10, reset P1.04.

## Relevance to decompilation

The driver layer matches the public democode (pinned copy referenced in
`r1/third-party/fetched/manifest.json`); the algorithm libraries are
binary-only and not redistributable.
