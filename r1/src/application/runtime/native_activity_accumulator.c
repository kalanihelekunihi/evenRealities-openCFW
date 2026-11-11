#include "native_activity_accumulator.h"
#include "../board/native_battery_memory.h"
/* Authenticated zero-initialized block; ends before activity mode at 0x20006ed4. */
volatile uint8_t r1_activity_accumulator_state[24]
    __attribute__((section(".r1.activity.accumulator"),aligned(4)))={0};

/* Stock 0x491bc: return the latest eight-byte accumulator snapshot. */
void r1_activity_accumulator_latest_copy(volatile void *output)
{
    if (output != 0) {
        volatile uint8_t *const destination = output;
        const uint32_t first = read32(r1_activity_accumulator_state + 16);
        const uint32_t second = read32(r1_activity_accumulator_state + 20);
        write32(destination, first);
        write32(destination + 4, second);
    }
}
extern uint32_t r1_time_backend_timestamp(void),r1_time_local_day_start(void);
extern uint32_t r1_activity_mode_byte_get(void),r1_health_mode_get(void),r1_health_mode_is_2(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
static void copy8(volatile uint8_t *to,const volatile uint8_t *from)
{
    uint32_t first=read32(from),second=read32(from+4);
    write32(to,first);write32(to+4,second);
}
static void log_reset(uint32_t rollback)
{
    const char *ring=rollback?"[RING]algo activity rollback, rebase":"[RING]algo activity clean";
    const char *sdk=rollback?"algo activity rollback, rebase":"algo activity clean";
    if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(0x0c000000,ring,ring);
    if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,sdk);
}
void r1_activity_periodic_accumulator(volatile void *input)
{
    if(!input)return;
    volatile uint8_t *sample=input,*state=r1_activity_accumulator_state;
    uint32_t now=r1_time_backend_timestamp(),day=r1_time_local_day_start();
    uint32_t bucket=now-now%600u;
    if(now==day){copy8(state+8,sample);log_reset(0);}
    copy8(state+16,sample);
    if(r1_activity_mode_byte_get()==1 || !r1_health_mode_get()){
        copy8(state+8,sample);state[1]=0;return;
    }
    if(!r1_health_mode_is_2()){
        if(!state[1]){state[1]=1;write32(state+4,now);return;}
        if(now-read32(state+4)<=900u)return;
        copy8(state+8,sample);state[1]=0;return;
    }
    state[1]=0;
    if(now<bucket+595u){state[0]=0;return;}
    if(state[0])return;
    uint32_t current=read32(sample),baseline=read32(state+8);
    if(current<baseline || read16(sample+6)<read16(state+14) || read16(sample+4)<read16(state+12)){
        copy8(state+8,sample);log_reset(1);state[0]=1;return;
    }
    _Alignas(4) uint8_t event[12]={0};
    write16(event,read16(sample+4)-read16(state+12));
    write16(event+2,read16(sample+6)-read16(state+14));
    write16(event+4,read16(sample)-baseline);
    write16(event+6,now-bucket);write32(event+8,now);
    (void)r1_event_publish(11,event,12);
    copy8(state+8,sample);state[0]=1;
}
