#include <stdint.h>
extern void opencfw_em9305_callback_32233c(void);
extern void opencfw_em9305_callback_322184(void);
extern void opencfw_em9305_callback_322178(void);
extern void opencfw_em9305_callback_322580(void);
extern void opencfw_em9305_callback_3225b0(void);
extern void opencfw_em9305_callback_3246f8(void);
extern void opencfw_em9305_callback_3042b4(void);
extern void opencfw_em9305_callback_30425c(void);
extern void opencfw_em9305_callback_3041e0(void);
extern void opencfw_em9305_callback_304214(void);
/* Full3042e8..304320: callback registration, nativeR0 slot address. */
uint32_t opencfw_em9305_init_child_3042e8(void)
{
 *(volatile uint32_t *)(uintptr_t)0x805c14u=(uint32_t)(uintptr_t)opencfw_em9305_callback_3042b4;
 *(volatile uint32_t *)(uintptr_t)0x805c10u=(uint32_t)(uintptr_t)opencfw_em9305_callback_30425c;
 *(volatile uint32_t *)(uintptr_t)0x805c08u=(uint32_t)(uintptr_t)opencfw_em9305_callback_3041e0;
 *(volatile uint32_t *)(uintptr_t)0x805c0cu=(uint32_t)(uintptr_t)opencfw_em9305_callback_304214;
 return 0x805c0cu;
}
/* Full307e30..307ec4; loop post-stores six584-byte buffer identities. */
uint32_t opencfw_em9305_init_lower_307e30(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x805c8cu=(uint32_t)(uintptr_t)opencfw_em9305_callback_32233c;
 *(volatile uint32_t *)(uintptr_t)0x805c88u=(uint32_t)(uintptr_t)opencfw_em9305_callback_322184;
 *(volatile uint32_t *)(uintptr_t)0x805c84u=(uint32_t)(uintptr_t)opencfw_em9305_callback_322178;
 *(volatile uint32_t *)(uintptr_t)0x805c90u=(uint32_t)(uintptr_t)opencfw_em9305_callback_322580;
 *(volatile uint32_t *)(uintptr_t)0x805c94u=(uint32_t)(uintptr_t)opencfw_em9305_callback_3225b0;
 (void)opencfw_em9305_init_child_3042e8();
 *(volatile uint32_t *)(uintptr_t)0x805ca8u=(uint32_t)(uintptr_t)opencfw_em9305_callback_3246f8;
 for(uint32_t i=0u;i<6u;i++)*(volatile uint32_t *)(uintptr_t)(0x805c44u+4u*i)=0x801a1cu+584u*i;
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(product+4u);
 if(version<13u)return version;
 uint32_t old=*(volatile uint32_t *)(uintptr_t)0x805b34u;
 *(volatile uint32_t *)(uintptr_t)0x805b34u=old|4096u;
 return 0x805b34u;
}
