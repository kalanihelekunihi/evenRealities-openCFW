#include <stdint.h>

/* Native xTaskGenericNotify task path 0x455c48..0x455db9. The RAM
 * cells are authenticated FreeRTOS scheduler state, not fabricated
 * product initializers. */
extern uint32_t g2_audio_notify_assert_enabled; /* 0x20074a34 */
extern uint32_t g2_audio_top_ready_priority;    /* 0x20074a38 */
extern void *g2_audio_current_task;             /* 0x20074a20 */
extern uint8_t g2_audio_ready_lists[];          /* 0x2006a49c */
extern void audio_enter_critical(void);         /* 0x4420d0 */
extern void audio_exit_critical(void);          /* 0x4420e8 */
extern void audio_queue_next_unblock(void);     /* 0x455876 */
extern void audio_yield(void);                   /* 0x4420bc */

static uint32_t load(uintptr_t address) {
    return *(uint32_t *)address;
}
static void save(uintptr_t address, uint32_t value) {
    *(uint32_t *)address = value;
}

/* The native invalid-task/index/assert path reads BASEPRI, writes
 * address UINT32_MAX, then loops. This is the decoded fault behavior. */
__attribute__((noreturn)) static void native_fault(void) {
    uint32_t basepri;
    __asm__ volatile("mrs %0, basepri" : "=r"(basepri));
    (void)basepri;
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    for (;;) __asm__ volatile("nop");
}

uint32_t audio_notify_task(void *task, uint32_t index, uint32_t value,
                           uint32_t action, uint32_t *previous) {
    if (index != 0u || task == 0)
        native_fault();
    const uintptr_t t = (uintptr_t)task;
    uint32_t result = 1u;
    audio_enter_critical();
    if (previous != 0)
        *previous = load(t + 104u);
    uint8_t const prior_state = *(uint8_t *)(t + 108u);
    *(uint8_t *)(t + 108u) = 2u;
    switch ((uint8_t)action) {
    case 0u: break;
    case 1u: save(t + 104u, load(t + 104u) | value); break;
    case 2u: save(t + 104u, load(t + 104u) + 1u); break;
    case 3u: save(t + 104u, value); break;
    case 4u:
        if (prior_state == 2u) result = 0u;
        else save(t + 104u, value);
        break;
    default:
        if (g2_audio_notify_assert_enabled != 0u)
            native_fault();
        break;
    }

    if (prior_state == 1u) {
        const uintptr_t item = t + 4u;
        const uintptr_t container = load(t + 20u);
        const uintptr_t next = load(t + 8u);
        const uintptr_t prev = load(t + 12u);
        save(next + 8u, (uint32_t)prev);
        save(prev + 4u, (uint32_t)next);
        if (load(container + 4u) == item)
            save(container + 4u, (uint32_t)prev);
        save(t + 20u, 0u);
        save(container, load(container) - 1u);
        const uint32_t priority = load(t + 44u);
        if (g2_audio_top_ready_priority < priority)
            g2_audio_top_ready_priority = priority;
        const uintptr_t ready = (uintptr_t)g2_audio_ready_lists + 20u * priority;
        const uintptr_t index_item = load(ready + 4u);
        save(t + 8u, (uint32_t)index_item);
        const uintptr_t index_prev = load(index_item + 8u);
        save(t + 12u, (uint32_t)index_prev);
        save(index_prev + 4u, (uint32_t)item);
        save(index_item + 8u, (uint32_t)item);
        save(t + 20u, (uint32_t)ready);
        save(ready, load(ready) + 1u);
        if (load(t + 40u) != 0u)
            native_fault();
        audio_queue_next_unblock();
        if (load((uintptr_t)g2_audio_current_task + 44u) < priority)
            audio_yield();
    }
    audio_exit_critical();
    return result;
}
