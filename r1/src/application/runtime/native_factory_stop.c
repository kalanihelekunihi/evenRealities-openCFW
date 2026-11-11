/* Stock 0x48c68. Only the separately observed 12-byte reset cache is owned
 * here; the existing 28-byte mode state remains its canonical owner. */
#include <stdint.h>
#include "native_factory_mode.h"
extern uint32_t r1_stream_timer_release(volatile uint32_t *);
extern void r1_kv_nv_r1_word_set_a(uint32_t);
extern void r1_sensor_stream_unregister_by_name(const char *,uint32_t);
volatile uint32_t r1_factory_reset_cache[3]
 __attribute__((section(".r1.factory.reset.cache"),aligned(4)));
uint32_t r1_factory_mode_stop(void)
{
    if(!r1_factory_mode_state.active)return 0;
    r1_factory_mode_state.active=0;
    uint32_t timer=r1_factory_mode_state.timer;
    if(timer){
        (void)r1_stream_timer_release((volatile uint32_t *)(uintptr_t)timer);
        r1_factory_mode_state.timer=0;
    }
    uint32_t saved=r1_factory_mode_state.saved_configuration;
    uint32_t configuration=r1_factory_mode_state.configuration;
    if(configuration!=saved){
        r1_factory_mode_state.saved_configuration=configuration;
        r1_kv_nv_r1_word_set_a(configuration);
    }
    uint32_t aging=r1_factory_mode_state.aging;
    if(aging){
        r1_sensor_stream_unregister_by_name("aging",aging);
        r1_factory_mode_state.aging=0;
    }
    uint32_t acc=r1_factory_mode_state.acc;
    if(acc){
        r1_sensor_stream_unregister_by_name("acc",acc);
        r1_factory_mode_state.acc=0;
        if(r1_factory_mode_state.reserved[0]){
            r1_factory_mode_state.reserved[0]=0;
            r1_factory_reset_cache[2]=0;
            r1_factory_reset_cache[1]=0;
            r1_factory_reset_cache[0]=0;
            *(volatile uint16_t *)((volatile uint8_t *)&r1_factory_mode_state+6)=0;
        }
    }
    return 1;
}
