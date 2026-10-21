/* Apollo main 0x4416b8: initialize and link a new RTOS mutex. */
#include <stdint.h>

extern void audio_uart_queue_send(uint32_t, uint32_t, uint32_t, uint32_t);

void audio_os_mutex_register_4416b8(uint32_t mutex) {
    if (mutex == 0u) return;
    *(volatile uint32_t *)(uintptr_t)(mutex + 8u) = 0u;
    *(volatile uint32_t *)(uintptr_t)mutex = 0u;
    *(volatile uint32_t *)(uintptr_t)(mutex + 12u) = 0u;
    audio_uart_queue_send(mutex, 0u, 0u, 0u);
}
