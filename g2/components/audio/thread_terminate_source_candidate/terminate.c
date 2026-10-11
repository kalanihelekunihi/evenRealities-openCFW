/* Stock CMSIS osThreadTerminate 0x4491fe..0x449237. */
#include <stdint.h>
extern uint32_t audio_irq_context(void); /* stock 0x44900e */
extern uint32_t audio_task_state(void *thread); /* stock 0x454b88 */
extern void audio_task_delete(void *thread); /* stock 0x454aae */
int32_t audio_thread_terminate_peer(void *thread)
{
    if (audio_irq_context()!=0u) return -6;
    if (thread==0) return -4;
    if ((uint8_t)audio_task_state(thread)==4u) return -3;
    audio_task_delete(thread);
    return 0;
}
