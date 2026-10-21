/* Independent f89a4c46 reconstruction:41bae8..41bbd0 and41cde0..41cdfa.
 * Reuses native query/critical/delay; optional callback stays a genuine API. */
#include "power_special_mode.h"
#include "runtime_query.h"
#include <stddef.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t opencfw_boot_control_critical_save(void);
extern void opencfw_boot_control_delay_us(uint32_t);
uint32_t opencfw_boot_power_special_hook(uint32_t operation,uint32_t mode){
 uint32_t callback=W(0x20026e5c);
 return callback?((uint32_t(*)(uint32_t,uint32_t))(uintptr_t)callback)((uint8_t)operation,(uint8_t)mode):0;
}
uint32_t opencfw_boot_power_special_mode(uint32_t mode){
 uint8_t selected=(uint8_t)mode,result;
 if(selected!=0&&selected!=3)return 6;
 if(selected==3&&((W(0x40021108)>>4)&3)!=3)return 7;
 if(opencfw_boot_control_query(20,&result))return 1;
 if(result)return 3;
 if(selected==B(0x200271a5)){
  if(B(0x200271a6)!=B(0x200271a5))B(0x200271a6)=selected;
  return 0;
 }
 uint32_t irq=opencfw_boot_control_critical_save();
 if(selected==3)(void)opencfw_boot_power_special_hook(1,selected);
 if(selected==3)W(0x40021090)|=1;
 else W(0x40021090)&=~1u;
 opencfw_boot_control_delay_us(1);
 W(0x4002108c)=(W(0x4002108c)&~3u)|(selected&3u);
 B(0x200271a5)=selected;B(0x200271a6)=selected;
 opencfw_boot_control_delay_us(6);
 if(selected==0)(void)opencfw_boot_power_special_hook(1,selected);
 __asm__ volatile("msr primask,%0"::"r"(irq):"memory");
 return 0;
}
