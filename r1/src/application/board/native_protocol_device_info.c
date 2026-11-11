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
    if (!payload) return 0;
    const uint32_t handle=r1_phone_connection_handle_get();
    return r1_protocol_response_send_0x100(handle,2,first,second,payload,32);
}
static uint32_t info_worker(const volatile uint8_t *packet,volatile uint8_t *record)
{
    __aeabi_memclr((void *)record,32);
    (void)snprintf((char *)record,16,r1_device_info_format,r1_device_info_firmware);
    (void)snprintf((char *)record+16,16,r1_device_info_format,r1_device_info_hardware);
    uint32_t sequence=read16(packet+3);
    return r1_system_response_wrapper((const void *)record,0,sequence);
}
/* The registered protocol entry consumes only its packet argument and
 * publishes a completely initialized 32-byte response. */
uint32_t r1_device_info_handler(uint32_t handle,const void *packet)
{
    (void)handle;
    uint8_t record[32];
    return info_worker(packet,record);
}
