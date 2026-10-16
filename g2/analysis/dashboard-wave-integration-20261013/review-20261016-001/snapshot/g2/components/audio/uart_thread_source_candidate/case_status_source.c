#include <stdint.h>

volatile uint8_t audio_uart_case_status_disabled
    __attribute__((section(".g2_ram_20075012"), used));
volatile uint8_t audio_uart_case_sensor_a
    __attribute__((section(".g2_ram_2007418f"), used));
volatile uint8_t audio_uart_case_sensor_b
    __attribute__((section(".g2_ram_2007418e"), used));

uint32_t audio_uart_case_status(void)
{
    if (audio_uart_case_status_disabled != 0u)
        return 0u;
    if (audio_uart_case_sensor_a == 1u)
        return 1u;
    return audio_uart_case_sensor_b == 1u ? 1u : 0u;
}
