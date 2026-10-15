#include <stdint.h>

/* The suspended-scheduler arm of Apollo vTaskDelay at 0x454b60 calls the
 * BASEPRI mask entry 0x5fa0a4, writes zero to 0xffffffff, then loops. This
 * synthetic boundary keeps the nonreturning behavior explicit in C. */
extern uint32_t audio_mask_save(void);

__attribute__((noreturn)) void audio_delay_scheduler_assert(void)
{
    (void)audio_mask_save();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    for (;;) { }
}
