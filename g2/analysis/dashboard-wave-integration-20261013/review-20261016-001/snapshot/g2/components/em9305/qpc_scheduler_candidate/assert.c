/* Native returning assertion dispatcher 0x3117d8..0x3117e6.
 * The product callback slot is real SRAM state; no fault policy is invented.
 */
#include <stdint.h>
void opencfw_em9305_assert(uint32_t module, uint32_t line)
{
    const uintptr_t callback = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x80fe1c);
    if (callback != 0) {
        void (*const handler)(uint32_t,uint32_t) = (void (*)(uint32_t,uint32_t))callback;
        handler(module,line);
    }
}
