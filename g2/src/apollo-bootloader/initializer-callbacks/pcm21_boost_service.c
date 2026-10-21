/* Locked f89a4c46 PCM2.1 boost callback42ae9c..42aeec. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t opencfw_boot_control_critical_save(void);
extern void native_spot_trim_restore_42ae6c(void),native_spot_profile_trim_42ae24(uint8_t);
extern void opencfw_pcm22_spot_timer_stop(void);
uint32_t pcm21_boost_service(void){
 uint32_t mask=opencfw_boot_control_critical_save();native_spot_trim_restore_42ae6c();
 if(B(0x200271b2)){
  if(W(0x20000144)!=8 && W(0x20000144)!=12){W(0x4002037c)|=8;W(0x4002037c)|=64;}
  B(0x200271b2)=0;
 }
 /* Common timer-stop41ccd6 provider is shared with PCM2.2. */
 opencfw_pcm22_spot_timer_stop();native_spot_profile_trim_42ae24(1);
 __asm__ volatile("msr primask,%0"::"r"(mask):"memory");return mask;
}
