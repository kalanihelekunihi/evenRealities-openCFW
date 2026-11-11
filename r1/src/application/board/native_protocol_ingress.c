/* Protocol ingress at stock 0x8316c. It admits the native packet prefix and
 * dispatches by module without adding CRC or advertised-length validation. */
#include <stdint.h>
#include "native_battery_memory.h"
extern uint32_t r1_eus_system_dispatch_plan_build(uint32_t,const void *);
extern uint32_t r1_health_registration_dispatcher(uint32_t,const void *);
extern uint32_t r1_ble_event_dispatch(uint32_t,const void *);
volatile uintptr_t r1_protocol_module_dispatch[4]
    __attribute__((section(".r1.protocol.modules"))) = {
        0,(uintptr_t)&r1_eus_system_dispatch_plan_build,
        (uintptr_t)&r1_health_registration_dispatcher,0
    };
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_protocol_ingress_ring[] __attribute__((section(".r1.protocol_ingress.ring")))=
    "[RING]ble proto rx:handle:%d, cmd:0x%06x, mask:%d, seq:%d";
const char r1_protocol_ingress_sdk[] __attribute__((section(".r1.protocol_ingress.sdk")))=
    "ble proto rx:handle:%d, cmd:0x%06x, mask:%d, seq:%d";

uint32_t r1_eus_ingress_plan_decode(uint32_t handle,const void *packet,
                                     uint32_t length)
{
    const volatile uint8_t *bytes=packet;
    if(!bytes || length<12u)return handle;
    if(bytes[0]!=100u)return bytes[0];
    if(bytes[2]<100u)return bytes[2];
    uint32_t module=bytes[1];
    if(module>=4u && module!=127u)return module;
    uint32_t command=(module<<16)|((uint32_t)bytes[6]<<8)|bytes[7];
    uint32_t mode=r1_structured_log_mode_get();
    uint32_t ring=mode&1u;
    if(!ring)ring=r1_structured_log_mode_get()&4u;
    if(ring) {
        uint32_t sequence=read16(bytes+3),flags=bytes[5];
        (void)r1_structured_log_format(0x0d000000u,r1_protocol_ingress_ring,
            r1_protocol_ingress_ring,handle,command,flags,sequence);
    }
    if(r1_structured_log_mode_get()&2u) {
        uint32_t sequence=read16(bytes+3),flags=bytes[5];
        nrf_log_frontend_std_4(0x001c0003u,r1_protocol_ingress_sdk,
            handle,command,flags,sequence);
    }
    uintptr_t target;
    if(module==127u)target=(uintptr_t)&r1_ble_event_dispatch;
    else {
        /* Keep the original integer-address lookup for malformed module
         * indices; source callers do not silently clamp the table access. */
        target=read32((const volatile uint8_t *)
            ((uintptr_t)r1_protocol_module_dispatch+module*4u));
    }
    if(!target)return module;
    return ((uint32_t (*)(uint32_t,const void *))target)((uint16_t)handle,packet);
}
