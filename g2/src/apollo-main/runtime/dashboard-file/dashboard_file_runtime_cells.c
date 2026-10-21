#include <stdint.h>

void *audio_file_api_mutex
    __attribute__((section(".g2_ram_200748f4"), used));
volatile uint8_t audio_uart_dashboard_ready
    __attribute__((section(".g2_ram_20074fa5"), used));
uint8_t audio_uart_dashboard_file_buffer[4096]
    __attribute__((section(".g2_ram_2036ae40"), used));
uint8_t audio_uart_dashboard_decoded[188]
    __attribute__((section(".g2_ram_2037cc68"), used));
