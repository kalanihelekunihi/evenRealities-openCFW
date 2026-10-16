/* Native device information0x83d5c and operation2 wrapper0x83872.
 * These are locked stock metadata strings, not an OpenCFW release identity. */
#include <stdint.h>
#include <stddef.h>
#include "native_battery_memory.h"
extern void __aeabi_memclr(void *,uint32_t);
extern int snprintf(char *,size_t,const char *,...);
extern uint32_t r1_phone_connection_handle_get(void);
extern uint32_t r1_protocol_response_send_0x100(uint32_t,uint32_t,uint32_t,uint32_t,const void *,uint32_t);
const char r1_device_info_firmware[] __attribute__((section(".r1.protocol_info.firmware")))="2.2.6.0009";
const char r1_device_info_format[] __attribute__((section(".r1.protocol_info.format")))="%s";
const char r1_device_info_hardware[] __attribute__((section(".r1.protocol_info.hardware")))="603MV1.9.3";
__attribute__((noinline)) uint32_t r1_system_response_wrapper(const void *payload,uint32_t first,uint32_t second)
{
    uint32_t incoming3;
    __asm__ volatile("mov %0, r3" : "=r"(incoming3));
    volatile uint32_t saved2=second,saved3=incoming3;
    uint32_t result=0;
    if(payload) {
        uint32_t handle=r1_phone_connection_handle_get();
        saved2=(uintptr_t)payload;saved3=32;
        result=r1_protocol_response_send_0x100(handle,2,first,second,payload,32);
    }
    uint32_t restored2=saved2,restored3=saved3;
    __asm__ volatile("mov r2, %0\nmov r3, %1" : : "r"(restored2),"r"(restored3) : "r2","r3");
    return result;
}
static __attribute__((used,noinline)) uint32_t info_worker(const volatile uint8_t *packet,volatile uint8_t *record)
{
    __aeabi_memclr((void *)record,32);
    (void)snprintf((char *)record,16,r1_device_info_format,r1_device_info_firmware);
    (void)snprintf((char *)record+16,16,r1_device_info_format,r1_device_info_hardware);
    register uint32_t native3 __asm__("r3");
    __asm__ volatile("" : "=r"(native3) : : "memory");uint32_t incoming3=native3;
    uint32_t sequence=read16(packet+3);
    register uint32_t restored3 __asm__("r3")=incoming3;
    __asm__ volatile("" : "+r"(restored3));
    uint32_t result=r1_system_response_wrapper((const void *)record,0,sequence);
    register uint32_t native1 __asm__("r1"),native2 __asm__("r2"),returned3 __asm__("r3");
    __asm__ volatile("" : "=r"(native1), "=r"(native2), "=r"(returned3) : : "memory");
    register uint32_t out0 __asm__("r0")=result;
    __asm__ volatile("" : "+r"(out0), "+r"(native1), "+r"(native2), "+r"(returned3));return out0;
}
__attribute__((naked)) uint32_t r1_device_info_handler(uint32_t handle __attribute__((unused)),const void *packet __attribute__((unused)))
{
    __asm__ volatile("push {r4,lr}\n"
                     "sub sp,#32\n"
                     "mov r0,r1\n"
                     "mov r1,sp\n"
                     "bl info_worker\n"
                     "add sp,#32\n"
                     "pop {r4,pc}\n");
}
