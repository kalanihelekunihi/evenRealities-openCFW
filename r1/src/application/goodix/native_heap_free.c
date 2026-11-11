#include <stdint.h>
#include <stddef.h>
#include "goodix_mem.h"
extern uint8_t *volatile r1_goodix_native_heap_pool;
static uint32_t read_word(uintptr_t address)
{ return *(const volatile uint32_t *)address; }
static void write_word(uintptr_t address,uint32_t value)
{ *(volatile uint32_t *)address=value; }
void *r1_goodix_native_heap_control(void)
{ return r1_goodix_native_heap_pool; }
uint32_t r1_goodix_native_size_bin(uint32_t size)
{ return size-8u<=1024u ? 0u : 1u; }
void r1_goodix_native_bin_remove(void *control,void *node,uint32_t bin)
{
    uintptr_t pool=(uintptr_t)control,block=(uintptr_t)node;
    uint32_t previous=read_word(block+8),next=read_word(block+12);
    write_word(previous+12,next);
    previous=read_word(block+8);next=read_word(block+12);
    write_word(next+8,previous);
    if (read_word(read_word(block+8)+12)==previous)
        write_word(pool,read_word(pool)&~(UINT32_C(1)<<bin));
}
void r1_goodix_native_bin_insert(void *control,void *node,uint32_t bin)
{
    uintptr_t pool=(uintptr_t)control,block=(uintptr_t)node;
    uintptr_t anchor=pool+4u+bin*8u;
    uint32_t bit=UINT32_C(1)<<bin,bitmap=read_word(pool);
    if (!(bitmap&bit)) {
        write_word(pool,bitmap|bit);
        write_word(block+8,(uint32_t)anchor);
        write_word(block+12,read_word(anchor+12));
        write_word(read_word(anchor+12)+8,(uint32_t)block);
        write_word(anchor+12,(uint32_t)block);
        return;
    }
    uintptr_t current=read_word(anchor+12);
    uint32_t flags=read_word(block+4);
    while (current!=anchor && read_word(current+4)<flags)
        current=read_word(current+12);
    write_word(block+8,read_word(current+8));
    write_word(block+12,(uint32_t)current);
    write_word(read_word(current+8)+12,(uint32_t)block);
    write_word(current+8,(uint32_t)block);
}
void goodix_mem_free(void *allocation)
{
    uintptr_t pool=(uintptr_t)r1_goodix_native_heap_control();
    uintptr_t user=(uintptr_t)allocation;
    if (!pool || !user || user<read_word(pool+32) || user>=read_word(pool+36)) return;
    uintptr_t block=user-8u;
    uint32_t flags=read_word(block+4);
    if (!(flags&2u)) return;
    uintptr_t next=block+(flags>>2),top=read_word(pool+28);
    if (next==top) {
        flags+=read_word(top+4);
        write_word(block+4,flags);
        if (flags&1u) {
            write_word(block+4,flags&~3u);
            write_word(pool+28,(uint32_t)block);
            return;
        }
        uintptr_t previous=block-read_word(block);
        r1_goodix_native_bin_remove((void *)pool,(void *)previous,
            r1_goodix_native_size_bin(read_word(previous+4)>>2));
        write_word(previous+4,(read_word(previous+4)+read_word(block+4))&~3u);
        write_word(pool+28,(uint32_t)previous);
        return;
    }
    uint32_t current_flags=read_word(block+4),next_flags=read_word(next+4);
    if ((current_flags&1u) && (next_flags&2u)) {
        write_word(block+4,current_flags&~2u);
        r1_goodix_native_bin_insert((void *)pool,(void *)block,
            r1_goodix_native_size_bin(current_flags>>2));
        write_word(next,read_word(block+4)>>2);
        write_word(next+4,read_word(next+4)&~1u);
        return;
    }
    if (!(next_flags&2u)) {
        r1_goodix_native_bin_remove((void *)pool,(void *)next,
            r1_goodix_native_size_bin(next_flags>>2));
        write_word(block+4,read_word(block+4)+(read_word(next+4)&~3u));
    }
    if (!(*(const volatile uint8_t *)(block+4)&1u)) {
        uintptr_t previous=block-read_word(block);
        r1_goodix_native_bin_remove((void *)pool,(void *)previous,
            r1_goodix_native_size_bin(read_word(previous+4)>>2));
        write_word(previous+4,read_word(previous+4)+(read_word(block+4)&~3u));
        block=previous;
    }
    uint32_t combined=read_word(block+4);
    write_word(block+4,combined&~2u);
    r1_goodix_native_bin_insert((void *)pool,(void *)block,
        r1_goodix_native_size_bin(combined>>2));
    next=block+(read_word(block+4)>>2);
    write_word(next,read_word(block+4)>>2);
    write_word(next+4,read_word(next+4)&~1u);
}
uint32_t goodix_mem_get_free_size(void)
{
    uintptr_t pool=(uintptr_t)r1_goodix_native_heap_control();
    if (!pool) return 0;
    uint32_t used=(uint32_t)(read_word(pool+28)-pool+16u);
    uint32_t available=read_word(pool+40);
    return available>used ? available-used : 0;
}
