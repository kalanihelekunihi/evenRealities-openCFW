/* Locked f89a4c46: profile apply42ab7c..42abb2; temperature init42ac54..42aca4. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
extern uint32_t opencfw_bl_mspi_mode_enter(uint32_t);
extern uint32_t __attribute__((pcs("aapcs-vfp"))) opencfw_boot_startup_temperature(float *,float);
extern uint32_t opencfw_boot_control_delay_status_change(uint32_t,volatile uint32_t *,uint32_t,uint32_t);
uint32_t opencfw_pcm22_profile_apply(void){
 if(W(0x20026ba0)==0x1f01600d){
  W(0x40020080)=(W(0x40020080)&~1023u)|((W(0x20026bc0)>>7)&1023u);
  W(0x40020088)=(W(0x40020088)&~63u)|((W(0x20026c08)>>2)&63u);
  W(0x400201b0)=(W(0x400201b0)&~0x18000u)|((W(0x20026c08)&3)<<15);
 }return 0;
}
uint32_t opencfw_pcm22_temperature_init(void){
 if(W(0x40021008)||W(0x40021010))return 1;
 if(opencfw_bl_mspi_mode_enter(29))return 1;
 float result[2];
 if(opencfw_boot_startup_temperature(result,-40.0f))return 1;
 return opencfw_boot_control_delay_status_change(2500,(volatile uint32_t *)0x400083e0,1,0)?4:0;
}
