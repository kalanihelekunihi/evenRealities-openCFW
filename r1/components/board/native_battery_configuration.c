#include <stdint.h>
#include "native_kv_class.h"
extern void *volatile r1_batcfg_record_kv_handle;
/* These native getters save incoming r3 as the read word, ignore the read
 * status, then restore the complete possibly modified word to r3. No default
 * record is invented when the cached class rejects the requested size. */
#define READ_WORD() \
    uint32_t incoming; \
    __asm__ volatile("mov %0, r3" : "=r"(incoming)); \
    volatile uint32_t word=incoming; \
    (void)r1_kv_class_read(r1_batcfg_record_kv_handle,(void *)&word,4)
#define RESTORE_WORD() \
    uint32_t restored=word; \
    __asm__ volatile("mov r3, %0" : : "r"(restored) : "r3")
__attribute__((noinline)) uint32_t r1_batcfg_byte0_get(void)
{
    READ_WORD();
    uint32_t result=(uint8_t)word;
    RESTORE_WORD();
    return result;
}
__attribute__((noinline)) uint32_t r1_batcfg_flag1_get(void)
{
    READ_WORD();
    uint32_t result=(uint16_t)(word>>16)!=0;
    RESTORE_WORD();
    return result;
}
__attribute__((noinline)) uint32_t r1_batcfg_word1_signed_get(void)
{
    READ_WORD();
    uint32_t result=(uint32_t)(int32_t)(int16_t)(word>>16);
    RESTORE_WORD();
    return result;
}
