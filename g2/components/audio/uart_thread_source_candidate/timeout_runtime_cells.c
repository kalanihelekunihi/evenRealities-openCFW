/* Native timeout worker RAM cells; final linker placement remains gated. */
#include <stdint.h>

void *audio_uart_timeout_queue
    __attribute__((section(".g2_ram_20074aa0"), aligned(4)));
void *audio_uart_timeout_mutex
    __attribute__((section(".g2_ram_20074aa4"), aligned(4)));
volatile uint8_t audio_uart_timeout_running_state
    __attribute__((section(".g2_ram_20075031")));
