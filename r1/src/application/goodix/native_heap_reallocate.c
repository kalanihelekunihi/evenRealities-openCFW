#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
extern void *r1_goodix_native_heap_control(void);
static uint32_t read_word(uintptr_t address)
{ return *(const volatile uint32_t *)address; }
static void write_word(uintptr_t address,uint32_t value)
{ *(volatile uint32_t *)address=value; }
/* This is the native resize ABI, not a replacement for libc realloc. */
void *r1_goodix_native_reallocate(void *allocation,uint32_t size)
{
    if (!allocation) return goodix_mem_malloc((int32_t)size);
    uintptr_t pool=(uintptr_t)r1_goodix_native_heap_control();
    uintptr_t user=(uintptr_t)allocation;
    if (!pool || user<read_word(pool+32u) || user>=read_word(pool+36u)) return NULL;
    uintptr_t block=user-8u;
    uint32_t adjusted=((size+3u)&~3u)+8u;
    uint32_t flags=read_word(block+4u);
    if ((flags>>2)<adjusted) {
        void *replacement=goodix_mem_malloc((int32_t)size);
        if (replacement) {
            uint32_t bytes=(read_word(block+4u)>>2)-8u;
            for (uint32_t i=0;i<bytes;i++)
                ((volatile uint8_t *)replacement)[i]=((const volatile uint8_t *)allocation)[i];
            goodix_mem_free(allocation);
        }
        return replacement;
    }
    uint32_t remainder=(flags>>2)-adjusted;
    if (remainder>=16u) {
        uint32_t retained=(flags&3u)|(adjusted<<2);
        write_word(block+4u,retained);
        uintptr_t tail=block+(retained>>2);
        write_word(tail+4u,(remainder<<2)+3u);
        goodix_mem_free((void *)(tail+8u));
    }
    return allocation;
}
