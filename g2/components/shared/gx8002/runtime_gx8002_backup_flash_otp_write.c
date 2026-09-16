/* SPDX-License-Identifier: MIT */
/* Recovered backup package 0x401c4. Preserve wrapped bounds and page splitting. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_command_write(unsigned,const uint8_t *,unsigned);
static inline uint8_t address_byte(unsigned address,unsigned width,unsigned index)
{
    unsigned shift=((width-index)*8u)&63u;
    return shift<32u ? (uint8_t)(address>>shift) : 0;
}
static inline __attribute__((always_inline)) void encode(unsigned address,unsigned width)
{
    for (unsigned i=1;i<=4;++i)
        open_cfw_gx8002_flash_state.command[i]=address_byte(address,width,i);
}
extern int open_cfw_gx8002_flash_otp_transmit(unsigned,const uint8_t *,unsigned);
int open_cfw_gx8002_flash_otp_write(unsigned offset,const uint8_t *buffer,unsigned length)
{
    uintptr_t device=open_cfw_gx8002_flash_state.selected_device;
    uintptr_t descriptor=*(volatile uint32_t *)(device+20);
    unsigned region=*(volatile uint32_t *)(descriptor+16)&7;
    if (!length) return -1;
    unsigned size=*(volatile uint32_t *)(descriptor+8);
    if (offset+length>size) return -1;
    unsigned address=*(volatile uint32_t *)descriptor+offset;
    unsigned stride=*(volatile uint32_t *)(descriptor+4);
    address+=region*stride;
    int manufacturer=*(volatile int16_t *)(device+6);
    if (manufacturer!=0x5e && manufacturer!=0x85) return -1;
    open_cfw_gx8002_flash_wait_ready();
    open_cfw_gx8002_flash_command_write(6,0,0);
    open_cfw_gx8002_flash_state.command[0]=0x42;
    unsigned width=open_cfw_gx8002_flash_state.address_bytes;
    open_cfw_gx8002_flash_state.command[1]=address_byte(address,width,1);
    open_cfw_gx8002_flash_state.command[2]=address_byte(address,width,2);
    open_cfw_gx8002_flash_state.command[4]=address_byte(address,width,4);
    open_cfw_gx8002_flash_state.command[3]=address_byte(address,width,3);
    unsigned page_offset=address&255;
    unsigned result;
    if (length+page_offset<=256) {
        open_cfw_gx8002_flash_otp_transmit(width+1,buffer,length);
        result=length;
    } else {
        result=256-page_offset;
        open_cfw_gx8002_flash_otp_transmit(width+1,buffer,result);
        unsigned done=result;
        while (done<length) {
            encode(address+done,open_cfw_gx8002_flash_state.address_bytes);
            open_cfw_gx8002_flash_wait_ready();
            unsigned chunk=length-done;
            open_cfw_gx8002_flash_command_write(6,0,0);
            if (chunk>256) chunk=256;
            open_cfw_gx8002_flash_otp_transmit(open_cfw_gx8002_flash_state.address_bytes+1,
                (const uint8_t *)((uintptr_t)buffer+done),chunk);
            if (result) result+=chunk;
            done+=chunk;
        }
    }
    open_cfw_gx8002_flash_wait_ready();
    return (int)result;
}
