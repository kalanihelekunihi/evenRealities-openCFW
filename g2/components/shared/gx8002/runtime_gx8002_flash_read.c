/* SPDX-License-Identifier: MIT */
/* Recovered package0x15830. Signed chunk selection intentionally preserves
 * stock behavior for lengths with bit31 set; callback results are ignored. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
int open_cfw_gx8002_flash_read(unsigned address,void *buffer,unsigned length)
{
    uintptr_t destination=(uintptr_t)buffer;
    open_cfw_gx8002_flash_wait_ready();
    while (length) {
        unsigned chunk=(int32_t)length<65536 ? length : 65536u;
        open_cfw_gx8002_flash_state.read_words(address,(uint32_t *)destination,chunk);
        length-=chunk;
        address+=chunk;
        destination+=chunk;
    }
    return 0;
}
