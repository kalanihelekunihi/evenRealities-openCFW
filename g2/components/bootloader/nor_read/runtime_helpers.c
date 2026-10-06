/* SPDX-License-Identifier: MIT. Locked bootloader local NOR transaction helpers.
 * Delay arguments are raw provider values, not established physical units.
 */
#include "runtime_helpers.h"
#include <stddef.h>
extern uint32_t opencfw_boot_fs_mutex_acquire(uint32_t,uint32_t);
extern uint32_t opencfw_boot_fs_mutex_release(uint32_t);
extern void opencfw_provider_41fe28(void),opencfw_provider_41fe48(void);
extern uint32_t opencfw_provider_420e08(const void *);
extern uint32_t opencfw_hal_mspi_control(uint32_t,uint32_t,void *);
extern uint32_t opencfw_bl_mspi_status_transfer(uint32_t,uint32_t,uint32_t,void *,uint32_t);
extern void opencfw_bl_delay_raw(uint32_t);
extern uint32_t opencfw_bl_kernel_state(void),opencfw_bl_task_delay(uint32_t);
extern void opencfw_bl_log(uint32_t,const char *,const char *,const char *,uint32_t,const char *,...);
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define LOG(level,fn,line,msg) opencfw_bl_log(level,"drv.norflash","D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c",fn,line,msg)
void opencfw_provider_41fe9c(void) {
 if(U32(0x200270e0u)!=0u && opencfw_boot_fs_mutex_acquire(U32(0x200270e0u),UINT32_MAX)!=0u)
  LOG(1,"mspi_flash_mutex_lock",0xc3,"failed to acquire mutex");
}
void opencfw_provider_41fed4(void) {
 if(U32(0x200270e0u)!=0u && opencfw_boot_fs_mutex_release(U32(0x200270e0u))!=0u)
  LOG(1,"mspi_flash_mutex_unlock",0xcc,"failed to release mutex");
}
void opencfw_bl_nor_read_before(void) {
 opencfw_provider_41fe9c();
 if(U8(0x200271c5u)!=1u)opencfw_provider_41fe48();
}
void opencfw_bl_nor_read_after(void) {
 if(U8(0x200271c5u)!=1u)opencfw_provider_41fe28();
 opencfw_provider_41fed4();
}
void opencfw_hal_mspi_control_latency(uint32_t enabled) {
 U8(0x2000023cu+5u)=(uint8_t)enabled==1u?8u:0u;
 (void)opencfw_hal_mspi_control(U32(0x200270dcu),0x10u,(void *)(uintptr_t)0x2000023cu);
}
void opencfw_bl_nor_read_configure(void) {
 uint32_t config[6];
 for(uint32_t i=0;i<6u;++i)config[i]=U32(0x20000224u+i*4u);
 uint8_t *p=(uint8_t *)config;p[0]=8u;p[4]=0x6cu;p[5]=0u;p[8]=0x10u;p[15]=1u;
 if(opencfw_provider_420e08(config)!=0u) {LOG(2,"mx25u25643g_set_serail_mode",0x5ae,"Failed to reconfigure serail mode");return;}
 opencfw_hal_mspi_control_latency(1u);
 uint8_t value=0x10u;
 if(opencfw_hal_mspi_control(U32(0x200270dcu),0x18u,&value)!=0u)
  LOG(2,"mx25u25643g_set_serail_mode",0x5b5,"Failed to control serail mode");
}
uint32_t opencfw_bl_nor_busy(void) {
 uint8_t status[5]={0};
 uint32_t result=opencfw_bl_mspi_status_transfer(5u,0u,0u,status,1u);
 if(result!=0u) {LOG(2,"DRV_Mx25u25643g_ReadStatus",0x376,"Read status failed");return result;}
 return status[0]&1u;
}
uint32_t opencfw_bl_nor_wait(uint32_t count) {
 for(uint32_t i=0;i<200u;++i) {
  if(opencfw_bl_nor_busy()==0u)return 0u;
  opencfw_bl_delay_raw(5u);
 }
 for(uint32_t i=0;i<count;++i) {
  if(opencfw_bl_kernel_state()==2u)(void)opencfw_bl_task_delay(1u);
  else opencfw_bl_delay_raw(1000u);
  if(opencfw_bl_nor_busy()==0u)return 0u;
 }
 return 1u;
}
uint32_t opencfw_bl_nor_read_delay(void) {return opencfw_bl_nor_wait(500u);}
