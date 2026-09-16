/* SPDX-License-Identifier: MIT */
/* Recovered backup package 0x40328. Preserve signed chunk selection,
 * width snapshots and final address encoding. Candidate awaiting decoded qualification. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern int open_cfw_gx8002_flash_wait_ready(void);
static inline __attribute__((always_inline)) void wait_idle(void)
{
    while (REG(0xa2000028)&1u) {}
}
static inline __attribute__((always_inline)) void wait_tx_empty(void)
{
    while (REG(0xa2000020)) {}
    wait_idle();
}
static inline __attribute__((always_inline)) void wait_rx_empty(void)
{
    while (REG(0xa2000024)) {}
    wait_idle();
}
static inline __attribute__((always_inline)) void encode(unsigned width, unsigned address)
{
    /* CK804 masks register shift counts to six bits; 32..63 yield zero. */
    for (unsigned i=1; i<=4; ++i) {
        unsigned shift=((width-i)*8u)&63u;
        open_cfw_gx8002_flash_state.command[i]=shift<32u ? (uint8_t)(address>>shift) : 0;
    }
}
int open_cfw_gx8002_flash_otp_read(unsigned offset,uint8_t *buffer,unsigned length)
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
    open_cfw_gx8002_flash_state.command[0]=0x48;
    unsigned width=open_cfw_gx8002_flash_state.address_bytes;
    encode(width,address);
    unsigned result=0;
    uintptr_t destination=(uintptr_t)buffer;
    do {
        unsigned chunk=(int32_t)length<32 ? length : 32;
        if (chunk) {
            unsigned prefix=width+2;
            wait_idle();
            REG(0xa2000008)=0;REG(0xa0300090)=2;
            REG(0xa200004c)=0;REG(0xa2000010)=0;
            REG(0xa2000000)=0x407;REG(0xa2000004)=width+1;
            REG(0xa2000018)=0;REG(0xa20000f4)=0;REG(0xa2000008)=1;
            for (unsigned i=0;i<prefix;++i) {
                while (!(REG(0xa2000028)&2)) {}
                REG(0xa2000060)=*(volatile uint8_t *)((uintptr_t)open_cfw_gx8002_flash_state.command+i);
            }
            REG(0xa2000010)=1;
            wait_tx_empty();
            REG(0xa2000008)=0;REG(0xa2000010)=0;
            REG(0xa2000000)=0x807;REG(0xa2000004)=chunk-1;
            REG(0xa2000018)=0;REG(0xa2000054)=7;
            REG(0xa200004c)=1;REG(0xa2000008)=1;REG(0xa2000010)=1;
            REG(0xa2000060)=0;
            uintptr_t end=destination+chunk;
            for (uintptr_t cursor=destination;cursor!=end;++cursor) {
                while (!(REG(0xa2000028)&8)) {}
                *(uint8_t *)cursor=(uint8_t)REG(0xa2000060);
            }
            wait_rx_empty();
            REG(0xa2000008)=0;REG(0xa200004c)=0;
            REG(0xa0300090)=3;REG(0xa0300090)=1;REG(0xa2000008)=1;
            width=open_cfw_gx8002_flash_state.address_bytes;
        }
        address+=chunk;length-=chunk;destination+=chunk;result+=chunk;
        encode(width,address);
    } while (length);
    open_cfw_gx8002_flash_wait_ready();
    return (int)result;
}
