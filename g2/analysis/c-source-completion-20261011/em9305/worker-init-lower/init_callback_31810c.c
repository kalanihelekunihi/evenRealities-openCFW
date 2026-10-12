#include <stdint.h>

/* Complete native 0x31810c..0x318166. Two DBNZ iterations preserve
 * base/slot rereads. Native 0x33301c fills with R1=0. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
uint32_t opencfw_em9305_init_callback_31810c(uint32_t incoming)
{
    (void)incoming;
    uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c38u;
    for (uint32_t index=0;index<2u;++index) {
        if (base==0u) continue;
        uintptr_t slot=base+index*0xb08u+0xafcu;
        uintptr_t object=*(volatile uint32_t *)slot;
        if (object==0u) continue;
        *(volatile uint16_t *)(object+96u)=0u;
        *(volatile uint16_t *)(object+94u)=0u;
        *(volatile uint8_t *)(object+80u)=0u;
        *(volatile uint16_t *)(object+76u)=0u;
        (void)opencfw_em9305_memset((void *)(object+100u),0u,44u);
        object=*(volatile uint32_t *)slot;
        (void)opencfw_em9305_memset((void *)(object+82u),0u,12u);
    }
    return 1u;
}
