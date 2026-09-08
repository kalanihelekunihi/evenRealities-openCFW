/* SPDX-License-Identifier: MIT */
/* Recovered package 0x15af4. Snapshot region before waiting, but reload the
 * selected device afterward. Unsupported manufacturers leave output untouched. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_read_status2(void);
int open_cfw_gx8002_flash_otp_status(uint8_t *locked)
{
    uintptr_t device=open_cfw_gx8002_flash_state.selected_device;
    uintptr_t descriptor=*(volatile uint32_t *)(device+20);
    uint32_t flags=*(volatile uint32_t *)(descriptor+16);
    open_cfw_gx8002_flash_wait_ready();
    device=open_cfw_gx8002_flash_state.selected_device;
    int manufacturer=*(volatile int16_t *)(device+6);
    if (manufacturer!=0x5e && manufacturer!=0x85) return -1;
    unsigned status=(unsigned)open_cfw_gx8002_flash_read_status2();
    *locked=(uint8_t)((status>>((flags&7)+3))&1);
    return 0;
}
