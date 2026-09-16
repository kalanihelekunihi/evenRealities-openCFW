/* SPDX-License-Identifier: MIT */
/* Backup command transport at package 0x3f570/0x3f5f0; polling is inline.
 * Recovered polling SPI transport. Infinite readiness waits are observed
 * behavior, not placeholders. Buffers/counts require valid caller storage. */
#include <stdint.h>
#define REG(off) (*(volatile uint32_t *)(0xa2000000u + (off)))
static inline __attribute__((always_inline)) int open_cfw_gx8002_spi_wait_idle(void)
{
    while (REG(0x28) & 1u) {}
    return 0;
}
static inline __attribute__((always_inline)) int open_cfw_gx8002_spi_wait_rx_empty(void)
{
    while (REG(0x24) != 0) {}
    open_cfw_gx8002_spi_wait_idle();
    return 0;
}
static inline __attribute__((always_inline)) int open_cfw_gx8002_spi_wait_tx_empty(void)
{
    while (REG(0x20) != 0) {}
    open_cfw_gx8002_spi_wait_idle();
    return 0;
}
int open_cfw_gx8002_flash_command_read(unsigned int command, uint8_t *buffer,
                                      unsigned int count)
{
    open_cfw_gx8002_spi_wait_idle();
    REG(8)=0; REG(0x4c)=0; REG(0)=0xc07; REG(4)=count-1u;
    REG(0x10)=1; REG(0x18)=0; REG(0xf4)=0; REG(8)=1; REG(0x60)=command;
    for (unsigned int i=0; i<count; ++i) {
        while (!(REG(0x28)&8u)) {}
        buffer[i]=(uint8_t)REG(0x60);
    }
    open_cfw_gx8002_spi_wait_rx_empty();
    return 0;
}
int open_cfw_gx8002_flash_command_write(unsigned int command, const uint8_t *buffer,
                                       unsigned int count)
{
    open_cfw_gx8002_spi_wait_idle();
    REG(8)=0; REG(0x10)=0; REG(0x4c)=0; REG(0)=0x407; REG(4)=count;
    REG(0x10)=1; REG(0x18)=count<<16; REG(0xf4)=0; REG(8)=1; REG(0x60)=command;
    for (unsigned int i=0; i<count; ++i) {
        while (!(REG(0x28)&2u)) {}
        REG(0x60)=buffer[i];
    }
    open_cfw_gx8002_spi_wait_tx_empty();
    return 0;
}
