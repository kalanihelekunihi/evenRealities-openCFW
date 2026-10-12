#include <stdint.h>
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern void opencfw_em9305_callback_3228a8(void);
extern void opencfw_em9305_callback_3228f0(void);
extern void opencfw_em9305_callback_3227e0(void);
extern void opencfw_em9305_callback_3227a4(void);
/* Full307d74..307dd4; R0 preserves low-version byte or high-version
 * state address. Product/config read follows clear child. */
uint32_t opencfw_em9305_init_lower_307d74(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x802958u=(uint32_t)(uintptr_t)opencfw_em9305_callback_3228a8;
 *(volatile uint32_t *)(uintptr_t)0x805204u=(uint32_t)(uintptr_t)opencfw_em9305_callback_3228f0;
 *(volatile uint32_t *)(uintptr_t)0x80289cu=(uint32_t)(uintptr_t)opencfw_em9305_callback_3227e0;
 *(volatile uint32_t *)(uintptr_t)0x802898u=(uint32_t)(uintptr_t)opencfw_em9305_callback_3227a4;
 (void)opencfw_em9305_memset((void *)0x804fd8u,0u,404u);
 uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 uint32_t version=*(volatile uint8_t *)(product+4u);
 if(version<8u)return version;
 uint32_t old=*(volatile uint32_t *)(uintptr_t)0x805b30u;
 *(volatile uint32_t *)(uintptr_t)0x805b30u=old|128u;
 return 0x805b30u;
}
