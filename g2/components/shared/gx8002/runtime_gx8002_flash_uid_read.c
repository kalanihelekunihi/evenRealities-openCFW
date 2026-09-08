/* SPDX-License-Identifier: MIT */
/* Recovered package0x16118. Manufacturer is a byte; count uses signed MIN. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern void open_cfw_gx8002_spi_wait_idle(void);
extern void open_cfw_gx8002_spi_wait_rx_empty(void);
int open_cfw_gx8002_flash_uid_read(uint8_t *buffer,int requested,volatile int *actual)
{
    uintptr_t device=open_cfw_gx8002_flash_state.selected_device;
    unsigned manufacturer=*(volatile uint8_t *)(device+6);
    if (manufacturer!=0x85 && manufacturer!=0x5e) {
        *actual=0;
        return -1;
    }
    unsigned count=requested<16 ? (unsigned)requested : 16;
    *actual=(int)count;
    open_cfw_gx8002_spi_wait_idle();
    REG(0xa2000008)=0;REG(0xa200004c)=0;
    REG(0xa2000000)=0xc07;REG(0xa2000004)=count-1;
    REG(0xa2000010)=1;REG(0xa2000018)=0x40000;
    REG(0xa20000f4)=0;REG(0xa2000008)=1;
    REG(0xa2000060)=0x4b;
    REG(0xa2000060)=0;REG(0xa2000060)=0;
    REG(0xa2000060)=0;REG(0xa2000060)=0;
    uintptr_t cursor=(uintptr_t)buffer,end=cursor+count;
    while (cursor!=end) {
        while (!(REG(0xa2000028)&8)) {}
        *(uint8_t *)cursor=(uint8_t)REG(0xa2000060);
        ++cursor;
    }
    open_cfw_gx8002_spi_wait_rx_empty();
    return 0;
}
