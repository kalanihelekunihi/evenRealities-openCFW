/* Stock R1 0x89ba8 (shared continuation) and 0x8a180. */
#include <stdint.h>
#include "../board/native_watchdog.h"
extern void r1_stream_list_unlink(struct r1_native_list *,void *);
extern uint32_t vPortFree(void *);
extern uint32_t r1_native_list_empty(struct r1_native_list *);
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern uint32_t r1_stream_object_rate_reduce(void *);
uint32_t r1_stream_object_stop(void *owner,uint32_t context)
{
    volatile uint32_t *object=owner;
    if(!object)return 0;
    uint32_t timer=object[8];
    if(timer){
        (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
        object[8]=0;
    }
    uint32_t ops=object[3];
    if(!ops)return 0;
    uint32_t callback=((volatile uint32_t *)(uintptr_t)ops)[1];
    if(!callback)return ops;
    return ((uint32_t (*)(uint32_t))(uintptr_t)callback)(context);
}
uint32_t r1_stream_deferred_cleanup(void *owner)
{
    volatile uint8_t *object=owner;
    if(!object)return 0;
    struct r1_native_list *list=(struct r1_native_list *)(uintptr_t)(object+44);
    void *node=r1_native_list_head(list);
    while(node){
        /* Capture next before unlink/free, then read the fresh mark byte. */
        void *next=r1_native_list_next(list,node);
        if(((volatile uint8_t *)node)[20]&1u){
            r1_stream_list_unlink(list,node);
            (void)vPortFree(node);
        }
        node=next;
    }
    object[40]&=(uint8_t)~4u;
    if(r1_native_list_empty(list)){
        uint32_t buffer=((volatile uint32_t *)object)[5];
        if(buffer){
            (void)vPortFree((void *)(uintptr_t)buffer);
            ((volatile uint32_t *)object)[5]=0;
            ((volatile uint32_t *)object)[6]=0;
        }
        return r1_stream_object_stop(owner,((volatile uint32_t *)object)[9]);
    }
    return r1_stream_object_rate_reduce(owner);
}
