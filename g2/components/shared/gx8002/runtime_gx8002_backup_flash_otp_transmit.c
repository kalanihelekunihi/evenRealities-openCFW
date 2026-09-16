/* SPDX-License-Identifier: MIT */
/* Recovered backup package 0x400d0. Setup and cleanup execute even for zero lengths. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
#define REG(address) (*(volatile uint32_t *)(uintptr_t)(address))
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
static inline uint32_t load_byte(uintptr_t address)
{
    return *(volatile uint8_t *)address;
}
static inline uint32_t tx_ready(void)
{
    return REG(0xa2000028)&2u;
}
int open_cfw_gx8002_flash_otp_transmit(unsigned prefix_bytes,const uint8_t *buffer,unsigned length)
{
    wait_idle();
    REG(0xa2000008)=0;
    REG(0xa0300090)=2;
    REG(0xa200004c)=0;
    REG(0xa2000010)=0;
    REG(0xa2000000)=0x407;
    REG(0xa2000004)=length-1;
    REG(0xa2000018)=0;
    REG(0xa20000f4)=0;
    REG(0xa2000050)=8;
    REG(0xa2000008)=1;
    unsigned i=0;
    for (;i!=prefix_bytes;++i) {
        while (!(tx_ready())) {}
        REG(0xa2000060)=load_byte((uintptr_t)open_cfw_gx8002_flash_state.command+i);
    }
    REG(0xa2000010)=1;
    uintptr_t cursor=(uintptr_t)buffer;
    uintptr_t end=cursor+length;
    while (cursor!=end) {
        while (!(tx_ready())) {}
        REG(0xa2000060)=load_byte(cursor);
        ++cursor;
    }
    wait_tx_empty();
    REG(0xa2000008)=0;
    REG(0xa0300090)=3;
    REG(0xa0300090)=1;
    REG(0xa2000008)=1;
    open_cfw_gx8002_flash_wait_ready();
    return 0;
}
