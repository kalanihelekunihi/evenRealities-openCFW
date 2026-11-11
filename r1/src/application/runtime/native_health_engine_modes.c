/* Stock state-mode/profile activation and their shared state setters. */
#include "native_health_engine_modes.h"
#include "gomore_primitives/gomore_primitives.h"
#include <stdbool.h>
#include <stddef.h>
extern volatile uint32_t r1_gomore_native_context;
static void slot_store(volatile uint8_t *at,uint32_t requested,uint32_t guarded) {
    uint8_t current=*at;
    if (guarded==1u) {
        if (current==4u) { if (requested==5u) *at=1; }
        else *at=(uint8_t)requested;
    } else if (current!=3u && current!=4u) *at=(uint8_t)requested;
}
uint32_t r1_gomore_profile_slot_native(uint32_t base,uint32_t slot,uint32_t requested,uint32_t guarded) {
    slot_store((volatile uint8_t *)(uintptr_t)(base+slot+0x3845u),requested,guarded);
    return 0;
}
void gomore_primitives_slot_state_transition(uint8_t *state,uint8_t requested,bool guarded) {
    if (state) slot_store(state,requested,guarded?1u:0u);
}
uint32_t r1_gomore_mode_threshold_native(uint32_t base,uint32_t value) {
    union {uint32_t u;float f;} threshold;
    threshold.u=value ? UINT32_C(0x3c54fdf4) : UINT32_C(0x3c23d70a);
    *(volatile float *)(uintptr_t)(base+0x7cu)=threshold.f;
    return 0;
}
uint32_t r1_gomore_mode_value_store_native(uint32_t base,uint32_t value) {
    if ((int32_t)value>=3) return 0x41;
    *(volatile uint32_t *)(uintptr_t)base=value;
    return 0;
}
uint32_t r1_gomore_mode_code_valid_native(uint32_t unused,uint32_t value) {
    (void)unused;
    return value<=3u || (value>=100u && value<=105u);
}
uint32_t r1_gomore_mode_code_set_native(uint32_t base,uint32_t value) {
    if (!r1_gomore_mode_code_valid_native(base,value)) return 0x40;
    *(volatile uint8_t *)(uintptr_t)(base+0x20f5u)=(uint8_t)value;
    return 0;
}
uint32_t r1_gomore_mode_checked_store_native(uint32_t base,uint32_t value) {
    if (*(volatile int32_t *)(uintptr_t)base>=3) return 0x42;
    *(volatile uint32_t *)(uintptr_t)base=value;
    return 0;
}
uint32_t r1_health_lifecycle_mode_native(uint32_t mode,uint32_t value) {
    uint32_t base=r1_gomore_native_context,status;
    switch (mode) {
    case 0: status=r1_gomore_mode_threshold_native(base+0xd14u,(uint8_t)value);break;
    case 1: status=r1_gomore_mode_code_set_native(base+0x13f8u,(uint8_t)value);break;
    case 2: status=r1_gomore_mode_value_store_native(base+0xd98u,value);break;
    case 3: status=r1_gomore_mode_checked_store_native(base+0x391cu,value);break;
    default:return UINT32_MAX;
    }
    return status ? UINT32_MAX : 0;
}
static void profile_slot(uint32_t slot,uint32_t value) {
    (void)r1_gomore_profile_slot_native(r1_gomore_native_context+0x140u,slot,value,1);
}
uint32_t r1_health_lifecycle_profile_apply_native(uint32_t profile,uint32_t selector,uint32_t fallback) {
    uint32_t base=r1_gomore_native_context;
    *(volatile uint32_t *)(uintptr_t)(base+0x39d4u)=profile;
    uint32_t requested=selector==0?4u:selector==1?5u:fallback;
    switch (profile) {
    case 0:profile_slot(0x11,0);profile_slot(1,3);break;
    case 1:profile_slot(0x11,3);profile_slot(1,0);break;
    case 2:profile_slot(0x20,3);profile_slot(0x11,0);profile_slot(1,3);break;
    case 11:profile_slot(0x45,requested);break;
    default:*(volatile uint32_t *)(uintptr_t)(base+0x39d4u)=UINT32_MAX;return UINT32_MAX;
    }
    return 0;
}
