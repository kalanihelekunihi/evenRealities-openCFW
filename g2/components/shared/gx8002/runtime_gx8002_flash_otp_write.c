/* SPDX-License-Identifier: MIT */
/* Recovered package0x15ecc. Preserve wrapped bounds and page splitting. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
extern int open_cfw_gx8002_flash_wait_ready(void);
extern int open_cfw_gx8002_flash_write_enable(void);
extern void open_cfw_gx8002_flash_encode_address(const volatile uint32_t *,unsigned,uint8_t *);
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
    open_cfw_gx8002_flash_write_enable();
    open_cfw_gx8002_flash_state.command[0]=0x42;
    open_cfw_gx8002_flash_encode_address(&open_cfw_gx8002_flash_state.address_bytes,
        address,(uint8_t *)open_cfw_gx8002_flash_state.command);
    unsigned page_offset=address&255;
    unsigned result;
    if (length+page_offset<=256) {
        open_cfw_gx8002_flash_otp_transmit(open_cfw_gx8002_flash_state.address_bytes+1,buffer,length);
        result=length;
    } else {
        result=256-page_offset;
        open_cfw_gx8002_flash_otp_transmit(open_cfw_gx8002_flash_state.address_bytes+1,buffer,result);
        unsigned done=result;
        while (done<length) {
            open_cfw_gx8002_flash_encode_address(&open_cfw_gx8002_flash_state.address_bytes,
                address+done,(uint8_t *)open_cfw_gx8002_flash_state.command);
            open_cfw_gx8002_flash_wait_ready();
            unsigned chunk=length-done;
            open_cfw_gx8002_flash_write_enable();
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
