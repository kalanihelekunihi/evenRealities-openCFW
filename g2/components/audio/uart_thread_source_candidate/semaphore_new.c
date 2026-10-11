/* CMSIS osSemaphoreNew, native 0x44989a. The queue children are the selected
 * FreeRTOS implementations; queue control has uxMessagesWaiting at +0x38. */
#include <stdint.h>

extern uint32_t audio_cmsis_irq_context(void); /* 0x44900e */
extern void *audio_queue_create_dynamic(uint32_t,uint32_t,uint32_t); /* 0x441636 */
extern void *audio_queue_create_static(uint32_t,uint32_t,void *,void *,uint32_t); /* 0x4415ca */
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t); /* 0x4417ee */
extern int32_t audio_queue_delete(void *); /* 0x441ea2 */

void *audio_uart_sync_sem_new(uint32_t maximum,uint32_t initial,
                              const void *attributes) {
    if (audio_cmsis_irq_context()!=0u || maximum==0u || initial>maximum)
        return 0;
    int static_control=0;
    void *control=0;
    if (attributes!=0) {
        const uint8_t *a=(const uint8_t *)attributes;
        control=*(void *const *)(a+8u);
        uint32_t size=*(const uint32_t *)(a+12u);
        if (control!=0 && size>=0x50u) static_control=1;
        else if (control==0 && size==0u) static_control=0;
        else return 0;
    }
    void *q;
    if (maximum==1u) {
        q=static_control ? audio_queue_create_static(1u,0u,0,control,3u)
                         : audio_queue_create_dynamic(1u,0u,3u);
        if (q!=0 && initial!=0u && audio_uart_queue_send(q,0,0u,0u)!=1) {
            (void)audio_queue_delete(q);
            q=0;
        }
    } else {
        q=static_control ? audio_queue_create_static(maximum,0u,0,control,2u)
                         : audio_queue_create_dynamic(maximum,0u,2u);
        if (q!=0) *(uint32_t *)((uint8_t *)q+0x38u)=initial;
    }
    return q;
}
