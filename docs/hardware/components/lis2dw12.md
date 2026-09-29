# STMicroelectronics LIS2DW12

**Used in:** R1 ring, accelerometer probe 1 of 3 at I2C 0x18. Tags:
[vocabulary](../README.md#confidence-vocabulary).

## Identification

| Evidence | Tag |
|---|---|
| ST `lis2dw12` pid driver v2.1.0 compatible; WHO_AM_I 0x44; probe wrappers `0x0006F380…` | FW High (driver; `r1/docs/correlation/MOTION-PROVIDER-CORRELATION.md:54,114`) |
| Fitted part in retail rings | Not established |

## Documents

| Document | URL |
|---|---|
| Product page | https://www.st.com/en/mems-and-sensors/lis2dw12.html |
| Datasheet | https://www.st.com/resource/en/datasheet/lis2dw12.pdf |
| AN5038 | https://www.st.com/resource/en/application_note/an5038-lis2dw12-alwayson-3axis-accelerometer-stmicroelectronics.pdf |

## Key specifications (DS)

±2/4/8/16 g; ODR 1.6–1600 Hz; 90 µA high-resolution, <1 µA low-power;
32-level FIFO; 1.62–3.6 V; I2C/SPI; LGA; −40 to +85 °C.

## Relevance to decompilation

Match against ST's `lis2dw12_reg.c` platform-independent driver.
