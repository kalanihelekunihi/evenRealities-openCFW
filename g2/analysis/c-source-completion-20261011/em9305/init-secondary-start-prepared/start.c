#include <stdint.h>
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_callback_321648(uintptr_t);
extern uint32_t opencfw_em9305_callback_321c30(uintptr_t);
extern uint32_t opencfw_em9305_callback_321958(uintptr_t);
/* Native3213ec..3213f6: preserve original R0, mark referenced record. */
uint32_t opencfw_em9305_callback_3213ec(uintptr_t object)
{
 uintptr_t record=*(volatile uint32_t *)(object+36u);
 *(volatile uint8_t *)(record+8u)=1u;
 return opencfw_em9305_callback_321648(object);
}
/* Native3213f8..32144c; callback pointers are genuine linker identities. */
uint32_t opencfw_em9305_init_secondary_start_3213f8(uintptr_t record)
{
 (void)opencfw_em9305_memset((void *)(record+48u),0u,148u);
 *(volatile uint8_t *)(record+74u)=1u;
 *(volatile uint8_t *)(record+72u)=1u;
 *(volatile uint8_t *)(record+96u)=9u;
 *(volatile uint32_t *)(record+80u)=(uint32_t)(uintptr_t)opencfw_em9305_callback_3213ec;
 *(volatile uint32_t *)(record+76u)=(uint32_t)(uintptr_t)opencfw_em9305_callback_321648;
 *(volatile uint32_t *)(record+200u)=(uint32_t)(uintptr_t)opencfw_em9305_callback_321c30;
 *(volatile uint32_t *)(record+196u)=(uint32_t)(uintptr_t)opencfw_em9305_callback_321958;
 *(volatile uint32_t *)(record+84u)=(uint32_t)record;
 *(volatile uint32_t *)(record+92u)=(uint32_t)(record+96u);
 *(volatile uint8_t *)(record+2u)=0u;
 *(volatile uint8_t *)(record+603u)=0u;
 *(volatile uint32_t *)(record+212u)=0u;
 return 0u;
}
