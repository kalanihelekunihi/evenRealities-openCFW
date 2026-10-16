/* Native UART thread RAM operands; placement and initialization remain gated. */
#include <stdint.h>

void *g2_uart_thread_event __attribute__((section(".g2_ram_20074b10"), aligned(4)));
void *g2_uart_thread_transport __attribute__((section(".g2_ram_20074b14"), aligned(4)));
void *g2_uart_thread_mutex __attribute__((section(".g2_ram_20074b18"), aligned(4)));
void (*g2_uart_thread_initialize_callback)(void)
    __attribute__((section(".g2_ram_20000658"), aligned(4)));
uint8_t g2_uart_command[11]
    __attribute__((section(".g2_ram_20074080"), aligned(4)));
uint8_t g2_uart_rx_buffer[1024]
    __attribute__((section(".g2_ram_2006c930"), aligned(4)));
