#include <stdint.h>
extern void opencfw_em9305_callback_32bb9c(void);
extern void opencfw_em9305_callback_32a218(void);
extern void opencfw_em9305_callback_329844(void);
extern void opencfw_em9305_callback_318f2c(void);
extern void opencfw_em9305_callback_318c1c(void);
extern void opencfw_em9305_callback_31bd78(void);
extern void opencfw_em9305_callback_32ae70(void);
extern void opencfw_em9305_callback_32bc6c(void);
extern void opencfw_em9305_callback_325984(void);
extern void opencfw_em9305_callback_3189f4(void);
extern void opencfw_em9305_callback_319890(void);
extern void opencfw_em9305_callback_32a628(void);
extern void opencfw_em9305_callback_32a5ac(void);
extern uint32_t opencfw_em9305_callback_30fc20(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_callback_30fc24(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_child_3251dc(uint32_t);
extern uint32_t opencfw_em9305_init_child_318ab8(uint32_t);
/* Full30a1a0..30a278; authentic callback identities, no table aliases. */
uint32_t opencfw_em9305_init_lower_30a1a0(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x802950u=(uint32_t)(uintptr_t)opencfw_em9305_callback_32bb9c;
 uint32_t prior=*(volatile uint32_t *)(uintptr_t)0x802954u;
 *(volatile uint32_t *)(uintptr_t)0x805200u=(uint32_t)(uintptr_t)opencfw_em9305_callback_32a218;
 if(prior==0u)*(volatile uint32_t *)(uintptr_t)0x802954u=(uint32_t)(uintptr_t)opencfw_em9305_callback_329844;
 prior=*(volatile uint32_t *)(uintptr_t)0x80280cu;
 *(volatile uint32_t *)(uintptr_t)0x802878u=(uint32_t)(uintptr_t)opencfw_em9305_callback_318f2c;
 *(volatile uint32_t *)(uintptr_t)0x80287cu=(uint32_t)(uintptr_t)opencfw_em9305_callback_318c1c;
 *(volatile uint32_t *)(uintptr_t)0x8056c8u=(uint32_t)(uintptr_t)opencfw_em9305_callback_31bd78;
 *(volatile uint32_t *)(uintptr_t)0x8056a8u=(uint32_t)(uintptr_t)opencfw_em9305_callback_32ae70;
 if(prior==0u)*(volatile uint32_t *)(uintptr_t)0x80280cu=(uint32_t)(uintptr_t)opencfw_em9305_callback_32bc6c;
 *(volatile uint32_t *)(uintptr_t)0x8027e0u=(uint32_t)(uintptr_t)opencfw_em9305_callback_325984;
 uint32_t value=opencfw_em9305_init_child_3251dc((uint32_t)(uintptr_t)opencfw_em9305_callback_3189f4);
 (void)opencfw_em9305_init_child_318ab8(value);
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(product+4u);
 if(version<7u)return (uint32_t)product;
 uint32_t old=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 value=old|14u;*(volatile uint32_t *)(uintptr_t)0x805b30u=value;
 if(version==7u)return value;
 uint32_t second=*(volatile uint32_t *)(uintptr_t)0x805b34u;
 value=old|46u;*(volatile uint32_t *)(uintptr_t)0x805b30u=value;
 if(version<9u)return value;
 value=old|0x1002eu;*(volatile uint32_t *)(uintptr_t)0x805b34u=second;*(volatile uint32_t *)(uintptr_t)0x805b30u=value;
 if(version==9u)return value;
 value=old|0x501002eu;*(volatile uint32_t *)(uintptr_t)0x805b34u=second;*(volatile uint32_t *)(uintptr_t)0x805b30u=value;
 if(version<12u)return value;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=value;*(volatile uint32_t *)(uintptr_t)0x805b34u=second|128u;
 return value;
}
/* Full30a134..30a19a, then authentic fallthrough into30a1a0. */
uint32_t opencfw_em9305_init_lower_30a134(uint32_t incoming)
{
 (void)incoming;uint32_t prior=*(volatile uint32_t *)(uintptr_t)0x80280cu;
 *(volatile uint32_t *)(uintptr_t)0x8056a0u=(uint32_t)(uintptr_t)opencfw_em9305_callback_319890;
 *(volatile uint32_t *)(uintptr_t)0x80569cu=(uint32_t)(uintptr_t)opencfw_em9305_callback_32a628;
 if(prior==0u)*(volatile uint32_t *)(uintptr_t)0x80280cu=(uint32_t)(uintptr_t)opencfw_em9305_callback_32a5ac;
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t old=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 uint32_t version=*(volatile uint8_t *)(product+4u);
 *(volatile uint32_t *)(uintptr_t)0x8052ccu=(uint32_t)(uintptr_t)opencfw_em9305_callback_30fc20;
 *(volatile uint32_t *)(uintptr_t)0x8052d0u=(uint32_t)(uintptr_t)opencfw_em9305_callback_30fc24;
 uint32_t value=old|1u;*(volatile uint32_t *)(uintptr_t)0x805b30u=value;
 if(version>=7u){value=old|17u;*(volatile uint32_t *)(uintptr_t)0x805b30u=value;}
 return opencfw_em9305_init_lower_30a1a0(value);
}
