/* Apollo Main compressed SRAM record 0x75d3f4 initializes this observed
 * UART thread-manager span at 0x200040d8; the next thread record begins at
 * 0x200040fc. The selected ring-sync path reads its handle at offset 28.
 * Absolute placement and complete native structure ownership remain gates. */
#include <stdint.h>

/* Sim-test fix (2026-10-26): the stock RAM-init words 0x004c9b49/0x004c9b71 are
 * stock-flash Thumb pointers; copying them as bytes made our image jump
 * into unrelated code (Renode boot hang in main_5ce01e). Evidence: main_5ce01e stock 0x5ce130 loads *0x200040d8 and blx; stock symbols thread_manager_kernel_start_4c9b48/thread_manager_deinit_4c9b70 (g2/symbols/apollo_main.tsv, thread_manager.c:28-29).
 * Now relocated to our own symbols thread_manager_kernel_start_4c9b48/thread_manager_deinit_4c9b70. Layout and size unchanged. */
void thread_manager_kernel_start_4c9b48(void);
void thread_manager_deinit_4c9b70(void);
_Alignas(4) struct { void (*init)(void); void (*deinit)(void); uint8_t rest[28u]; } audio_uart_thread_manager_state = {
    thread_manager_kernel_start_4c9b48, thread_manager_deinit_4c9b70, {0}
};
