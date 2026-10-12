#include "startup_ton_hooks.h"
#include "startup_spot_events.h"
extern int spotmgr_init_42abbc_native(void);
extern int hw_state_compose_42bdf0_native(void);
extern int bl_bl009_dispatch_native(void);
extern int startup_noop_42f670_native(void);
extern uint32_t opencfw_pcm22_profile_apply(void);
extern uint32_t opencfw_pcm22_post_lptohp(void);
extern uint32_t opencfw_pcm22_timer_service(void);
extern uint32_t pcm21_boost_service(void);
extern uint32_t opencfw_pcm22_temperature_init(void);
extern uint32_t opencfw_boot_hardware_readiness_gate(void);
extern uint32_t opencfw_boot_spotmgr_power_state_update_a(uint32_t,uint32_t,void *);
extern uint32_t opencfw_boot_spot_state_power_event(uint8_t,uint8_t,uint32_t *);
/* SPDX-License-Identifier: MIT. Locked-f89a4c46 reconstruction.
 * INFO/cache control matches public Apollo510 HAL5.1 pwrctrl family.
 * SPOT callback pointers bind to selected source providers. Root startup and
 * initialized product-state contracts remain separate. */
#include "startup_runtime.h"
#include "../application_storage/device_mode_wait.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
NI uint32_t opencfw_boot_startup_trim_version(uint32_t *output){
 if(W(0x20000098)==0xffffffffu){uint32_t s=opencfw_boot_device_mode_wait(1,0x244,1,(volatile uint32_t *)(uintptr_t)0x20000098u);if(W(0x20000098)==0||s)W(0x20000098)=0;}
 if(output){*output=W(0x20000098);return 0;}return 6;
}
NI uint32_t opencfw_boot_startup_info_cache(void){
 if(!(W(0x400201bc)&8u)||!(W(0x40021008)&0x08000000u))return 7;
 uint32_t values[12],status;
 #define READ(space,offset,count,dest) do{status=opencfw_boot_device_mode_wait(space,offset,count,values);if(status)return status;for(uint32_t i=0;i<count;i++)W(0x200267f8u+dest+4*i)=values[i];}while(0)
 READ(5,0x480,2,4);READ(1,0x204,1,12);READ(1,0x206,1,16);READ(3,0x208,8,20);
 READ(1,0x210,1,52);READ(1,0x240,3,56);READ(1,0x24a,2,72);READ(1,0x250,12,80);READ(1,0x245,1,68);
 W(0x200267f8)=0x1f01600d;return 0;
 #undef READ
}
static void slot(uint32_t offset,uint32_t address){W(0x20026e38u+offset)=address;}
/* Stock BL009 slot 8 target 0x42d848 is a two-instruction zero return. */
__attribute__((noinline,used)) static uint32_t bl009_slot8_noop(void){return 0;}
/* Stock BL009 slot 0x34 enables both autoswitch control bits and marks ready. */
__attribute__((noinline,used)) static uint32_t bl009_slot34_enable(void){
 W(0x400211a0u)|=3u;B(0x200271b8u)=1u;return 0u;
}
/* Stock BL009 slot 0x38 conditionally clears the paired control and ready bits. */
__attribute__((noinline,used)) static uint32_t bl009_slot38_disable(void){
 if(B(0x200271b8u)){W(0x400211a0u)&=~3u;B(0x200271b8u)=0u;}
 return 0u;
}
/* Stock BL009 non-special slot 0x1c writes two documented bit fields. */
__attribute__((noinline,used)) static uint32_t bl009_slot1c_config(void){
 W(0x40020088u)=(W(0x40020088u)&~0x3fu)|1u;
 W(0x400201b0u)=(W(0x400201b0u)&~(3u<<15))|(2u<<15);
 return 0u;
}
/* Stock BL009 non-special slot 0x18 conditionally sets a ten-bit timing field. */
__attribute__((noinline,used)) static uint32_t bl009_slot18_timing(void){
 if(B(0x200271a8u)){
  uint32_t count=W(0x2002705cu);
  uint32_t field=count>=8u?count-7u:0u;
  W(0x40020080u)=(W(0x40020080u)&~0x3ffu)|(field&0x3ffu);
 }
 return 0u;
}
/* Revision 33 / variant 2 uses a one-count-earlier timing threshold. */
__attribute__((noinline,used)) static uint32_t bl009_special_slot18_timing(void){
 if(B(0x200271a8u)){
  uint32_t count=W(0x2002705cu);
  uint32_t field=count>=7u?count-6u:0u;
  W(0x40020080u)=(W(0x40020080u)&~0x3ffu)|(field&0x3ffu);
 }
 return 0u;
}
__attribute__((noinline,used)) static uint32_t bl009_special_slot1c_config(void){
 W(0x40020088u)&=~0x3fu;
 W(0x400201b0u)=(W(0x400201b0u)&~(3u<<15))|(1u<<15);
 return 0u;
}
/* PCM2.1 slot 0x14 selects the six-step control setting. */
__attribute__((noinline,used)) static uint32_t pcm21_slot14_config(void){
 W(0x4002034cu)=(W(0x4002034cu)&~(31u<<25))|(6u<<25);
 return 0u;
}
/* PCM2.1 timing slots act only after the INFO cache magic is installed. */
__attribute__((noinline,used)) static uint32_t pcm21_slot18_timing(void){
 if(W(0x20026ba0u)==0x1f01600du){
  uint32_t field=W(0x20026bc0u)>>7;
  W(0x40020080u)=(W(0x40020080u)&~0x3ffu)|(field&0x3ffu);
 }
 return 0u;
}
__attribute__((noinline,used)) static uint32_t pcm21_slot1c_timing(void){
 if(W(0x20026ba0u)==0x1f01600du){
  uint32_t value=W(0x20026c08u);
  W(0x40020088u)=(W(0x40020088u)&~0x3fu)|((value>>2)&0x3fu);
  W(0x400201b0u)=(W(0x400201b0u)&~(3u<<15))|((value&3u)<<15);
 }
 return 0u;
}
NI uint32_t opencfw_boot_startup_spot_dispatch(void){
 /* Native byte loop replaces IAR memset without any stock executable fallback. */
 for(uint32_t i=0;i<60;i++)B(0x20026e38u+i)=0;
 #define REV (W(0x4002000c)&255u)
 #define VAR W(0x20000098u)
 B(0x200271ad)=((REV==35&&VAR>=2)||REV>=36)?1:0;
 B(0x200271a9)=((REV==34&&VAR==2)||(REV==35&&VAR==1))?1:0;
 B(0x200271aa)=((REV==33&&VAR==2)||(REV==33&&VAR==3)||(REV==34&&VAR==0))?1:0;
 B(0x200271ab)=(REV==33&&VAR>=3)?1:0;
 B(0x200271ac)=((REV==34&&VAR==1)||(REV==35&&VAR==0))?1:0;
 B(0x200271ae)=((REV==34&&VAR==2)||(REV==35&&VAR==1))?((B(0x2002682c)&1)^1):0;
 if(B(0x200271aa)|B(0x200271ac)|B(0x200271ae)){
  W(0x40020028)&=~2u;W(0x40020028)|=1;W(0x40020060)|=0x8000;W(0x40020060)|=0x4000;W(0x40020060)|=0x2000;
 }
 if(B(0x200271ad)){
  slot(0,(uint32_t)(uintptr_t)&spotmgr_init_42abbc_native);slot(4,(uint32_t)(uintptr_t)&opencfw_boot_spotmgr_power_state_update_a);slot(8,(uint32_t)(uintptr_t)&opencfw_pcm22_temperature_init);slot(0x1c,(uint32_t)(uintptr_t)&opencfw_pcm22_profile_apply);slot(0x28,(uint32_t)(uintptr_t)&opencfw_pcm22_post_lptohp);slot(0x2c,(uint32_t)(uintptr_t)&opencfw_pcm22_timer_service);
 }else if(B(0x200271a9)){
  slot(0,(uint32_t)(uintptr_t)&hw_state_compose_42bdf0_native);slot(4,(uint32_t)(uintptr_t)&opencfw_boot_spot_state_power_event);slot(8,(uint32_t)(uintptr_t)&opencfw_boot_hardware_readiness_gate);slot(0x14,(uint32_t)(uintptr_t)&pcm21_slot14_config);slot(0x18,(uint32_t)(uintptr_t)&pcm21_slot18_timing);slot(0x1c,(uint32_t)(uintptr_t)&pcm21_slot1c_timing);slot(0x2c,(uint32_t)(uintptr_t)&pcm21_boost_service);
 }else if((REV==33&&VAR>=2)||(REV==34&&VAR<2)||(REV==35&&VAR==0)){
  slot(0,(uint32_t)(uintptr_t)&bl_bl009_dispatch_native);slot(4,(uint32_t)(uintptr_t)&state_event_dispatch_42d562_native);slot(8,(uint32_t)(uintptr_t)&bl009_slot8_noop);slot(0xc,(uint32_t)(uintptr_t)&state_event_flag_set_42d5c2_native);slot(0x10,(uint32_t)(uintptr_t)&state_event_finalize_42d5cc_native);slot(0x30,(uint32_t)(uintptr_t)&autosw_initialize_42d63a_native);slot(0x34,(uint32_t)(uintptr_t)&bl009_slot34_enable);slot(0x38,(uint32_t)(uintptr_t)&bl009_slot38_disable);
  if(REV==33&&VAR==2){slot(0x18,(uint32_t)(uintptr_t)&bl009_special_slot18_timing);slot(0x1c,(uint32_t)(uintptr_t)&bl009_special_slot1c_config);}else{slot(0x18,(uint32_t)(uintptr_t)&bl009_slot18_timing);slot(0x1c,(uint32_t)(uintptr_t)&bl009_slot1c_config);}
 }else if(REV==33&&VAR==1){slot(0,(uint32_t)(uintptr_t)&startup_noop_42f670_native);slot(4,(uint32_t)(uintptr_t)&opencfw_boot_ton_state_event);slot(0x18,(uint32_t)(uintptr_t)&bl009_special_slot18_timing);slot(0x1c,(uint32_t)(uintptr_t)&bl009_special_slot1c_config);}
 if(REV==33&&VAR<2){slot(0x20,(uint32_t)(uintptr_t)&opencfw_boot_ton_trim_cache);slot(0x24,(uint32_t)(uintptr_t)&opencfw_boot_ton_trim_apply);}
 uint32_t callback=W(0x20026e38);return callback?((uint32_t(*)(void))(uintptr_t)W(0x20026e38))():0;
 #undef REV
 #undef VAR
}
