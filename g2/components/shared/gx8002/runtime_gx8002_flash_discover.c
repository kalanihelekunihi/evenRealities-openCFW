/* SPDX-License-Identifier: MIT */
/* Recovered JEDEC discovery at image-A 0x161a4. Table/state ownership is
 * separate from this function; a fallback selection still returns -2. */
#include <stdint.h>
#include <stddef.h>
struct open_cfw_flash_device {
    uint32_t name;
    uint32_t jedec;
    uint32_t usable_bytes;
    uint32_t unknown[3];
};
#include "runtime_gx8002_flash_state.h"
extern const volatile struct open_cfw_flash_device open_cfw_gx8002_flash_devices[];
extern int open_cfw_gx8002_flash_command_read(unsigned, uint8_t *, unsigned);
_Static_assert(sizeof(struct open_cfw_flash_device)==24,"device stride");

int open_cfw_gx8002_flash_discover(void)
{
    uint8_t id[3];
    open_cfw_gx8002_flash_state.device_index=-1;
    if (open_cfw_gx8002_flash_command_read(0x9f,id,3)<0) return -1;
    unsigned jedec=((unsigned)id[0]<<16)|((unsigned)id[1]<<8)|id[2];
    for (unsigned i=0; ; ++i) {
        unsigned candidate=open_cfw_gx8002_flash_devices[i].jedec;
        if (!candidate) break;
        if (candidate==jedec) {
            open_cfw_gx8002_flash_state.device_index=i;
            open_cfw_gx8002_flash_state.usable_bytes=open_cfw_gx8002_flash_devices[i].usable_bytes;
            open_cfw_gx8002_flash_state.address_bytes=3;
            open_cfw_gx8002_flash_state.selected_device=(uintptr_t)&open_cfw_gx8002_flash_devices[i];
            break;
        }
    }
    if (open_cfw_gx8002_flash_state.device_index>=0) return 0;
    for (unsigned i=0; ; ++i) {
        unsigned candidate=open_cfw_gx8002_flash_devices[i].jedec;
        if (!candidate) break;
        if (candidate==0xc22016) {
            open_cfw_gx8002_flash_state.device_index=i;
            open_cfw_gx8002_flash_state.usable_bytes=open_cfw_gx8002_flash_devices[i].usable_bytes;
            open_cfw_gx8002_flash_state.address_bytes=3;
            open_cfw_gx8002_flash_state.selected_device=(uintptr_t)&open_cfw_gx8002_flash_devices[i];
            break;
        }
    }
    return -2;
}
