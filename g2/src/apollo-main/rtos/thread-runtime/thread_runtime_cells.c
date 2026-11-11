/* Native UART thread RAM operands; placement and initialization remain gated. */
#include <stdint.h>

/* g2_uart_thread_event: same stock cell as another object; now an alias there (see sim-test-report Fix 31). */
void *g2_uart_thread_transport __attribute__((section(".g2_ram_20074b14"), aligned(4)));
void *g2_uart_thread_mutex __attribute__((section(".g2_ram_20074b18"), aligned(4)));
/* Sim-test fix (2026-10-26): RAM 0x20000658 is the first word of the
 * displaydrv_manager record, stock .data init {0x473953 (Disp_ThreadInit),
 * 0x473aa5, 0, 0} (.waves/init_20000000.bin +0x658), defined in C as
 * audio_display_driver_manager (drivers/S1-drivers-hal-ble-data/display_data.c).
 * A separate zero cell defined here made uart_thread_handler (stock 0x5417d6) blx 0
 * -> INVSTATE HardFault in Renode. Removed. */
/* (No separate cell: thread.c reads the record directly.) */
uint8_t g2_uart_command[11]
    __attribute__((section(".g2_ram_20074080"), aligned(4)));
uint8_t g2_uart_rx_buffer[1024]
    __attribute__((section(".g2_ram_2006c930"), aligned(4)));
