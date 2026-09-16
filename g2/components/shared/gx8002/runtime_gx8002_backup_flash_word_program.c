/* SPDX-License-Identifier: MIT */
/* Backup word programming: inline polling; partial words are ignored. */
#include <stdint.h>
#define REG(off) (*(volatile uint32_t *)(0xa2000000u+(off)))
extern int open_cfw_gx8002_flash_wait_ready(void);
int open_cfw_gx8002_flash_word_program(unsigned address, const uint32_t *buffer, unsigned length)
{
    while (REG(0x28)&1u) {}
    unsigned words=length>>2;
    REG(8)=0; REG(0x10)=0; REG(0x4c)=0; REG(0)=0x0080041f;
    REG(4)=words-1u; REG(0x10)=1; REG(0x18)=0x20000;
    REG(0xf4)=0x40000218; REG(0x50)=8; REG(0x4c)=2;
    REG(8)=1; REG(0x64)=0x32; REG(0x64)=address;
    for (unsigned i=0;i<words;++i) {
        while (!(REG(0x28)&2u)) {}
        REG(0x60)=buffer[i];
    }
    while (REG(0x20)) {}
    while (REG(0x28)&1u) {}
    open_cfw_gx8002_flash_wait_ready();
    REG(8)=0; REG(0x4c)=0; REG(8)=1;
    return 0;
}
