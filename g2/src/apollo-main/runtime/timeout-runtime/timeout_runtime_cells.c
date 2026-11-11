/* Native timeout worker RAM cells; final linker placement remains gated. */
#include <stdint.h>

void *audio_uart_timeout_queue
    __attribute__((section(".g2_ram_20074aa0"), aligned(4)));
void *audio_uart_timeout_mutex
    __attribute__((section(".g2_ram_20074aa4"), aligned(4)));
volatile uint8_t audio_uart_timeout_running_state
    __attribute__((section(".g2_ram_20075031")));
/* Stock 0x20074aa0 is a single cell (literal pool 0x491618); alias so all users share it (Fix 31). */
extern void * audio_uart_pool_queue __attribute__((alias("audio_uart_timeout_queue")));
/* Stock 0x20074aa4 is a single cell (literal pool 0x491650); alias so all users share it (Fix 31). */
extern void * audio_uart_pool_mutex __attribute__((alias("audio_uart_timeout_mutex")));
/* Stock 0x20075031 is a single cell (literal pool 0x491630); alias so all users share it (Fix 31). */
extern uint8_t audio_uart_pool_initialized __attribute__((alias("audio_uart_timeout_running_state")));
