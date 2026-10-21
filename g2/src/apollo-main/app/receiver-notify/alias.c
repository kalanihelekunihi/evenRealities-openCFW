#include <stdint.h>

/* Both receiver imports identify selected native notification entries.
 * Task notify is 0x455c48; wait is 0x455b84. The latter selected C
 * body is qualified for index zero and bounded nonblocking paths. */
extern uint32_t audio_notify_task(void *task, uint32_t index,
                                  uint32_t value, uint32_t action,
                                  uint32_t *previous);
extern int32_t audio_notify_wait(uint32_t index, uint32_t clear_enter,
                                 uint32_t clear_exit, uint32_t *out,
                                 uint32_t ticks);

uint32_t receiver_notify(void *task, uint32_t index, uint32_t value,
                         uint32_t action, uint32_t *previous) {
    return audio_notify_task(task, index, value, action, previous);
}

int32_t receiver_notify_wait(uint32_t index, uint32_t clear_enter,
                             uint32_t clear_exit, uint32_t *out,
                             uint32_t ticks) {
    return audio_notify_wait(index, clear_enter, clear_exit, out, ticks);
}
