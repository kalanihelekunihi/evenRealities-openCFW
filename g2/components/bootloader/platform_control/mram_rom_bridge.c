/* SPDX-License-Identifier: MIT
 * Source reconstruction of42e8a4..42e8c2, whose immutable API table433120
 * slot1 is Thumb0x0200ff21. The external ROM implementation is not supplied.
 */
#include <stdint.h>
extern uint32_t opencfw_boot_rom_mram_program(uint32_t,uint32_t,const void *,uint32_t,uint32_t);
uint32_t opencfw_boot_control_mram(uint32_t key,uint32_t operation,const void *source,uint32_t word_offset,uint32_t words) {
    uint32_t result=opencfw_boot_rom_mram_program(key,operation,source,word_offset,words);
    *(volatile uint32_t *)(uintptr_t)0x40014008u=0xc3u;
    *(volatile uint32_t *)(uintptr_t)0x40014024u=0;
    *(volatile uint32_t *)(uintptr_t)0x40014008u=0;
    return result;
}
