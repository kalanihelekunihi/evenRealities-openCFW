#include <stdint.h>
extern void opencfw_em9305_callback_31bbb0(void);
extern void opencfw_em9305_callback_328d78(void);
extern void opencfw_em9305_callback_32922c(void);
extern void opencfw_em9305_callback_31ce10(void);
extern uint32_t opencfw_em9305_init_child_3251dc(uint32_t);
extern uint32_t opencfw_em9305_init_child_317498(void);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
/* Full31b7d4..31b7e0, incoming R0 overwritten. */
uint32_t opencfw_em9305_init_child_31b7d4(uint32_t incoming)
{(void)incoming;return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)0x8028d0u,0u,128u);}
/* Full30a0a4..30a0fe, children ordered before fresh product read. */
uint32_t opencfw_em9305_init_lower_30a0a4(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x802894u=(uint32_t)(uintptr_t)opencfw_em9305_callback_31bbb0;
 *(volatile uint32_t *)(uintptr_t)0x802990u=(uint32_t)(uintptr_t)opencfw_em9305_callback_328d78;
 *(volatile uint32_t *)(uintptr_t)0x80523cu=(uint32_t)(uintptr_t)opencfw_em9305_callback_32922c;
 (void)opencfw_em9305_init_child_3251dc((uint32_t)(uintptr_t)opencfw_em9305_callback_31ce10);
 uint32_t result=opencfw_em9305_init_child_317498();
 (void)opencfw_em9305_init_child_31b7d4(result);
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(product+4u);
 if(version<11u)return version;
 uint32_t old=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=old|0x40000000u;
 return 0x805b30u;
}
