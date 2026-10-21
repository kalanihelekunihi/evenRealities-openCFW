/* Stock FreeRTOS scheduler list initialization, 0x45568c. */
#include <stdint.h>
#include "../../../../apollo-common/freertos-ready/ready.h"
extern void vListInitialise(List_t *list);
extern uint8_t g2_audio_ready_lists[];
extern uint8_t g2_audio_delayed_buffer_a[];
extern uint8_t g2_audio_delayed_buffer_b[];
extern uint8_t g2_audio_pending_ready_list[];
extern uint8_t g2_audio_terminated_list[];
extern uint8_t g2_audio_suspended_list[];
extern void *g2_audio_delayed_list0;
extern void *g2_audio_delayed_list1;
void g2_thread_initialize_lists(void) {
    List_t *const ready=(List_t *)(void *)g2_audio_ready_lists;
    List_t *const delayed_a=(List_t *)(void *)g2_audio_delayed_buffer_a;
    List_t *const delayed_b=(List_t *)(void *)g2_audio_delayed_buffer_b;
    for(uint32_t i=0;i<56u;i++) vListInitialise(&ready[i]);
    vListInitialise(delayed_a);
    vListInitialise(delayed_b);
    vListInitialise((List_t *)(void *)g2_audio_pending_ready_list);
    vListInitialise((List_t *)(void *)g2_audio_terminated_list);
    vListInitialise((List_t *)(void *)g2_audio_suspended_list);
    g2_audio_delayed_list0=delayed_a;
    g2_audio_delayed_list1=delayed_b;
}
