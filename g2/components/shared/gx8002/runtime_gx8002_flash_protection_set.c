/* SPDX-License-Identifier: MIT */
/* Candidate recovered from package 0x159b8..0x15aa4; not admitted. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_write_enable(void);
extern unsigned open_cfw_gx8002_flash_read_status(void);
extern unsigned open_cfw_gx8002_flash_read_status2(void);
extern int open_cfw_gx8002_flash_command_write(unsigned,const uint8_t *,unsigned);
extern int open_cfw_gx8002_flash_write_protect_status(unsigned *);
/* Ordered, zero-extending CK804 byte load; no encoded instruction bytes. */
static inline unsigned read_byte(volatile uint8_t *address,unsigned offset)
{
    unsigned value;
    __asm__ volatile ("ld.b %0, (%1, %2)" : "=r"(value) : "r"(address), "i"(offset) : "memory");
    return value;
}
int open_cfw_gx8002_flash_write_protect_set(unsigned requested,unsigned *actual)
{
    volatile uint8_t command[2]={0,0};
    volatile uint32_t *device=(volatile uint32_t *)open_cfw_gx8002_flash_state.selected_device;
    volatile uint32_t *profile=(volatile uint32_t *)(uintptr_t)device[4];
    *actual=0;
    if (!profile || !profile[0]) return requested ? -1 : 0;
    unsigned identifier=device[1];
    open_cfw_gx8002_flash_wait_ready();
    device=(volatile uint32_t *)open_cfw_gx8002_flash_state.selected_device;
    profile=(volatile uint32_t *)(uintptr_t)device[4];
    volatile uint8_t *entry=(volatile uint8_t *)(uintptr_t)profile[0];
    unsigned count=profile[1];
    unsigned value1=0,value2=0,mask1=0,mask2=0;
    for (unsigned i=0;i!=count;++i,entry+=8) {
        unsigned length=((volatile uint32_t *)entry)[1];
        if (requested<length) break;
        value1=read_byte(entry,0);
        value2=read_byte(entry,2);
        mask1=read_byte(entry,1);
        mask2=read_byte(entry,3);
    }
    unsigned manufacturer=identifier>>16;
    if (manufacturer!=0x5e && manufacturer!=0x85) return -1;
    command[0]=(uint8_t)((open_cfw_gx8002_flash_read_status()&~mask1)|value1);
    command[1]=(uint8_t)((open_cfw_gx8002_flash_read_status2()&~mask2)|value2);
    open_cfw_gx8002_flash_wait_ready();
    open_cfw_gx8002_flash_write_enable();
    open_cfw_gx8002_flash_command_write(1,(const uint8_t *)command,2);
    open_cfw_gx8002_flash_wait_ready();
    unsigned observed;
    int result=open_cfw_gx8002_flash_write_protect_status(&observed);
    if (result==-1) return result;
    *actual=observed;
    return 0;
}
int open_cfw_gx8002_flash_write_protect_lock(unsigned requested)
{
    unsigned actual;
    return open_cfw_gx8002_flash_write_protect_set(requested,&actual);
}
int open_cfw_gx8002_flash_write_protect_unlock(void)
{
    unsigned actual;
    return open_cfw_gx8002_flash_write_protect_set(0,&actual);
}
