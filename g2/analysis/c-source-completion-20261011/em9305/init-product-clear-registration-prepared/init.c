#include <stdint.h>
extern void opencfw_em9305_callback_32aa48(void);
extern void opencfw_em9305_callback_327a54(void);
extern void opencfw_em9305_callback_32bb40(void);
extern void opencfw_em9305_callback_32ae3c(void);
extern void opencfw_em9305_callback_32c148(void);
extern void opencfw_em9305_callback_306cbc(void);
extern uint32_t opencfw_em9305_init_child_3251dc(uint32_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
/* Full30a27c..30a29a; native MPYUW low halves, count is a byte. */
uint32_t opencfw_em9305_init_child_30a27c(void)
{
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uintptr_t output=*(volatile uint32_t *)(uintptr_t)0x805c38u;
 uint32_t count=*(volatile uint8_t *)(product+12u);
 return (uint32_t)(uintptr_t)opencfw_em9305_memset((void *)output,0u,count*2824u);
}
/* Full30a29c..30a324; version captured before flag stores/clear child. */
uint32_t opencfw_em9305_init_lower_30a29c(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x802970u=(uint32_t)(uintptr_t)opencfw_em9305_callback_32aa48;
 *(volatile uint32_t *)(uintptr_t)0x802988u=(uint32_t)(uintptr_t)opencfw_em9305_callback_327a54;
 *(volatile uint32_t *)(uintptr_t)0x80521cu=(uint32_t)(uintptr_t)opencfw_em9305_callback_32ae3c;
 *(volatile uint32_t *)(uintptr_t)0x8028a0u=(uint32_t)(uintptr_t)opencfw_em9305_callback_32c148;
 (void)opencfw_em9305_init_child_3251dc((uint32_t)(uintptr_t)opencfw_em9305_callback_32bb40);
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(product+4u);
 *(volatile uint32_t *)(uintptr_t)0x801300u=(uint32_t)(uintptr_t)opencfw_em9305_callback_306cbc;
 if(version>=9u){
  uint32_t first=*(volatile uint32_t *)(uintptr_t)0x805b30u|4096u;
  *(volatile uint32_t *)(uintptr_t)0x805b30u=first;
  if(version>=13u){
   uint32_t second=*(volatile uint32_t *)(uintptr_t)0x805b34u;
   *(volatile uint32_t *)(uintptr_t)0x805b30u=first;
   *(volatile uint32_t *)(uintptr_t)0x805b34u=second|256u;
   if(version!=13u){*(volatile uint32_t *)(uintptr_t)0x805b30u=first;*(volatile uint32_t *)(uintptr_t)0x805b34u=second|1280u;}
  }
 }
 return opencfw_em9305_init_child_30a27c();
}
