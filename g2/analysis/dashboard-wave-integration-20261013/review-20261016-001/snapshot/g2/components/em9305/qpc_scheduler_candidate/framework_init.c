/* Native QF_init0x311014..0x31105e and QF_bzero0x310fac..0x310fb8.
 * Fixed SRAM locations are decoded product identities; final initialization
 * and source-owned linker placement remain unresolved.
 */
#include <stdint.h>
extern void *opencfw_em9305_memset(void *destination,uint32_t value,uint32_t bytes); /* 0x33301c */
void opencfw_em9305_bzero(void *destination,uint32_t bytes)
{
    if (bytes != 0) (void)opencfw_em9305_memset(destination,0,bytes);
}
void opencfw_em9305_framework_init(void)
{
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x801390) = 0;
    *(volatile uint8_t *)(uintptr_t)UINT32_C(0x801360) = 0;
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x801364) = 0;
    opencfw_em9305_bzero((void *)(uintptr_t)UINT32_C(0x801394),0);
    opencfw_em9305_bzero((void *)(uintptr_t)UINT32_C(0x80131c),68);
    opencfw_em9305_bzero((void *)(uintptr_t)UINT32_C(0x801394),8);
    *(volatile uint8_t *)(uintptr_t)UINT32_C(0x801394) = 0;
    *(volatile uint8_t *)(uintptr_t)UINT32_C(0x801396) = 16;
}
