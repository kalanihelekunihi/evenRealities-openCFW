/* Default backend, second-change callback and native clock constructor.
 * Snapshot/bind have a separate C owner in native_clock_binding.c.
 * The normal source composition uses the verified C constructor/callback ABI. */
#include <string.h>
#include "native_clock_bootstrap.h"
#include "native_battery_memory.h"
extern time_calendar_registration r1_time_registration;
extern time_calendar_state r1_time_state;
extern uint32_t r1_time_backend_timestamp(void);
extern uint32_t r1_structured_log_timestamp_adapter(void);
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
extern uint64_t r1_clock_backend_slot12(void);
extern uint32_t r1_clock_backend_slot20(time_calendar_datetime *);
extern uint32_t r1_clock_backend_slot24(const time_calendar_datetime *);
extern int32_t r1_clock_backend_update(uint32_t,int32_t,void *);
extern uint32_t r1_clock_backend_bind_tick(uint32_t,uint32_t,uint32_t,r1_clock_tick_fn);
static int32_t default_init(void *context){(void)context;return 1;}
static int32_t default_deinit(void *context){(void)context;return 1;}
static uint32_t default_get(void *context){(void)context;return r1_structured_log_timestamp_adapter();}
/* Native backend slot +12 goes through the branch veneer at 0x50d82. */
static uint64_t default_read64(void){return r1_clock_backend_slot12();}
const r1_native_clock_ops r1_clock_default_backend __attribute__((section(".r1.clock.backend")))={
    {{(uintptr_t)default_init,(uintptr_t)default_deinit},default_get,(uintptr_t)default_read64,r1_clock_backend_update},
    (uintptr_t)r1_clock_backend_slot20,(uintptr_t)r1_clock_backend_slot24,r1_clock_backend_bind_tick
};
const r1_clock_boot_config r1_clock_boot_defaults __attribute__((section(".r1.clock.defaults")))={480,0,0};
_Static_assert(sizeof(r1_native_clock_ops)==32,"native eight-slot backend");
_Static_assert(sizeof(r1_clock_boot_config)==8,"native boot configuration");
_Static_assert(offsetof(time_calendar_registration,snapshot_backend)==16,"snapshot binding");
_Static_assert(offsetof(time_calendar_registration,context)==20,"snapshot context");
const r1_native_clock_ops *r1_clock_default_backend_get(void){return &r1_clock_default_backend;}
void r1_clock_second_changed(uint32_t incoming_payload)
{
    uint32_t now=r1_time_backend_timestamp();
    if (now!=r1_time_state.reserved_00[1]) (void)r1_event_publish(4,&incoming_payload,1);
}
uint32_t r1_clock_initialize(const r1_clock_boot_config *config,void *incoming_r1)
{
    volatile uint8_t *state=(volatile uint8_t *)&r1_time_state;
    if (state[10]) return 1;
    const volatile uint8_t *input=(const volatile uint8_t *)(config?config:&r1_clock_boot_defaults);
    uint32_t offset_word=read32(input),epoch=read32(input+4);
    write32(state,offset_word);
    write32(state+4,epoch);
    write16(state+8,read16(state));
    /* Normal Clang reserves the native 24-byte frame with context/ops at +0/+4.
     * Volatile reloads preserve callbacks that change these exposed slots. */
    union { struct { void *context; const r1_native_clock_ops *ops; }; uint64_t padding[2]; } volatile saved;
    saved.context=incoming_r1;
    if (!r1_clock_backend_snapshot((const r1_native_clock_ops **)&saved.ops,(void **)&saved.context)) {
        saved.ops=r1_clock_default_backend_get();
        if (!saved.ops) return 0;
        (void)r1_clock_backend_bind(saved.ops,0);
    }
    if (saved.ops) {
        int32_t (*init)(void *)=(int32_t (*)(void *))(uintptr_t)read32((const volatile uint8_t *)saved.ops);
        if (init && !init(saved.context)) return 0;
        if (saved.ops) {
            int32_t (*update)(uint32_t,int32_t,void *)=saved.ops->prefix.update;
            if (update) (void)update(read32(state+4),read16(state),saved.context);
            if (saved.ops) {
                uint32_t (*bind_tick)(uint32_t,uint32_t,uint32_t,r1_clock_tick_fn)=saved.ops->bind_tick;
                if (bind_tick) (void)bind_tick(0,0,0,r1_clock_second_changed);
            }
        }
    }
    write32((volatile uint8_t *)&r1_time_registration+8,(uint32_t)(uintptr_t)saved.ops);
    memset((void *)(state+12),0,20);
    state[10]=1;
    return 1;
}
