/* SPDX-License-Identifier: MIT */
/* Recovered package0x15fb8. Preserve signed chunk selection and final encode. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
#define REG(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern int open_cfw_gx8002_flash_wait_ready(void);
extern void open_cfw_gx8002_spi_wait_idle(void);
extern void open_cfw_gx8002_spi_wait_tx_empty(void);
extern void open_cfw_gx8002_spi_wait_rx_empty(void);
extern void open_cfw_gx8002_flash_encode_address(const volatile uint32_t *,unsigned,uint8_t *);
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
    open_cfw_gx8002_flash_encode_address(&open_cfw_gx8002_flash_state.address_bytes,
        address,(uint8_t *)open_cfw_gx8002_flash_state.command);
    unsigned result=0;
    uintptr_t destination=(uintptr_t)buffer;
    do {
        unsigned chunk=(int32_t)length<32 ? length : 32;
        if (chunk) {
            unsigned width=open_cfw_gx8002_flash_state.address_bytes;
            unsigned prefix=width+2;
            open_cfw_gx8002_spi_wait_idle();
            REG(0xa2000008)=0;REG(0xa0300090)=2;
            REG(0xa200004c)=0;REG(0xa2000010)=0;
            REG(0xa2000000)=0x407;REG(0xa2000004)=width+1;
            REG(0xa2000018)=0;REG(0xa20000f4)=0;REG(0xa2000008)=1;
            for (unsigned i=0;i<prefix;++i) {
                while (!(REG(0xa2000028)&2)) {}
                REG(0xa2000060)=*(volatile uint8_t *)((uintptr_t)open_cfw_gx8002_flash_state.command+i);
            }
            REG(0xa2000010)=1;
            open_cfw_gx8002_spi_wait_tx_empty();
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
            open_cfw_gx8002_spi_wait_rx_empty();
            REG(0xa2000008)=0;REG(0xa200004c)=0;
            REG(0xa0300090)=3;REG(0xa0300090)=1;REG(0xa2000008)=1;
        }
        address+=chunk;length-=chunk;destination+=chunk;result+=chunk;
        open_cfw_gx8002_flash_encode_address(&open_cfw_gx8002_flash_state.address_bytes,
            address,(uint8_t *)open_cfw_gx8002_flash_state.command);
    } while (length);
    open_cfw_gx8002_flash_wait_ready();
    return (int)result;
}
