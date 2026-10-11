/* Stock FreeRTOS vTaskDelete 0x454aae..0x454b4b.
 * Retains authentic task cleanup as a distinct child contract. */
#include <stdint.h>
extern void *g2_audio_current_task; /* cell 0x20074a20 */
extern uint32_t g2_audio_task_count; /* cell 0x20074a30 */
extern uint32_t g2_audio_task_deletion_count; /* cell 0x20074a4c */
extern uint32_t g2_audio_tasks_waiting_cleanup; /* cell 0x20074a2c */
extern uint32_t g2_audio_scheduler_running; /* cell 0x20074a3c */
extern uint32_t g2_audio_scheduler_suspended; /* cell 0x20074a58 */
extern uint8_t g2_audio_terminated_list[]; /* object 0x20073d38 */
extern void stock_enter_critical(void);
extern void stock_exit_critical(void);
extern void stock_yield(void);
extern uint32_t stock_list_remove(void *);
extern void audio_public_list_insert(void *,void *);
extern void audio_queue_next_unblock(void); /* 0x455876 */
extern void audio_task_cleanup(void *); /* 0x455836 */
extern void offline_assert(void) __attribute__((noreturn));
void audio_task_delete(void *thread)
{
    stock_enter_critical();
    uint8_t *task=(uint8_t *)(thread ? thread : g2_audio_current_task);
    stock_list_remove(task+4);
    if (*(uint32_t *)(task+40)!=0u) stock_list_remove(task+24);
    g2_audio_task_deletion_count++;
    if (task==(uint8_t *)g2_audio_current_task) {
        audio_public_list_insert(g2_audio_terminated_list,task+4);
        g2_audio_tasks_waiting_cleanup++;
    } else {
        g2_audio_task_count--;
        audio_queue_next_unblock();
    }
    stock_exit_critical();
    if (task!=(uint8_t *)g2_audio_current_task) audio_task_cleanup(task);
    if (g2_audio_scheduler_running && task==(uint8_t *)g2_audio_current_task) {
        if (g2_audio_scheduler_suspended) offline_assert();
        stock_yield();
    }
}
