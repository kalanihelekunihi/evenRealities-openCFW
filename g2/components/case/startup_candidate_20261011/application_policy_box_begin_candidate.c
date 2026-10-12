#include "../semantic_strings_candidate_20261011/case_semantic_strings.h"
/* SPDX-License-Identifier: MIT
 * Native CASE 0x38e0 option-bit update for box activation.
 * The option selector is read from the actual native stack slot at SP+4
 * after the exact four-register push and 32-byte local frame allocation.
 * This models the architectural ambient word without inventing a default.
 */
#include <stdint.h>
extern void case_boot_read_option_words(uint32_t *words); /* 0x4a00 */
extern uint32_t case_boot_option_write(const uint32_t *words); /* 0x4a6c */
extern void case_boot_option_prepare(void); /* 0x4bf4 */
extern void case_boot_option_unlock(void); /* 0x4b6c */
extern void case_boot_option_commit_a(void); /* 0x4b3c */
extern void case_boot_option_commit_b(void); /* 0x4b50 */
extern void case_boot_option_commit_c(void); /* 0x4b20 */
extern uint32_t case_legacy_logger(const char *format,...); /* 0x9170 */
extern void case_policy_sensor_delay(uint32_t ticks); /* 0xa7b0 */
__attribute__((noinline,used)) void case_policy_box_begin_with_native_words(uint32_t *words,uint32_t selector)
{
    words[1]=selector;
    case_boot_read_option_words(words);
    uint32_t status=words[6];
    uint8_t quiet=*(volatile uint8_t *)(uintptr_t)0x200000bfu;
    if((status&0x100000u)==0u){
        if(quiet==0u){(void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(08003964),status);(void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800398c));}
        status|=0x100000u;
    }else{
        if(quiet==0u){(void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(08003990),status);(void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800398c));}
        status&=~0x100000u;
    }
    words[6]=status;
    case_boot_option_prepare();case_boot_option_unlock();
    if(quiet==0u){(void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(080039b8),case_boot_option_write(words));(void)case_legacy_logger((const char *)(uintptr_t)CASE_STRING_ADDR(0800398c));}
    case_policy_sensor_delay(100u);
    case_boot_option_commit_a();case_boot_option_commit_b();case_boot_option_commit_c();
}

__attribute__((naked,noinline)) void case_policy_box_begin(void)
{
    __asm__ volatile(
        "push {r4, r5, r6, lr}\n"
        "sub sp, #32\n"
        "mov r0, sp\n"
        "ldr r1, [sp, #4]\n"
        "bl case_policy_box_begin_with_native_words\n"
        "add sp, #32\n"
        "pop {r4, r5, r6, pc}\n");
}
