/* Stock 0x89b08 name wrapper and 0x89c20 object removal body. Shared
 * deferred cleanup at 0x89ba8 is supplied by native_stream_cleanup.c. */
#include <stdint.h>
#include "../board/native_watchdog.h"
extern void *r1_stream_object_lookup(const char *);
extern void r1_stream_list_unlink(struct r1_native_list *,void *),vPortFree(void *);
extern uint32_t r1_native_list_empty(struct r1_native_list *);
extern uint32_t r1_stream_object_stop(void *,uint32_t),r1_stream_object_rate_reduce(void *);
extern _Noreturn void r1_bae8_rx_allocation_fault(void);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
void r1_sensor_stream_unregister_object(void *owner,uint32_t handle)
{
    if(!owner || !handle)r1_bae8_rx_allocation_fault();
    volatile uint8_t *object=owner;
    struct r1_native_list *list=(struct r1_native_list *)(uintptr_t)(object+44);
    for(void *node=r1_native_list_head(list);node;node=r1_native_list_next(list,node)){
        if((uint32_t)(uintptr_t)node!=handle)continue;
        if(object[40]&2u){
            volatile uint16_t *mark=(volatile uint16_t *)(uintptr_t)(handle+20u);
            *mark=(uint16_t)(*mark|1u);
            object[40]=(uint8_t)(object[40]|4u);
            return;
        }
        r1_stream_list_unlink(list,(void *)(uintptr_t)handle);
        vPortFree((void *)(uintptr_t)handle);
        if(r1_native_list_empty(list)){
            uint32_t buffer=((volatile uint32_t *)object)[5];
            if(buffer){
                vPortFree((void *)(uintptr_t)buffer);
                ((volatile uint32_t *)object)[5]=0;
                ((volatile uint32_t *)object)[6]=0;
            }
            (void)r1_stream_object_stop(owner,((volatile uint32_t *)object)[9]);
        }else (void)r1_stream_object_rate_reduce(owner);
        return;
    }
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04800000,"[RING]%s not found in %s, skip unregister","[RING]%s not found in %s, skip unregister",(const char *)(uintptr_t)(handle+4u),owner);
    if(r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_2(0x001c0001,"%s not found in %s, skip unregister",handle+4u,(uint32_t)(uintptr_t)owner);
}
void r1_sensor_stream_unregister_by_name(const char *name,uint32_t handle)
{
    void *object=r1_stream_object_lookup(name);
    if(object){r1_sensor_stream_unregister_object(object,handle);return;}
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04400000,"[RING]unregister not find obj:%s","[RING]unregister not find obj:%s",name);
    if(r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0001,"unregister not find obj:%s",(uint32_t)(uintptr_t)name);
}
