/* Authenticated native3344c8..3344df: exact six word default record;
 * native30e9e0 reader copies24bytes, next distinct table starts3344e0. */
static const uint32_t opencfw_em9305_init_defaults_3344c8[6]={0x00138800u,0x00138800u,0u,0u,0u,7u};
/* Native30e9e0..30ea06: clear full112byte state, signed sentinel127,
 * then24byte typed record; native R0 is destination+4. */
uint32_t opencfw_em9305_init_lower_30e9e0(uint32_t incoming)
{
 (void)incoming;(void)opencfw_em9305_memset((void *)(uintptr_t)0x805b84u,0u,112u);
 *(volatile uint8_t *)(uintptr_t)0x805bf0u=127u;
 return (uint32_t)(uintptr_t)opencfw_em9305_memcpy((void *)(uintptr_t)0x805b88u,opencfw_em9305_init_defaults_3344c8,24u);
}
