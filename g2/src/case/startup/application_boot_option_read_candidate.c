/* SPDX-License-Identifier: MIT
 * Native CASE 0x4a00 option-word reader. The caller supplies selector words[1].
 */
#include <stdint.h>
/* Stock 0x08003EA8 (case_flash_status_classify) */
uint32_t case_boot_option_status_a(void) /* 0x3ea8 */
{
    uint32_t status=*(volatile uint32_t *)(uintptr_t)0x40022020u&0xffu;
    return status==0xaau || status==0xccu?status:0xbbu;
}
/* Stock 0x08003EC0 (case_flash_status_masked) */
uint32_t case_boot_option_status_b(void) /* 0x3ec0 */
{return *(volatile uint32_t *)(uintptr_t)0x40022020u&0x077f6000u;}
void case_boot_read_option_words(uint32_t *words)
{
    words[0]=7u;
    const uint32_t selector=words[1];
    uint32_t register_word;
    if(selector==1u)register_word=*(volatile uint32_t *)(uintptr_t)0x4002202cu;
    else if(selector==4u)register_word=*(volatile uint32_t *)(uintptr_t)0x4002204cu;
    else if(selector==8u)register_word=*(volatile uint32_t *)(uintptr_t)0x40022050u;
    else register_word=*(volatile uint32_t *)(uintptr_t)0x40022030u;
    words[2]=register_word&0x7fu;
    words[3]=(register_word>>16)&0x7fu;
    words[4]=case_boot_option_status_a();
    words[6]=case_boot_option_status_b();
    words[5]=0x077f6000u;
}
