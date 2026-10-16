/* Authenticated event leaves: special target0x84cc0 (not a locked ledger row)
 * and activity refresh0x82c10. Source compilation does not prove event delivery. */
#include <stdint.h>
#include "native_battery_memory.h"
extern uint32_t r1_event_publish(uint32_t,const void *,uint32_t);
uint32_t r1_protocol_command_00084cc0(uint32_t handle __attribute__((unused)),const void *packet)
{
    register uint32_t incoming2 __asm__("r2"),incoming3 __asm__("r3");
    __asm__ volatile("" : "+r"(incoming2), "+r"(incoming3) : : "memory");
    uint32_t length=(uint16_t)(read16((const volatile uint8_t *)packet+8)-12u);
    uintptr_t next=(uintptr_t)packet;
    if(length) {
        next=(uint32_t)next+12u;
        if(next) {
            register uint32_t native3 __asm__("r3")=incoming3;
            __asm__ volatile("" : "+r"(native3));
            return r1_event_publish(15,(const void *)next,9);
        }
    }
    register uint32_t out0 __asm__("r0")=length,out2 __asm__("r2")=incoming2,out3 __asm__("r3")=incoming3;
    register uintptr_t out1 __asm__("r1")=next;
    __asm__ volatile("" : "+r"(out0), "+r"(out1), "+r"(out2), "+r"(out3));
    return out0;
}
static __attribute__((used,noinline)) uint32_t activity_worker(const volatile uint8_t *packet,volatile uint8_t *record,uint32_t flags,uint32_t initial_sequence)
{
    uint32_t result=flags;
    uintptr_t returned_packet=(uintptr_t)packet;
    if(flags&2u) goto finished;
    result=0;if(flags&1u) goto finished;
    record[0]=4;record[1]=0;
    uint32_t sequence=initial_sequence;
    /* The native sequence load follows its first two record-byte stores. The
     * wrapper snapshots before entering private C stack; adjust overlap here. */
    for(uint32_t i=0;i<2;i++) {
        uintptr_t address=(uint32_t)(uintptr_t)packet+3u+i;
        if(address==(uintptr_t)record) sequence=(sequence&~(255u<<(i*8)))|(4u<<(i*8));
        if(address==(uintptr_t)record+1u) sequence&=~(255u<<(i*8));
    }
    write16(record+2,sequence);
    {
        register uint32_t native3 __asm__("r3")=read32(record+4);
        __asm__ volatile("" : "+r"(native3));
        result=r1_event_publish(14,(const void *)record,8);
    }
    {
        register uintptr_t native1 __asm__("r1");
        __asm__ volatile("" : "=r"(native1) : : "memory");returned_packet=native1;
    }
finished:
    {
        register uint32_t out0 __asm__("r0")=result;
        register uintptr_t out1 __asm__("r1")=returned_packet;
        __asm__ volatile("" : "+r"(out0), "+r"(out1));return out0;
    }
}
/* The eight event bytes are the incoming r2/r3 words at the native stack
 * boundary. The incoming r3 word is retained; it is not zero-initialized padding. */
__attribute__((naked)) uint32_t r1_activity_refresh_handler(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)))
{
    __asm__ volatile("push {r2,r3,r4,lr}\n"
                     "mov r0,r1\n"
                     "mov r1,sp\n"
                     "ldrb r2,[r0,#5]\n"
                     "tst r2,#3\n"
                     "bne 1f\n"
                     "ldrh.w r3,[r0,#3]\n"
                     "b 2f\n"
                     "1: movs r3,#0\n"
                     "2: bl activity_worker\n"
                     "pop {r2,r3,r4,pc}\n");
}
