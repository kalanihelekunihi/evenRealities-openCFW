#include <stdint.h>
#include <stddef.h>
extern uint32_t r1_goodix_native_size_bin(uint32_t);
extern void r1_goodix_native_bin_remove(void *,void *,uint32_t);
extern void r1_goodix_native_bin_insert(void *,void *,uint32_t);
static uint32_t read_word(uintptr_t address)
{ return *(const volatile uint32_t *)address; }
static void write_word(uintptr_t address,uint32_t value)
{ *(volatile uint32_t *)address=value; }
/* Native bin-only allocation. The caller supplies an adjusted block size;
 * wilderness allocation, payload clearing and fatal policy belong to the
 * public wrapper and are deliberately not folded into this interface. */
void *r1_goodix_native_bin_allocate(void *control,uint32_t requested)
{
    uintptr_t pool=(uintptr_t)control;
    uint32_t bin=r1_goodix_native_size_bin(requested);
    uint32_t bitmap=read_word(pool),bit=UINT32_C(1)<<bin,selected=0;
    if ((bitmap&bit) &&
        requested<=(read_word(read_word(pool+12u+bin*8u)+4u)>>2)) {
        selected=bin;
    } else {
        uint32_t threshold=bit<<1;
        uint32_t higher=bitmap&~(threshold-1u);
        if (higher<threshold) return NULL;
        uint32_t low=bin+1u,high=1u;
        do {
            uint32_t middle=(high+low)>>1;
            uint32_t lower_bits=(UINT32_C(1)<<(middle+1u))-1u;
            if ((higher&lower_bits)>=threshold) high=middle;
            else low=middle;
        } while (high-low>1u);
        if (bitmap&(UINT32_C(1)<<low)) selected=low;
        else selected=high;
    }
    uint32_t encoded=requested<<2;
    uintptr_t block=read_word(pool+16u+selected*8u);
    while (read_word(block+4u)<encoded) block=read_word(block+12u);
    r1_goodix_native_bin_remove(control,(void *)block,selected);
    uint32_t flags=read_word(block+4u);
    uintptr_t following=block+(flags>>2);
    uint32_t remainder=(flags>>2)-requested;
    uintptr_t split=0;
    if (remainder<16u) {
        write_word(following+4u,read_word(following+4u)|1u);
    } else {
        split=block+(encoded>>2);
        write_word(block+4u,encoded);
        write_word(split+4u,(remainder<<2)|1u);
        write_word(following,remainder);
    }
    write_word(block+4u,read_word(block+4u)|3u);
    if (split)
        r1_goodix_native_bin_insert(control,(void *)split,
            r1_goodix_native_size_bin(read_word(split+4u)>>2));
    return (void *)(block+8u);
}
