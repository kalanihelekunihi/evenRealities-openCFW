#include "native_gomore_authorization.h"
volatile struct r1_gomore_authorization_state r1_gomore_authorization_state
    __attribute__((section(".r1.gomore.authorization.state"),aligned(4)))={
        .entries={{.flags=2},{.flags=30},{.flags=30},{.flags=2},{.flags=4},{.flags=12},{.flags=0}}
    };
extern uint32_t r1_sensor_stream_register_by_name(const char *,const char *,uintptr_t,uint32_t,uint32_t);
extern uint32_t r1_sensor_stream_unregister_by_name(const char *,uint32_t);
extern uint32_t r1_stream_timer_create_back(uint32_t,uint32_t,uint32_t);
extern uint32_t r1_stream_timer_release(uint32_t);
extern uint32_t r1_gomore_acc_topic_adapter(uint32_t,volatile void *,uint32_t);
extern uint32_t r1_gomore_raw_hr_topic_adapter(uint32_t,volatile void *,uint32_t);
extern uint32_t r1_gomore_hr_topic_adapter(uint32_t,volatile void *,uint32_t);
extern uint32_t r1_gomore_hrv_topic_adapter(uint32_t,volatile void *,uint32_t);
extern uint32_t r1_gomore_idle_timer_callback(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
static __attribute__((noinline)) uint32_t auth_sensor_in_use(uint32_t mask)
{
    for (uint8_t i=0;i<7;i++) {
        uint32_t flags=r1_gomore_authorization_state.entries[i].flags;
        if ((flags&mask) && (flags&1u)) return 1;
    }
    return 0;
}
static __attribute__((noinline)) uint32_t auth_all_inactive(void)
{
    for (uint8_t i=0;i<7;i++)
        if (r1_gomore_authorization_state.entries[i].flags&1u) return 0;
    return 1;
}
static void auth_log(uint32_t tag,uint32_t sdk_tag,const char *ring,const char *sdk)
{
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        (void)r1_structured_log_format(tag,ring,ring);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_0(sdk_tag,sdk);
}
uint32_t r1_gomore_authorization_dispatch_native(uint32_t index,uint32_t enable)
{
    volatile struct r1_gomore_authorization_state *state=&r1_gomore_authorization_state;
    if (!state->ready) {
        auth_log(0x04000000,0x001c0001,"[RING]gm auth params not set","gm auth params not set");
        return 0;
    }
    if (index>=7) return 0;
    volatile struct r1_gomore_authorization_entry *entry=&state->entries[index];
    uint32_t flags=entry->flags;
    if ((flags&1u)==enable) return 0;
    static const char *const names[]={"acc","raw_hr","hr","hrv"};
    static void (*const callbacks[])(void)={(void (*)(void))r1_gomore_acc_topic_adapter,
        (void (*)(void))r1_gomore_raw_hr_topic_adapter,(void (*)(void))r1_gomore_hr_topic_adapter,
        (void (*)(void))r1_gomore_hrv_topic_adapter};
    if (enable) {
        for (uint32_t i=0;i<4;i++) {
            /* The first sensor uses the entry byte captured at equality check. */
            if (i) flags=entry->flags;
            if ((flags&(2u<<i)) && !auth_sensor_in_use(2u<<i) && !state->streams[i])
                state->streams[i]=r1_sensor_stream_register_by_name(names[i],"gomore",(uintptr_t)callbacks[i],1,0);
        }
        uint32_t callback=entry->enable_callback;
        if (callback) ((void (*)(void))(uintptr_t)callback)();
    }
    flags=entry->flags;
    flags=(flags&254u)|(enable&1u);
    entry->flags=(uint8_t)flags;
    if (!enable) {
        for (uint32_t i=0;i<4;i++) {
            if (i) flags=entry->flags;
            if ((flags&(2u<<i)) && !auth_sensor_in_use(2u<<i) && state->streams[i]) {
                (void)r1_sensor_stream_unregister_by_name(names[i],state->streams[i]);
                state->streams[i]=0;
                if (i==2) r1_gomore_authorization_samples.hr_value=0;
                if (i==3) {
                    state->hrv_count=0;state->hrv_total=0;
                    r1_gomore_authorization_samples.hrv_active=0;
                }
            }
        }
        uint32_t callback=entry->disable_callback;
        if (callback) ((void (*)(void))(uintptr_t)callback)();
    }
    if (auth_all_inactive() && !state->idle_timer) {
        state->idle_timer=r1_stream_timer_create_back((uint32_t)(uintptr_t)r1_gomore_idle_timer_callback,1000,0);
        auth_log(0x0c000000,0x001c0003,"[RING]gomore idle timer create","gomore idle timer create");
    } else if (!auth_all_inactive() && state->idle_timer) {
        (void)r1_stream_timer_release(state->idle_timer);
        state->idle_timer=0;
        auth_log(0x0c000000,0x001c0003,"[RING]gomore idle timer delete","gomore idle timer delete");
    }
    return 1;
}
