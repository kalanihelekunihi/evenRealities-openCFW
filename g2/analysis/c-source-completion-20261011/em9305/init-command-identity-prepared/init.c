#include <stdint.h>
extern void opencfw_em9305_callback_31c0e0(void);
extern void opencfw_em9305_callback_324628(void);
extern void opencfw_em9305_callback_326904(void);
extern void opencfw_em9305_callback_323620(void);
extern void opencfw_em9305_callback_324dd4(void);
extern void opencfw_em9305_callback_324e3c(void);
extern uint32_t opencfw_em9305_ll_command_pending_310634(void);
extern uint32_t opencfw_em9305_radio_identity_control_303c9c(uint32_t);
/* Full3080f8..308148; old state read before later callback stores. */
uint32_t opencfw_em9305_init_lower_3080f8(uint32_t incoming)
{
 (void)incoming;
 *(volatile uint32_t *)(uintptr_t)0x8056bcu=(uint32_t)(uintptr_t)opencfw_em9305_callback_31c0e0;
 *(volatile uint32_t *)(uintptr_t)0x803d48u=(uint32_t)(uintptr_t)opencfw_em9305_callback_31c0e0;
 uint32_t old=*(volatile uint32_t *)(uintptr_t)0x805b34u;
 *(volatile uint32_t *)(uintptr_t)0x805178u=(uint32_t)(uintptr_t)opencfw_em9305_callback_324628;
 *(volatile uint32_t *)(uintptr_t)0x8052c8u=(uint32_t)(uintptr_t)opencfw_em9305_callback_326904;
 *(volatile uint32_t *)(uintptr_t)0x805170u=(uint32_t)(uintptr_t)opencfw_em9305_callback_323620;
 *(volatile uint32_t *)(uintptr_t)0x805b34u=old|14u;
 return opencfw_em9305_ll_command_pending_310634();
}
/* Full30814c..308196; captured product before four ordered clears. */
uint32_t opencfw_em9305_init_lower_30814c(uint32_t incoming)
{
 (void)incoming;uintptr_t product=*(volatile uint32_t *)(uintptr_t)0x805cacu;
 *(volatile uint32_t *)(uintptr_t)0x8051f0u=0u;
 *(volatile uint32_t *)(uintptr_t)0x8051ecu=0u;
 *(volatile uint32_t *)(uintptr_t)0x8051e8u=0u;
 uint32_t version=*(volatile uint8_t *)(product+4u);
 *(volatile uint32_t *)(uintptr_t)0x802968u=(uint32_t)(uintptr_t)opencfw_em9305_callback_324dd4;
 *(volatile uint32_t *)(uintptr_t)0x8051e4u=0u;
 if(version>=8u){uint32_t old=*(volatile uint32_t *)(uintptr_t)0x805b30u;*(volatile uint32_t *)(uintptr_t)0x805b30u=old|64u;}
 (void)opencfw_em9305_radio_identity_control_303c9c((uint32_t)(uintptr_t)opencfw_em9305_callback_324e3c);
 *(volatile uint16_t *)(uintptr_t)0x8051eau=262u;
 return 262u;
}
