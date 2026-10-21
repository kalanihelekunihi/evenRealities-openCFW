/* Native FreeRTOS mutex allocation wrappers 0x4416d6, 0x4416f0 and
 * mutex initialization 0x4416b8. */
#include <stdint.h>
extern void *audio_queue_create_dynamic(uint32_t count,uint32_t size,uint32_t type); /* selected 0x441636 */
extern void *audio_queue_create_static(uint32_t count,uint32_t size,void *storage,void *control,uint32_t type); /* selected 0x4415ca */
extern uint32_t audio_uart_queue_send(void *queue,const void *item,uint32_t ticks,uint32_t position); /* 0x4417ee */
static void mutex_initialize(void *mutex)
{
    if (!mutex) return;
    uint8_t *p=(uint8_t *)mutex;
    *(uint32_t *)(p+8u)=0u;
    *(uint32_t *)(p+0u)=0u;
    *(uint32_t *)(p+12u)=0u;
    (void)audio_uart_queue_send(mutex,0,0u,0u);
}
void *audio_uart_mutex_dynamic_create(uint32_t type)
{
    void *mutex=audio_queue_create_dynamic(1u,0u,(uint8_t)type);
    mutex_initialize(mutex);
    return mutex;
}
void *audio_uart_mutex_static_create(uint32_t type,void *storage)
{
    void *mutex=audio_queue_create_static(1u,0u,0,storage,(uint8_t)type);
    mutex_initialize(mutex);
    return mutex;
}
