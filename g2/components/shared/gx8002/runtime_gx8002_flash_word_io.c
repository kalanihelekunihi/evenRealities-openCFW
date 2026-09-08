/* SPDX-License-Identifier: MIT */
/* Recovered image-A word-oriented SPI callbacks. Transfer count is floor
 * (length/4); callers must provide appropriately aligned word buffers. */
#include <stdint.h>
#define REG(off) (*(volatile uint32_t *)(0xa2000000u+(off)))
extern int open_cfw_gx8002_spi_wait_idle(void);
extern int open_cfw_gx8002_spi_wait_rx_empty(void);
extern int open_cfw_gx8002_spi_wait_tx_empty(void);
extern int open_cfw_gx8002_flash_wait_ready(void);
#include "runtime_gx8002_flash_state.h"

int open_cfw_gx8002_flash_word_read(unsigned address, uint32_t *buffer, unsigned length)
{
    if (!length) return 0;
    open_cfw_gx8002_spi_wait_idle();
    unsigned words=length>>2;
    REG(8)=0; REG(0x4c)=0; REG(0x10)=0; REG(0)=0x0080081f;
    REG(4)=words-1u; REG(0x18)=0; REG(0x54)=7;
    uintptr_t device=open_cfw_gx8002_flash_state.selected_device;
    REG(0x4c)=1;
    unsigned id=*(volatile uint32_t *)(device+4);
    if (id-0x1c3812u<2u) {
        REG(0xf4)=0x40003219; REG(8)=1; REG(0x64)=0xeb;
    } else {
        REG(0xf4)=0x40004218; REG(8)=1; REG(0x64)=0x6b;
    }
    REG(0x64)=address; REG(0x10)=1;
    for (unsigned i=0;i<words;++i) {
        while (!(REG(0x28)&8u)) {}
        buffer[i]=REG(0x60);
    }
    open_cfw_gx8002_spi_wait_rx_empty();
    REG(8)=0; REG(0x4c)=0; REG(8)=1;
    return 0;
}

int open_cfw_gx8002_flash_word_program(unsigned address, const uint32_t *buffer, unsigned length)
{
    open_cfw_gx8002_spi_wait_idle();
    unsigned words=length>>2;
    REG(8)=0; REG(0x10)=0; REG(0x4c)=0; REG(0)=0x0080041f;
    REG(4)=words-1u; REG(0x10)=1; REG(0x18)=0x20000;
    REG(0xf4)=0x40000218; REG(0x50)=8; REG(0x4c)=2;
    REG(8)=1; REG(0x64)=0x32; REG(0x64)=address;
    for (unsigned i=0;i<words;++i) {
        while (!(REG(0x28)&2u)) {}
        REG(0x60)=buffer[i];
    }
    open_cfw_gx8002_spi_wait_tx_empty();
    open_cfw_gx8002_flash_wait_ready();
    REG(8)=0; REG(0x4c)=0; REG(8)=1;
    return 0;
}
