#include <stdint.h>

struct native_product_317ebc {uint32_t low,high;};
static struct native_product_317ebc native_mpydu_317ebc(uint32_t a,uint32_t b)
{
    uint64_t product=(uint64_t)a*b;
    return (struct native_product_317ebc){(uint32_t)product,(uint32_t)(product>>32u)};
}

static uint32_t native_mpywhl_317ebc(uint32_t high)
{
    return (uint32_t)high*4295u;
}

/* Full native 0x317ebc..0x317efa. The status byte at 0x805a8b gates the
 * multiply path. MPYDU writes the R2/R3 pair; ADD.F followed by ADC.F adds
 * the low-word carry to the high-word result. */
uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t first,uint32_t second)
{
    uint32_t status=*(volatile uint8_t *)(uintptr_t)0x805a8bu;
    if((status&8u)==0u) return 0u;
    struct native_product_317ebc first_product=native_mpydu_317ebc(first,second);
    uint32_t correction=native_mpywhl_317ebc(first_product.high);
    struct native_product_317ebc second_product=native_mpydu_317ebc(
        first_product.low,0x10c7u);
    uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    uint32_t result=second_product.high+correction;
    uint32_t carry=second_product.low>UINT32_MAX-0x6ef9u;
    uint32_t byte=*(volatile uint8_t *)(config+41u);
    result+=carry+1u;
    return byte+result+16u;
}
