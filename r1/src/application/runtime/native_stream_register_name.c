/* Stock R1 0x897e8: lookup, forward all registration words, or log and zero. */
#include <stdint.h>
#include <stddef.h>
extern void *r1_stream_object_lookup(const char *);
extern uint32_t r1_sensor_stream_register_object(void *,const char *,uintptr_t,uint32_t,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
uint32_t r1_sensor_stream_register_by_name(const char *name,const char *group,uintptr_t callback,uint32_t order,uint32_t flags)
{
    volatile uint32_t saved_flags=flags;
    void *object=r1_stream_object_lookup(name);
    if (object) {
        volatile uint32_t result=r1_sensor_stream_register_object(object,group,callback,order,saved_flags);
        return result;
    }
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x04400000,"[RING]register not find obj:%s","[RING]register not find obj:%s",name);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0001,"register not find obj:%s",(uint32_t)(uintptr_t)name);
    return 0;
}
