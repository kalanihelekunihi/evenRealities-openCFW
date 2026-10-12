/* Native30e564..30e57c: VREP2HL16 = two16-bit lanes, value00100010. */
uint32_t opencfw_em9305_init_lower_30e564(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x805b00u=0u;
 *(volatile uint32_t *)(uintptr_t)0x805afcu=0u;
 *(volatile uint32_t *)(uintptr_t)0x805af8u=0x00100010u;
 *(volatile uint32_t *)(uintptr_t)0x805b08u=0u;
 *(volatile uint32_t *)(uintptr_t)0x805b04u=0u;
 *(volatile uint8_t *)(uintptr_t)0x805b00u=7u;
 return 0x805af8u;
}
uint32_t opencfw_em9305_init_lower_30e580(uint32_t incoming)
{(void)incoming;*(volatile uint8_t *)(uintptr_t)0x805b5cu=0u;*(volatile uint32_t *)(uintptr_t)0x805b58u=900u;return 0x805b58u;}
uint32_t opencfw_em9305_init_lower_30e594(uint32_t incoming)
{(void)incoming;*(volatile uint8_t *)(uintptr_t)0x805b82u=0u;*(volatile uint16_t *)(uintptr_t)0x805b80u=0u;return 0x805b80u;}
/* Native30e538..30e560: live config reload occurs after the clear. */
uint32_t opencfw_em9305_init_lower_30e538(uint32_t incoming)
{
 (void)incoming;(void)opencfw_em9305_memset((void *)(uintptr_t)0x805adcu,0u,28u);
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint8_t *)(uintptr_t)0x805af0u=3u;
 uint32_t value=*(volatile uint16_t *)(config+42u);
 *(volatile uint16_t *)(uintptr_t)0x805af4u=8096u;
 *(volatile uint16_t *)(uintptr_t)0x805adcu=(uint16_t)value;
 return value;
}
/* Native30e42c..30e47a: preserve the second clear and its delay-slot
 * halfword27 write; final native R0 is VREP2HL1 =00010001. */
uint32_t opencfw_em9305_init_lower_30e42c(uint32_t incoming)
{
 (void)incoming;(void)opencfw_em9305_memset((void *)(uintptr_t)0x805ab4u,0u,40u);
 uintptr_t config=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint16_t *)(uintptr_t)0x805ab8u=328u;
 uint32_t first=*(volatile uint8_t *)(config+35u),second=*(volatile uint8_t *)(config+36u);
 *(volatile uint8_t *)(uintptr_t)0x805ac8u=3u;
 *(volatile uint8_t *)(uintptr_t)0x805ab4u=(uint8_t)first;
 *(volatile uint8_t *)(uintptr_t)0x805ab5u=(uint8_t)second;
 *(volatile uint16_t *)(uintptr_t)0x805ab6u=27u;
 (void)opencfw_em9305_memset((void *)(uintptr_t)0x805ac9u,0u,5u);
 *(volatile uint16_t *)(uintptr_t)0x805aceu=10u;
 *(volatile uint16_t *)(uintptr_t)0x805ad8u=3200u;
 *(volatile uint32_t *)(uintptr_t)0x805ad0u=0x00010001u;
 return 0x00010001u;
}
