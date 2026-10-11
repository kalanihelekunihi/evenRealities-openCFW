/* Codec lifecycle callers use these same Apollo UART HAL entries. */
#include "../uart_power_config_offline/am_hal_uart.c"
__asm__(".global codec_hal_power\n"
        ".set codec_hal_power, am_hal_uart_power_control\n"
        ".global codec_hal_configure\n"
        ".set codec_hal_configure, am_hal_uart_configure\n");
