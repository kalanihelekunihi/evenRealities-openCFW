# STMicroelectronics STM32G0B1 (G0Bx class)

**Used in:** G2 charging case (B200) as the case MCU. Tags:
[vocabulary](../README.md#confidence-vocabulary).

## Identification

| Evidence | Tag |
|---|---|
| 46-word vector table matching the `stm32g0b1xx.h` IRQ map (ADC1_COMP, TIM17, USART1 at G0Bx slots); USART3/USART4 bases; 512 KiB dual-bank flash with `nSWAP_BANK`; Cortex-M0+ (no `movw`/`movt`) | FW High for G0Bx class (`g2/docs/research/g2-box-stm32g0-platform-recovery.md:28-52`) |
| G0B0 vs G0B1 vs G0C1 not separable (AES/RNG/FDCAN2 unused; DBGMCU IDCODE never read) | FW (Medium for G0B1) |

## Documents

| Document | URL |
|---|---|
| Datasheet STM32G0B1xB/xC/xE | https://www.st.com/resource/en/datasheet/stm32g0b1re.pdf ; https://www.st.com/resource/en/datasheet/stm32g0b1cc.pdf |
| Reference manual RM0444 (Rev 6) | https://www.st.com/resource/en/reference_manual/rm0444-stm32g0x1-advanced-armbased-32bit-mcus-stmicroelectronics.pdf |
| Errata ES0548 | https://www.st.com/resource/en/errata_sheet/es0548-stm32g0b1xbxcxe-device-errata-stmicroelectronics.pdf |
| Product page (STM32G0B1RE) | https://www.st.com/en/microcontrollers-microprocessors/stm32g0b1re.html |
| Series documentation | https://www.st.com/en/microcontrollers-microprocessors/stm32g0-series/documentation.html |

## Key specifications (DS)

| Item | Value |
|---|---|
| Core | Arm Cortex-M0+, up to 64 MHz |
| Memory | Up to 512 KB dual-bank flash; 144 KB SRAM |
| Peripherals used by the case | USART1–4, ADC1, TIM1/3/6/14/16/17, RTC, GPIOA–D, FLASH option bytes |
| Peripherals present but unused by the case | I2C, DMA, USB (device/host + UCPD), FDCAN, LPUART, AES/RNG (G0C1/G0B1 variants) |

## Register map / SVD

The official CMSIS device header `stm32g0b1xx.h` is in ST's `cmsis_device_g0`
repository (used by the box platform analysis). ST distributes the
STM32G0B1 SVD with its device packs; RM0444 is the register reference.

## Relevance to decompilation

Load `firmware/box.bin` payload at `0x08000000` (bank 1); add a bank-2
alias at `0x08040000`; SRAM at `0x20000000`. Label the HAL islands
(FLASH keys, `HAL_UART_IRQHandler`) and the FreeRTOS GCC CM0 port
(`xPortPendSVHandler` at `0x08000102`).
