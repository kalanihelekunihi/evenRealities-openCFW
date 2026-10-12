/* Native331ac0..331aea: argument ignored, 28-byte tail clear and ordered masks.
 * R0 at native return is the mask 0x1fff, retained for the caller ABI. */
uint32_t opencfw_em9305_ll_dispatch_initialize(uint32_t ignored)
{
 (void)ignored;
 (void)opencfw_em9305_memset((void *)(uintptr_t)0x805700u,0u,28u);
 *(volatile uint32_t *)(uintptr_t)0x8056f8u=31u;
 *(volatile uint32_t *)(uintptr_t)0x8056e8u=UINT32_MAX;
 *(volatile uint32_t *)(uintptr_t)0x8056fcu=0u;
 *(volatile uint32_t *)(uintptr_t)0x8056f4u=0u;
 *(volatile uint32_t *)(uintptr_t)0x8056f0u=0u;
 *(volatile uint32_t *)(uintptr_t)0x8056ecu=0x1fffu;
 return 0x1fffu;
}
