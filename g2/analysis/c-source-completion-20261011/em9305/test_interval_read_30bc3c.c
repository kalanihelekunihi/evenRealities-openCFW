/* Native30bc3c tail branch to Native306ed4..306ee6: ordered byte copies. */
uint32_t opencfw_em9305_ll_test_30bc3c(uintptr_t output)
{
 uint32_t low=*(volatile uint8_t *)(uintptr_t)0x805af4u;
 *(volatile uint8_t *)output=(uint8_t)low;
 uint32_t high=*(volatile uint8_t *)(uintptr_t)0x805af5u;
 *(volatile uint8_t *)(output+1u)=(uint8_t)high;
 return 2u;
}
