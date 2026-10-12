#include <stdint.h>
extern void opencfw_em9305_init_callback_30e840(void);
extern void opencfw_em9305_init_callback_32b61c(void);
extern void opencfw_em9305_init_callback_32beb0(void);
extern void opencfw_em9305_init_callback_32bfc4(void);
extern void opencfw_em9305_init_callback_31ae84(void);
extern void opencfw_em9305_init_callback_304430(void);
extern void opencfw_em9305_init_callback_3044e8(void);
extern void opencfw_em9305_init_callback_3043ac(void);
extern void opencfw_em9305_init_callback_304468(void);
extern void opencfw_em9305_init_callback_3183ec(void);
extern void opencfw_em9305_init_callback_31836c(void);
extern void opencfw_em9305_init_callback_3245ec(void);
extern void opencfw_em9305_init_callback_32468c(void);
extern void opencfw_em9305_init_callback_324698(void);
extern void opencfw_em9305_init_callback_31810c(void);
extern void opencfw_em9305_init_callback_31807c(void);
extern void opencfw_em9305_init_callback_318168(void);
uint32_t opencfw_em9305_init_child_304324(void)
{
 *(volatile uint32_t *)(uintptr_t)0x805c20u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_304430;
 *(volatile uint32_t *)(uintptr_t)0x805c28u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3044e8;
 *(volatile uint32_t *)(uintptr_t)0x805c1cu=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3043ac;
 *(volatile uint32_t *)(uintptr_t)0x805c24u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_304468;
 return 0x805c24u;
}
uint32_t opencfw_em9305_init_lower_307ec8(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x805cdcu=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_30e840;
 *(volatile uint32_t *)(uintptr_t)0x805cc4u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32b61c;
 *(volatile uint32_t *)(uintptr_t)0x805cc8u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32beb0;
 *(volatile uint32_t *)(uintptr_t)0x805cccu=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32bfc4;
 *(volatile uint32_t *)(uintptr_t)0x805c74u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31ae84;
 (void)opencfw_em9305_init_child_304324();
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(product+4u);
 *(volatile uint32_t *)(uintptr_t)0x805c60u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3183ec;
 *(volatile uint32_t *)(uintptr_t)0x805c5cu=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31836c;
 *(volatile uint32_t *)(uintptr_t)0x805c9cu=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_3245ec;
 *(volatile uint32_t *)(uintptr_t)0x805ca0u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_32468c;
 *(volatile uint32_t *)(uintptr_t)0x805ca4u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_324698;
 *(volatile uint32_t *)(uintptr_t)0x805248u=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31810c;
 *(volatile uint32_t *)(uintptr_t)0x80299cu=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_31807c;
 if(version>=13u){
  uint32_t state=*(volatile uint32_t *)(uintptr_t)0x805b34u;
 *(volatile uint32_t *)(uintptr_t)0x8028acu=(uint32_t)(uintptr_t)opencfw_em9305_init_callback_318168;
  state|=2048u;
  *(volatile uint32_t *)(uintptr_t)0x805b34u=state;
  return state;
 }
 return version;
}
