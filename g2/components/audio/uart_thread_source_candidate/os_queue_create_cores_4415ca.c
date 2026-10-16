/* Apollo main 0x4415ca/0x441636: FreeRTOS static and dynamic queue creation. */
#include <stdint.h>

extern uint32_t audio_os_interrupt_mask_5fa0a4(void);
extern uint32_t pvPortMalloc(uint32_t);
extern void audio_os_queue_initialize_441696(uint32_t, uint32_t, uint32_t,
                                             uint32_t, uint32_t);

static void invalid_queue(void) {
    (void)audio_os_interrupt_mask_5fa0a4();
    *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    for (;;) { }
}

uint32_t audio_os_mutex_static_core_4415ca(uint32_t length, uint32_t item_size,
                                            uint32_t storage, uint32_t control,
                                            uint32_t kind) {
    if (control == 0u || length == 0u ||
        ((storage == 0u) != (item_size == 0u))) invalid_queue();
    *(volatile uint8_t *)(uintptr_t)(control + 70u) = 1u;
    audio_os_queue_initialize_441696(length, item_size, storage,
                                      (uint8_t)kind, control);
    return control;
}

uint32_t audio_os_mutex_dynamic_core_441636(uint32_t length, uint32_t item_size,
                                             uint32_t kind) {
    if (length == 0u || item_size > UINT32_MAX / length ||
        length * item_size > UINT32_MAX - 80u) invalid_queue();
    uint32_t control = pvPortMalloc(length * item_size + 80u);
    if (control != 0u) {
        *(volatile uint8_t *)(uintptr_t)(control + 70u) = 0u;
        audio_os_queue_initialize_441696(length, item_size, control + 80u,
                                          (uint8_t)kind, control);
    }
    return control;
}
