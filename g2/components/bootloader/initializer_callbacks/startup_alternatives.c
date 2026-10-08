/* Reconstructed locked f89a4c46 startup orchestration. HAL children remain
 * explicit dependencies; their status/spin order is preserved. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
extern uint32_t opencfw_boot_startup_shutdown_first(void);
extern uint32_t opencfw_boot_startup_shutdown_second(void);
extern void opencfw_boot_startup_external_mode(uint32_t);
extern void opencfw_boot_power_register_update(uint32_t,uint32_t);
extern void opencfw_boot_startup_power_initialize(void);
extern void opencfw_boot_startup_power_configure(uint32_t,uint32_t);
extern void __attribute__((pcs("aapcs-vfp"))) opencfw_boot_startup_temperature(float *,float);
extern void opencfw_boot_startup_clock_descriptor(const uint32_t *);
extern uint32_t opencfw_boot_startup_clock_select(uint32_t,uint32_t,uint32_t);
NI void opencfw_boot_startup_conditional(void){
 if(B(0x20027198)!=1)return;
 if(opencfw_boot_startup_shutdown_first())for(;;)__asm__ volatile("nop");
 if(opencfw_boot_startup_shutdown_second())for(;;)__asm__ volatile("nop");
 opencfw_boot_startup_external_mode(0);
 opencfw_boot_power_register_update(0x1c,W(0x434154));
 B(0x20027198)=0;
}
NI void opencfw_provider_41fa50(void){
 float scratch[2];const uint32_t descriptor[5]={0,0,0,0x8000,0xb71b00};
 opencfw_boot_startup_conditional();opencfw_boot_startup_power_initialize();
 opencfw_boot_startup_power_configure(0,0);
 opencfw_boot_startup_temperature(scratch,25.0f);
 opencfw_boot_startup_clock_descriptor(descriptor);
 (void)opencfw_boot_startup_clock_select(4,0,0);
 (void)opencfw_boot_startup_clock_select(5,0,0);
}
