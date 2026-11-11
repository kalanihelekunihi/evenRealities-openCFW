/* Native UART sync RAM cells; final linker placement remains a separate gate. */
#include <stdint.h>

void *g2_uart_sync_driver __attribute__((section(".g2_ram_20074610"), aligned(4)));
void (*g2_uart_sync_callback_cell)(void)
    __attribute__((section(".g2_ram_20074618"), aligned(4)));
void *g2_uart_sync_semaphore_handle
    __attribute__((section(".g2_ram_2007461c"), aligned(4)));
void *g2_uart_sync_mutex __attribute__((section(".g2_ram_20074620"), aligned(4)));
/* g2_uart_sync_module: same stock cell as another object; now an alias there (see sim-test-report Fix 31). */
/* g2_uart_sync_semaphore: same stock cell as another object; now an alias there (see sim-test-report Fix 31). */
volatile uint8_t g2_uart_sync_started
    __attribute__((section(".g2_ram_20074fc9")));
volatile uint8_t g2_uart_sync_write_error
    __attribute__((section(".g2_ram_20074fca")));
uint8_t g2_uart_sync_tx_buffer[0x400]
    __attribute__((section(".g2_ram_20379da0"), aligned(4)));
