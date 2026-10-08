/* SPDX-License-Identifier: MIT. Independent locked-f89a4c46 reconstruction.
 * Numeric operations/registers preserve stock; no physical power guarantee. */
#include "startup_power_config.h"
#include "../platform_control/runtime_query.h"
#include "../platform_control/power_domains.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
extern uint32_t opencfw_boot_control_delay_status_change(uint32_t,volatile uint32_t *,uint32_t,uint32_t);
extern uint32_t opencfw_hal_status_poll(uint32_t,uintptr_t,uint32_t,uint32_t,uint32_t);
NI void opencfw_boot_startup_external_mode(uint32_t callback){W(0x200270ccu)=callback;}
NI uint32_t opencfw_boot_startup_hook_before(void){
 uintptr_t callback=W(0x20026e4cu);return callback?((uint32_t(*)(void))callback)():0;
}
NI uint32_t opencfw_boot_startup_hook_middle(void){
 uintptr_t callback=W(0x20026e50u);return callback?((uint32_t(*)(void))callback)():0;
}
NI uint32_t opencfw_boot_startup_hook_after(void){
 uintptr_t callback=W(0x20026e54u);return callback?((uint32_t(*)(void))callback)():0;
}
NI void opencfw_boot_startup_register_setup(void){
 W(0x40020060u)|=0x20000u;W(0x40020060u)|=0x40000u;
 W(0x40020060u)|=0x80000u;W(0x40020060u)|=0x10000u;
 W(0x40020060u)&=~16u;W(0x40020060u)|=14u;
 W(0x40020060u)|=1u;W(0x40020060u)&=~0x200u;
 W(0x40020060u)|=0x1c0u;W(0x40020060u)|=0x20u;
}
NI uint32_t opencfw_boot_startup_resource_ready(void){
 uint32_t status=opencfw_boot_control_delay_status_change(100,(volatile uint32_t *)(uintptr_t)0x40020180u,0x100,0x100);
 if(status==0)return 0;
 status=opencfw_boot_control_delay_status_change(100,(volatile uint32_t *)(uintptr_t)0x400c0a7cu,1,1);
 if(status!=0)return status;
 W(0x400c0a80u)|=1u;
 return opencfw_boot_control_delay_status_change(100,(volatile uint32_t *)(uintptr_t)0x40020180u,0x100,0x100);
}
NI uint32_t opencfw_boot_startup_power_configure(uint32_t operation,uint32_t unused){
 (void)unused;
 switch((uint8_t)operation){
 case 0:
  if(((W(0x40021108u)>>4)&3u)==3u)return 0;
  (void)opencfw_boot_startup_hook_before();opencfw_boot_startup_register_setup();
  W(0x40020378u)|=0x80000000u;W(0x4002033cu)|=15u;
  (void)opencfw_boot_startup_hook_middle();W(0x40021100u)|=1u;
  (void)opencfw_boot_startup_hook_after();return 0;
 case 1:{
  uint8_t active=0;(void)opencfw_boot_control_query(23,&active);
  if(active){uint32_t status=opencfw_boot_startup_resource_ready();if(status)return status;
   status=opencfw_bl_mspi_mode_leave(23);if(status)return status;}
  return 0;
 }
 case 2:
  W(0x40020124u)=(W(0x40020124u)&~0xfcu)|0x80u;W(0x40020120u)=1u;return 0;
 case 3:{
  W(0xe000edfcu)&=~0x1000000u;W(0x40020250u)&=~1u;W(0x40020250u)&=~14u;
  W(0x40021004u)=0;W(0x4002100cu)=0;
  uint32_t status=opencfw_hal_status_poll(5,0x40021004u,0x3fffffffu,0,1);if(status)return status;
  uint32_t value=0;(void)opencfw_boot_power_callback(3,0,&value);
  status=opencfw_hal_status_poll(5,0x4002100cu,0x4c4u,0,1);if(status)return status;
  value=0;(void)opencfw_boot_power_callback(4,0,&value);return 0;
 }
 default:return 6;
 }
}
/* The original float-in-S0 ABI pushes incoming R1/R2 as response words.
 * Those words survive absent/partial callbacks. Explicit assembly retains
 * that concrete register behavior without uninitialized C object reads. */
__attribute__((naked,noinline,pcs("aapcs-vfp")))
uint32_t opencfw_boot_startup_temperature(float *output __attribute__((unused)),float input __attribute__((unused))){
 __asm__ volatile(
  "push {r0-r4,lr}\nmovs r4,r0\nvstr s0,[sp]\nmov r2,sp\nmovs r1,#0\nmovs r0,#2\n"
  "bl opencfw_boot_power_callback\ncmp r0,#0\nbne 1f\n"
  "ldr r0,[sp,#4]\nstr r0,[r4]\nldr r0,[sp,#8]\nstr r0,[r4,#4]\nmovs r0,#0\nb 2f\n"
  "1: movs r0,#0\nstr r0,[r4]\nstr r0,[r4,#4]\nmovs r0,#1\n"
  "2: add sp,#16\npop {r4,pc}\n");
}
