/* 0x8316c: native ingress policy with a C worker and explicit saved-word/tail
 * boundary. It does not validate CRC or advertised packet length. */
#include <stdint.h>
#include "native_battery_memory.h"
extern void r1_eus_system_dispatch_plan_build(void),r1_health_registration_dispatcher(void),r1_ble_event_dispatch(void);
volatile uintptr_t r1_protocol_module_dispatch[4]
    __attribute__((section(".r1.protocol.modules"))) = {
        0,(uintptr_t)&r1_eus_system_dispatch_plan_build,
        (uintptr_t)&r1_health_registration_dispatcher,0
    };
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern void nrf_log_frontend_std_4(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t);
const char r1_protocol_ingress_ring[] __attribute__((section(".r1.protocol_ingress.ring")))="[RING]ble proto rx:handle:%d, cmd:0x%06x, mask:%d, seq:%d";
const char r1_protocol_ingress_sdk[] __attribute__((section(".r1.protocol_ingress.sdk")))="ble proto rx:handle:%d, cmd:0x%06x, mask:%d, seq:%d";
#define CAPTURE_SCRATCH() do { \
    register uint32_t native2 __asm__("r2"),native3 __asm__("r3"); \
    __asm__ volatile("" : "=r"(native2), "=r"(native3) : : "memory"); \
    scratch2=native2;scratch3=native3; \
} while(0)
#define MODE_GET(destination) do { \
    register uint32_t input2 __asm__("r2")=scratch2,input3 __asm__("r3")=scratch3; \
    __asm__ volatile("" : "+r"(input2), "+r"(input3) : : "memory"); \
    destination=r1_structured_log_mode_get();CAPTURE_SCRATCH(); \
} while(0)
static __attribute__((used,noinline)) uint32_t ingress_worker(uint32_t handle,volatile uint32_t *saved)
{
    const volatile uint8_t *packet=(const volatile uint8_t *)(uintptr_t)saved[0];
    uint32_t length=saved[1],scratch2=length,scratch3=saved[2],result=handle;
    uintptr_t target=0;
    if(!packet || length<12u) goto finished;
    result=packet[0];if(result!=100u) goto finished;
    result=packet[2];if(result<100u) goto finished;
    result=packet[1];if(result>=4u && result!=127u) goto finished;
    uint32_t command=result<<16;command|=(uint32_t)packet[6]<<8;command|=packet[7];
    uint32_t mode;MODE_GET(mode);
    uint32_t ring=mode&1u;
    if(!ring) { MODE_GET(mode);ring=mode&4u; }
    if(ring) {
        uint32_t sequence=read16(packet+3),flags=packet[5];
        saved[0]=command;saved[1]=flags;saved[2]=sequence;
        (void)r1_structured_log_format(0x0d000000,r1_protocol_ingress_ring,r1_protocol_ingress_ring,handle,command,flags,sequence);CAPTURE_SCRATCH();
    }
    MODE_GET(mode);
    if(mode&2u) {
        uint32_t sequence=read16(packet+3),flags=packet[5];
        saved[0]=flags;saved[1]=sequence;
        nrf_log_frontend_std_4(0x001c0003,r1_protocol_ingress_sdk,handle,command,flags,sequence);CAPTURE_SCRATCH();
    }
    result=packet[1];
    if(result==127u) target=(uintptr_t)&r1_ble_event_dispatch;
    else {
        /* Reload after callbacks; preserve native out-of-table access if a
         * logger changed the module. No extra validation is inserted here. */
        target=read32((const volatile uint8_t *)((uintptr_t)r1_protocol_module_dispatch+result*4u));
        scratch2=(uint32_t)target;
    }
    if(target) result=(uint16_t)handle;
finished:
    {
        register uint32_t out0 __asm__("r0")=result;
        register uintptr_t out1 __asm__("r1")=(uintptr_t)packet;
        register uint32_t out2 __asm__("r2")=scratch2,out3 __asm__("r3")=scratch3;
        register uintptr_t out12 __asm__("r12")=target;
        __asm__ volatile("" : "+r"(out0), "+r"(out1), "+r"(out2), "+r"(out3), "+r"(out12));
        return out0;
    }
}
/* Original saved argument words are also the native logger's outgoing words.
 * The C worker models their writes; this wrapper restores them on rejection or
 * performs the original tail handoff after restoring callee-saved state. */
__attribute__((naked)) uint32_t r1_eus_ingress_plan_decode(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)),uint32_t length __attribute__((unused)))
{
    __asm__ volatile("push {r1,r2,r3,r4,r5,r6,r7,lr}\n"
                     "mov r1,sp\n"
                     "bl ingress_worker\n"
                     "cmp r12,#0\n"
                     "bne 1f\n"
                     "pop {r1,r2,r3,r4,r5,r6,r7,pc}\n"
                     "1: add sp,#12\n"
                     "pop {r4,r5,r6,r7,lr}\n"
                     "bx r12\n");
}
