/* FreeRTOS scheduler BSS layout proven by vTaskStartScheduler/list init
 * native 0x45568c. These are live state cells, not invented product values.
 * Relocatable C linker placement still needs a complete image script. */
#include <stdint.h>
#include "../../../apollo-common/freertos-event-group/event_group.h"
_Static_assert(sizeof(List_t)==20u,"native FreeRTOS list ABI");

_Alignas(4) uint8_t g2_audio_ready_lists[56u*20u]; /* stock 0x2006a49c */
_Alignas(4) uint8_t g2_audio_delayed_buffer_a[20u]; /* 0x20073cfc */
_Alignas(4) uint8_t g2_audio_delayed_buffer_b[20u]; /* 0x20073d10 */
_Alignas(4) uint8_t g2_audio_pending_ready_list[20u]; /* 0x20073d24 */
_Alignas(4) uint8_t g2_audio_terminated_list[20u]; /* 0x20073d38 */
_Alignas(4) uint8_t g2_audio_suspended_list[20u]; /* 0x20073d4c */

void *g2_audio_current_task; /* 0x20074a20 */
void *g2_audio_delayed_list0; /* 0x20074a24, set by list init */
void *g2_audio_delayed_list1; /* 0x20074a28, set by list init */
uint32_t g2_audio_tasks_waiting_cleanup; /* 0x20074a2c */
uint32_t g2_audio_task_count; /* 0x20074a30 */
uint32_t g2_audio_top_ready_priority; /* 0x20074a38 */
uint32_t g2_audio_scheduler_running; /* 0x20074a3c */
uint32_t g2_audio_task_deletion_count; /* 0x20074a4c */
uint32_t g2_audio_scheduler_suspended; /* 0x20074a58 */
