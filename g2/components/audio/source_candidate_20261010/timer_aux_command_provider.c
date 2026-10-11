#include <stdint.h>

extern uint32_t audio_scheduler_state(void);
extern int32_t xQueueGenericSend(void *, const void *, uint32_t, int32_t);
extern int32_t xQueueGenericSendFromISR(void *, const void *, int32_t *, int32_t);
extern uint32_t audio_mask_save(void);

typedef struct {
    uint32_t command;
    uint32_t value;
    void *timer;
    void *woken;
} timer_command_packet;

int32_t audio_aux_command(void *timer, int32_t command, uint32_t value,
                          void *woken, uint32_t ticks) {
    if (!timer) {
        (void)audio_mask_save();
        *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0;
        for (;;) { }
    }
    void *queue = *(void * volatile *)(uintptr_t)0x20074ab0u;
    if (!queue) return 0;
    timer_command_packet packet = {(uint32_t)command, value, timer, woken};
    if (command < 6) {
        uint32_t wait = audio_scheduler_state() == 2 ? ticks : 0;
        return xQueueGenericSend(queue, &packet, wait, 0);
    }
    return xQueueGenericSendFromISR(queue, &packet, (int32_t *)woken, 0);
}
