/* Apollo main 0x441696: FreeRTOS queue structure initialization. */
#include <stdint.h>

extern void audio_os_queue_reset_441516(uint32_t, uint32_t);

uint32_t audio_os_queue_initialize_441696(uint32_t length, uint32_t item_size,
                                           uint32_t storage, uint32_t kind,
                                           uint32_t control) {
    *(volatile uint32_t *)(uintptr_t)control = item_size == 0u ? control : storage;
    *(volatile uint32_t *)(uintptr_t)(control + 60u) = length;
    *(volatile uint32_t *)(uintptr_t)(control + 64u) = item_size;
    audio_os_queue_reset_441516(control, 1u);
    *(volatile uint8_t *)(uintptr_t)(control + 76u) = (uint8_t)kind;
    return kind;
}
