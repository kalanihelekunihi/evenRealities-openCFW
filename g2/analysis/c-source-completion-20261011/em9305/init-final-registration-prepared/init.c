#include <stdint.h>
extern void *opencfw_em9305_memset(void *,int,unsigned long);

/* Native308630..308662: callback registration and ordered state publication. */
extern void opencfw_em9305_init_callback_325450(void);
extern void opencfw_em9305_init_callback_325474(void);
uint32_t opencfw_em9305_init_registration_31408c(uint32_t callback)
{
 uint32_t count=*(volatile uint8_t *)(uintptr_t)0x80606cu;
 if(count<=2u){
  *(volatile uint8_t *)(uintptr_t)0x80606cu=(uint8_t)(count+1u);
  *(volatile uint32_t *)(uintptr_t)(0x806060u+count*4u)=callback;
 }
 return callback;
}
uint32_t opencfw_em9305_init_lower_308630(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x8028a8u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_325450;
 (void)opencfw_em9305_init_registration_31408c((uint32_t)(uintptr_t)opencfw_em9305_init_callback_325474);
 uint32_t state=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 *(volatile uint8_t *)(uintptr_t)0x805b83u=0u;
 state|=UINT32_C(1)<<27u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=state;
 return state;
}
/* Native309cb8..309cf6: four callback identities and tail buffer clear. */
extern void opencfw_em9305_init_callback_327de0(void);
extern void opencfw_em9305_init_callback_3280c8(void);
extern void opencfw_em9305_init_callback_327dc8(void);
extern void opencfw_em9305_init_callback_32c254(void);
uint32_t opencfw_em9305_init_lower_309cb8(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x802960u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_327de0;
 *(volatile uint32_t *)(uintptr_t)0x80520cu=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3280c8;
 *(volatile uint32_t *)(uintptr_t)0x8028b0u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_327dc8;
 *(volatile uint32_t *)(uintptr_t)0x8028a0u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32c254;
 return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)(uintptr_t)0x8052d4u,0u,304u);
}
