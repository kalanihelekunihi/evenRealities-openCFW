/* SPDX-License-Identifier: MIT */
/* Recovered package0x15e28. Setup and cleanup execute even for zero lengths. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
#define REG(address) (*(volatile uint32_t *)(uintptr_t)(address))
extern void open_cfw_gx8002_spi_wait_idle(void);
extern void open_cfw_gx8002_spi_wait_tx_empty(void);
extern int open_cfw_gx8002_flash_wait_ready(void);
/* LD.B already zero-extends on CK804. Express that result width directly
 * to avoid the compiler's redundant narrow-value extension. */
static inline uint32_t load_byte(uintptr_t address)
{
    uint32_t value;
    __asm__ volatile ("ld.b %0, (%1, 0)" : "=r"(value) : "r"(address) : "memory");
    return value;
}
/* Keep the status value and its mask in one temporary register. */
static inline uint32_t tx_ready(void)
{
    uint32_t value;
    __asm__ volatile ("ld.w %0, (%1, 40)\n\tandi %0, %0, 2"
                      : "=r"(value) : "r"((uintptr_t)0xa2000000) : "memory");
    return value;
}
int open_cfw_gx8002_flash_otp_transmit(unsigned prefix_bytes,const uint8_t *buffer,unsigned length)
{
    open_cfw_gx8002_spi_wait_idle();
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
    register unsigned i __asm__("r0")=0;
    for (;i!=prefix_bytes;++i) {
        __asm__ volatile ("" : "+r"(i));
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
    open_cfw_gx8002_spi_wait_tx_empty();
    REG(0xa2000008)=0;
    REG(0xa0300090)=3;
    REG(0xa0300090)=1;
    REG(0xa2000008)=1;
    open_cfw_gx8002_flash_wait_ready();
    return 0;
}
