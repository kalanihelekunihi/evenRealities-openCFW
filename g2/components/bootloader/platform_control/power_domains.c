/* SPDX-License-Identifier: MIT. Locked41bf84/41c17a and dependency dispatch.
 * Power acknowledgement timing is outside these source semantics. */
#include "power_domains.h"
#include "runtime_query.h"
#include "../clock_manager/clock_manager.h"
extern uint32_t opencfw_boot_control_critical_save(void);
extern uint32_t opencfw_hal_status_poll(uint32_t,uintptr_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_boot_control_delay_status_change(uint32_t,volatile uint32_t *,uint32_t,uint32_t);
extern void opencfw_hal_delay_us(uint32_t);
extern uint32_t opencfw_boot_power_special_mode(uint32_t); /* 41bae8 */
extern uint32_t opencfw_bl_clock_release_all(uint32_t);
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
uint32_t opencfw_boot_power_callback(uint32_t id,uint32_t enabled,void *value) {
 uintptr_t callback=U32(0x20026e3cu);
 return callback?((uint32_t (*)(uint32_t,uint32_t,void *))callback)((uint8_t)id,(uint8_t)enabled,value):0u;
}
static uint32_t hook(uintptr_t slot) {
 uintptr_t callback=U32(slot);return callback?((uint32_t (*)(void))callback)():0u;
}
uint32_t opencfw_boot_power_hook_begin(void) {return hook(0x20026e44u);}
uint32_t opencfw_boot_power_hook_end(void) {return hook(0x20026e48u);}
uint32_t opencfw_boot_power_release_needed(uint32_t selector) {
 uint32_t d[4];if(opencfw_boot_control_query_descriptor_copy(d,(uint8_t)selector)!=0u)return 1u;
 uint32_t group=d[3];if(group!=0x1eu && group!=0xc0u && group!=0x1e0u && group!=0x1e00u && group!=0x30000001u)return 1u;
 if((U32(d[0])&group)!=0u && (U32(d[0])&d[1])==0u)return 0u;
 return 1u;
}
uint32_t opencfw_bl_mspi_mode_enter(uint32_t selector) {
 uint8_t id=(uint8_t)selector;uint32_t d[4],value=0;uint32_t status=opencfw_boot_control_query_descriptor_copy(d,id);
 if(status!=0u)return status;
 if((U32(d[0])&d[1])!=0u)return 0u;
 if(id==23u && (U32(0x40021008u)&(1u<<27))==0u)return 1u;
 (void)opencfw_boot_power_hook_begin();
 if(id==20u) {
  if(U8(0x200271a6u)==3u)(void)opencfw_boot_power_special_mode(3u);
  (void)clock_request(4u,20u);
  if(U8(0x200271a5u)==3u)(void)clock_request(5u,20u);
  value=U8(0x200271a5u)==0u?1u:2u;(void)opencfw_boot_power_callback(1u,1u,&value);
 } else {
  if((d[1]<<2)!=0u && id<30u)(void)opencfw_boot_power_callback(3u,1u,&d[3]);
  if((d[1]&0x4c4u)!=0u && id>=30u)(void)opencfw_boot_power_callback(4u,1u,&d[3]);
 }
 uint32_t saved=opencfw_boot_control_critical_save();U32(d[0])|=d[1];__asm__ volatile("msr primask,%0"::"r"(saved):"memory");
 (void)opencfw_boot_power_hook_end();status=opencfw_hal_status_poll(5u,d[2],d[3],d[3],1u);if(status!=0u)return status;
 if(id==23u) {status=opencfw_boot_control_delay_status_change(100u,(volatile uint32_t *)(uintptr_t)0x400c1f10u,1u,1u);if(status!=0u)return status;(void)clock_request(4u,23u);}
 if(id==29u)opencfw_hal_delay_us(100u);
 return (U32(d[2])&d[3])!=0u?0u:1u;
}
uint32_t opencfw_bl_mspi_mode_leave(uint32_t selector) {
 uint8_t id=(uint8_t)selector;uint32_t d[4],value=0;uint32_t status=opencfw_boot_control_query_descriptor_copy(d,id);
 if(status!=0u)return status;
 if((U32(d[0])&d[1])==0u)return 0u;
 if(id==29u) {
  if((U32(0x4002000cu)&255u)<34u && (U32(0x40021008u)&(1u<<21))!=0u)return 3u;
  status=opencfw_hal_status_poll(100000u,0x40014ac4u,1u,0u,1u);if(status!=0u)return status;
 }
 if(id==28u) {U32(0xe000edfcu)&=~(1u<<24);U32(0x40020250u)&=~1u;U32(0x40020250u)&=~14u;}
 (void)opencfw_boot_power_hook_begin();uint32_t saved=opencfw_boot_control_critical_save();U32(d[0])&=~d[1];__asm__ volatile("msr primask,%0"::"r"(saved):"memory");
 if(opencfw_boot_power_release_needed(id)!=0u) {
  status=opencfw_hal_status_poll(5u,d[2],d[3],d[3],0u);
  if(status==0u) {
   if(id==23u)(void)clock_release(4u,23u);
   if(id==20u) {
    value=0u;if(U8(0x200271a5u)==3u) {(void)opencfw_boot_power_special_mode(0u);U8(0x200271a6u)=3u;} else U8(0x200271a6u)=0u;
    (void)opencfw_boot_power_callback(1u,1u,&value);(void)opencfw_bl_clock_release_all(20u);
   } else {
    if(id<30u && (d[1]<<2)!=0u)(void)opencfw_boot_power_callback(3u,0u,&d[3]);
    if(id>=30u && (d[1]&0x4c4u)!=0u)(void)opencfw_boot_power_callback(4u,0u,&d[3]);
   }
  }
 }
 (void)opencfw_boot_power_hook_end();return status;
}
