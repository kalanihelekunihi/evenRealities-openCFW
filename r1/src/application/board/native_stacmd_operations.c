#include "native_stacmd.h"
#include <stdint.h>
#include "native_battery_memory.h"
static volatile uint8_t *configuration(void) { return (volatile uint8_t *)&r1_stacmd; }
uint32_t r1_stacmd_open(generic_device_registry_device *device)
{
    (void)device;
    if (!configuration()[4]) configuration()[4]=1;
    return 0;
}
uint32_t r1_stacmd_close(generic_device_registry_device *device)
{
    (void)device;
    if (configuration()[4]) configuration()[4]=0;
    return 0;
}
uint32_t r1_stacmd_read(generic_device_registry_device *device,uintptr_t unused,uintptr_t request_address,uintptr_t flags)
{
    const volatile uint8_t *request=(const volatile uint8_t *)request_address;
    (void)device;(void)unused;(void)flags;
    if (!request) return 11;
    if (!configuration()[4]) return 29;
    uint32_t reg=request[0],length=request[16];
    uint8_t *buffer=(void *)(uintptr_t)read32(request+12);
    for (uint32_t attempt=0;attempt<9;attempt++) {
        r1_stacmd_bus_recovery_native();
        if (r1_stacmd_read_frame_native(0x44,reg,length,buffer)) return 0;
        r1_stacmd_failed_transactions=r1_stacmd_failed_transactions+1;
    }
    for (uint32_t i=0;i<length;i++) buffer[i]=0xff;
    return 31;
}
uint32_t r1_stacmd_write(generic_device_registry_device *device,uintptr_t unused,uintptr_t request_address,uintptr_t flags)
{
    const volatile uint8_t *request=(const volatile uint8_t *)request_address;
    (void)device;(void)unused;(void)flags;
    if (!request) return 11;
    if (!configuration()[4]) return 27;
    uint32_t length=request[8];
    const uint8_t *buffer=(void *)(uintptr_t)read32(request+4);
    uint32_t reg=request[0];
    return r1_stacmd_write_retry_native(reg,length,buffer) ? 0 : 30;
}
