/* SPDX-License-Identifier: MIT */
#include <driver/gx_clock.h>
/* Recovered ordered divider/DTO setup at backup 0x3bc8c..0x3bd1a.
 * Keep board-specific ADC/PDM divisors and audio-play DTO distinct from
 * upstream board defaults. Values are register parameters, not Hertz. */
void open_cfw_gx8002_backup_clock_dividers(void)
{
    gx_clock_set_dto(CLOCK_MODULE_AUDIO_IN_SYS, 0x01000000, 1);
    gx_clock_set_div(CLOCK_MODULE_SRAM, 2);
    gx_clock_set_div(CLOCK_MODULE_RTC, 4);
    gx_clock_set_div(CLOCK_MODULE_PMU, 3);
    gx_clock_set_div(CLOCK_MODULE_FFT, 2);
    gx_clock_set_div(CLOCK_MODULE_AUDIO_IN_SYS, 2);
    gx_clock_set_div(CLOCK_MODULE_AUDIO_IN_ADC, 384);
    gx_clock_set_div(CLOCK_MODULE_AUDIO_IN_PDM, 12);
    gx_clock_set_div(CLOCK_MODULE_I2C0_I2C1, 2);
    gx_clock_set_dto(CLOCK_MODULE_UART0_UART1, 0x01000000, 1);
    gx_clock_set_dto(CLOCK_MODULE_AUDIO_PLAY, 0x00800000, 1);
    gx_clock_set_div(CLOCK_MODULE_SCPU, 0);
    gx_clock_set_div(CLOCK_MODULE_NPU, 6);
    gx_clock_set_div(CLOCK_MODULE_FLASH_SPI, 2);
    gx_clock_set_div(CLOCK_MODULE_AUDIO_LODAC, 4);
    gx_clock_set_div(CLOCK_MODULE_GENERAL_SPI, 4);
}
