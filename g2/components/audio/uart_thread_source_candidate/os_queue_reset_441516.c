/* Apollo main 0x441516: FreeRTOS queue reset. */
#include <stdint.h>

extern uint32_t audio_os_interrupt_mask_5fa0a4(void);
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern void audio_os_list_initialize_45607c(uint32_t);
extern uint32_t opencfw_ready_remove_event_list(uint32_t);
extern void audio_yield(void);

static void invalid_queue(void) {
    (void)audio_os_interrupt_mask_5fa0a4();
    *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    for (;;) { }
}

static uint32_t read32(uint32_t address) {
    return *(volatile uint32_t *)(uintptr_t)address;
}
static void write32(uint32_t address, uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)address = value;
}

uint32_t audio_os_queue_reset_441516(uint32_t queue, uint32_t new_queue) {
    if (queue == 0u) invalid_queue();
    uint32_t length = read32(queue + 60u);
    uint32_t item_size = read32(queue + 64u);
    if (length == 0u || item_size > UINT32_MAX / length) invalid_queue();
    stock_enter_critical();
    uint32_t head = read32(queue);
    write32(queue + 8u, head + length * item_size);
    write32(queue + 56u, 0u);
    write32(queue + 4u, head);
    write32(queue + 12u, head + (length - 1u) * item_size);
    *(volatile uint8_t *)(uintptr_t)(queue + 68u) = 0xffu;
    *(volatile uint8_t *)(uintptr_t)(queue + 69u) = 0xffu;
    if (new_queue == 0u) {
        if (read32(queue + 16u) != 0u &&
            opencfw_ready_remove_event_list(queue + 16u) != 0u)
            audio_yield();
    } else {
        audio_os_list_initialize_45607c(queue + 16u);
        audio_os_list_initialize_45607c(queue + 36u);
    }
    stock_exit_critical();
    return 1u;
}
