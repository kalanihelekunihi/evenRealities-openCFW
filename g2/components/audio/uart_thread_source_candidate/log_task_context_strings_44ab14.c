/* Apollo Main logger wrappers at 0x44ab14 and 0x44ab1c share native
 * 0x44aae0. The scheduler-suspended path returns stock "unknown";
 * otherwise xTaskGetCurrentTaskHandle leads to the TCB name at +0x34.
 * Null TCB reaches native 0x454f16's interrupt-mask/fault loop. */
#include <stdint.h>

extern uint32_t audio_scheduler_state(void);       /* native 0x4558a4 */
extern void *receiver_current_task(void);          /* native 0x45589c */
extern uint32_t audio_os_interrupt_mask_5fa0a4(void);

static const char suspended_name[] = "unknown";

static const char *task_context_name(void)
{
    if (audio_scheduler_state() == 1u)
        return suspended_name;
    uint8_t *task = (uint8_t *)receiver_current_task();
    if (task == 0) {
        (void)audio_os_interrupt_mask_5fa0a4();
        *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
        for (;;) {}
    }
    return (const char *)(task + 0x34u);
}

const char *g2_log_process_string(void)
{
    return task_context_name();
}

const char *g2_log_thread_string(void)
{
    return task_context_name();
}
