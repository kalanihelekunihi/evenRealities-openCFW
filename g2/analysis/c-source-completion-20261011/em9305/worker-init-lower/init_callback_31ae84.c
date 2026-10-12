#include <stdint.h>

/* Native 0x31ae84..0x31aeb2. LP_COUNT is loaded from the product
 * configuration byte at root+13; ARC LP executes exactly that many
 * records when nonzero. Input byte+1 is read only for active records. */
uint32_t opencfw_em9305_init_callback_31ae84(uintptr_t incoming)
{
    uintptr_t root=*(volatile uint32_t *)(uintptr_t)0x805cacu;
    uint32_t count=*(volatile uint8_t *)(root+13u);
    if (count==0u) return (uint32_t)incoming;
    uintptr_t record=0x805184u;
    for (uint32_t n=0;n<count;++n) {
        uint8_t active=*(volatile uint8_t *)record;
        if (active!=0u) {
            uint8_t key=*(volatile uint8_t *)(incoming+1u);
            uint8_t matched=*(volatile uint8_t *)(record+1u);
            if (matched==key)
                *(volatile uint16_t *)record=0u;
        }
        record+=12u;
    }
    return (uint32_t)incoming;
}
