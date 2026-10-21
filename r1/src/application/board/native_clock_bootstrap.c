/* Supplemental native contracts at5a988/5a990/5a9b4/5a9d0/8adc0.
 * Snapshot binding is distinct from the timestamp fast-path binding.
 * Unimplemented default-port callbacks remain explicit providers. */
#include <string.h>
#include "native_clock_bootstrap.h"
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
const r1_native_clock_ops r1_clock_default_backend __attribute__((section(".r1.clock.backend")))={
    {{(uintptr_t)default_init,(uintptr_t)default_deinit},default_get,(uintptr_t)r1_clock_backend_slot12,r1_clock_backend_update},
    (uintptr_t)r1_clock_backend_slot20,(uintptr_t)r1_clock_backend_slot24,r1_clock_backend_bind_tick
};
const r1_clock_boot_config r1_clock_boot_defaults __attribute__((section(".r1.clock.defaults")))={480,0,0};
_Static_assert(sizeof(r1_native_clock_ops)==32,"native eight-slot backend");
_Static_assert(sizeof(r1_clock_boot_config)==8,"native boot configuration");
_Static_assert(offsetof(time_calendar_registration,snapshot_backend)==16,"snapshot binding");
_Static_assert(offsetof(time_calendar_registration,context)==20,"snapshot context");
const r1_native_clock_ops *r1_clock_default_backend_get(void){return &r1_clock_default_backend;}
uint32_t r1_clock_backend_snapshot(const r1_native_clock_ops **out,void **context)
{
    if (((0u-(uint32_t)r1_time_registration.backend_registered)&(uintptr_t)r1_time_registration.snapshot_backend)==0) return 0;
    if (out) *out=(const r1_native_clock_ops *)r1_time_registration.snapshot_backend;
    if (context) *context=r1_time_registration.context;
    return 1;
}
uint32_t r1_clock_backend_bind(const r1_native_clock_ops *ops,void *context)
{
    if (!ops || !ops->prefix.get) return 0;
    r1_time_registration.snapshot_backend=&ops->prefix;
    r1_time_registration.context=context;
    r1_time_registration.backend_registered=1;
    return 1;
}
void r1_clock_second_changed(uint32_t incoming_payload)
{
    uint32_t now=r1_time_backend_timestamp();
    if (now!=r1_time_state.reserved_00[1]) (void)r1_event_publish(4,&incoming_payload,1);
}
uint32_t r1_clock_initialize(const r1_clock_boot_config *config,void *incoming_r1)
{
    if (r1_time_state.registered) return 1;
    if (!config) config=&r1_clock_boot_defaults;
    memcpy(r1_time_state.reserved_00,config,8);
    r1_time_state.utc_offset_minutes=(int16_t)config->offset;
    const r1_native_clock_ops *ops=0;
    void *context=incoming_r1; /* Native saved incoming R1 survives failed snapshot. */
    if (!r1_clock_backend_snapshot(&ops,&context)) {
        ops=r1_clock_default_backend_get();
        if (!ops) return 0;
        (void)r1_clock_backend_bind(ops,0);
    }
    if (ops) {
        int32_t (*init)(void *);memcpy(&init,&ops->prefix.reserved_00[0],sizeof(init));
        if (init && !init(context)) return 0;
        if (ops->prefix.update) (void)ops->prefix.update(r1_time_state.reserved_00[1],(uint16_t)r1_time_state.reserved_00[0],context);
        if (ops->bind_tick) (void)ops->bind_tick(0,0,0,r1_clock_second_changed);
    }
    r1_time_registration.backend=ops?&ops->prefix:0;
    memset((uint8_t *)&r1_time_state+12,0,20);
    r1_time_state.registered=1;
    return 1;
}
