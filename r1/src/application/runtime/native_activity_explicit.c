#include "native_activity_accumulator.h"
#include "../board/native_battery_memory.h"
extern uint32_t r1_time_backend_timestamp(void),r1_time_local_day_start(void);
extern uint32_t r1_activity_mode_byte_get(void),r1_health_mode_get(void),r1_health_mode_is_2(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
static void rebase(void)
{
    volatile uint8_t *state=r1_activity_accumulator_state;
    uint32_t first=read32(state+16),second=read32(state+20);
    write32(state+8,first);write32(state+12,second);
}
void r1_activity_explicit_refresh_accumulator(void)
{
    volatile uint8_t *state=r1_activity_accumulator_state;
    uint32_t now=r1_time_backend_timestamp();
    if(r1_activity_mode_byte_get()==1 || !r1_health_mode_get()){
        rebase();state[1]=0;return;
    }
    if(!r1_health_mode_is_2()){
        if(!state[1]){state[1]=1;write32(state+4,now);return;}
        if(now-read32(state+4)<=900u)return;
        rebase();state[1]=0;return;
    }
    state[1]=0;
    (void)r1_time_local_day_start();
    uint32_t current=read32(state+16),baseline=read32(state+8);
    if(current<baseline || read16(state+22)<read16(state+14) || read16(state+20)<read16(state+12)){
        rebase();
        const char *ring="[RING]algo activity rollback, rebase";
        if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
            (void)r1_structured_log_format(0x0c000000,ring,ring);
        if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,"algo activity rollback, rebase");
        return;
    }
    _Alignas(4) uint8_t event[12]={0};
    write16(event,read16(state+20)-read16(state+12));
    write16(event+2,read16(state+22)-read16(state+14));
    write16(event+4,current-baseline);
    write16(event+6,now%600u);write32(event+8,now);
    (void)r1_event_publish(11,event,12);
    rebase();
}
extern void r1_event_service_00049068(void) __attribute__((alias("r1_activity_explicit_refresh_accumulator")));
