/* Stock FreeRTOS prvDeleteTCB 0x455836..0x455875. */
#include <stdint.h>
extern void audio_heap_free(void *); /* selected vPortFree 0x456210 */
extern void offline_assert(void) __attribute__((noreturn));
void audio_task_cleanup(void *thread)
{
    uint8_t *task=(uint8_t *)thread;
    switch (task[109]) {
    case 0:
        audio_heap_free(*(void **)(task+48));
        audio_heap_free(task);
        return;
    case 1:
        audio_heap_free(task);
        return;
    case 2:
        return;
    default:
        offline_assert();
    }
}
