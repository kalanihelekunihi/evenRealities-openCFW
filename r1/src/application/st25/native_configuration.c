/* Stock ST25 configuration policy and deterministic native adapters.
 * The native mailbox read/modify/write entry remains an explicit boundary. */
#include <stddef.h>
#include <stdint.h>
#include "stock_bus_bindings.h"
#include "st25dvxxkc.h"
extern ST25DVxxKC_Object_t r1_st25_device;
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
extern uint32_t r1_st25_mailbox_mode_enable_native(uint32_t);
_Static_assert(sizeof(ST25DVxxKC_I2CSSO_STATUS_E)==1,"native session byte");
_Static_assert(offsetof(ST25DVxxKC_Object_t,Ctx)==28,"pinned C register context");
_Static_assert(sizeof(ST25DVxxKC_PASSWD_t)==8 && _Alignof(ST25DVxxKC_PASSWD_t)==4,
               "native password argument words");
volatile uint8_t r1_st25_configured
 __attribute__((section(".r1.st25.configured")))=0;
const char r1_st25_already_ring[]="[RING]-------->nfc_st25dvxxkc_init has been inited ";
const char r1_st25_already_sdk[]="-------->nfc_st25dvxxkc_init has been inited ";
const char r1_st25_failed_ring[]="[RING]nfc_st25dvxxkc_init failed";
const char r1_st25_failed_sdk[]="nfc_st25dvxxkc_init failed";
const char r1_st25_success_ring[]="[RING]nfc_st25dvxxkc_init success";
const char r1_st25_success_sdk[]="nfc_st25dvxxkc_init success";
const char r1_st25_mailbox1_ring[]="[RING]static 1mbCtrlDynValue: %d";
const char r1_st25_mailbox1_sdk[]="static 1mbCtrlDynValue: %d";
const char r1_st25_mailbox2_ring[]="[RING]static 2mbCtrlDynValue: %d";
const char r1_st25_mailbox2_sdk[]="static 2mbCtrlDynValue: %d";
const char r1_st25_reset_ring[]="[RING]ResetEHENMode_Dyn success";
const char r1_st25_reset_sdk[]="ResetEHENMode_Dyn success";
const char r1_st25_mailbox3_ring[]="[RING]static 3mbCtrlDynValue: 0x%x";
const char r1_st25_mailbox3_sdk[]="static 3mbCtrlDynValue: 0x%x";
const char r1_st25_gpo_ring[]="[RING]_st25dvxxkc_set_gpo: %d";
const char r1_st25_gpo_sdk[]="_st25dvxxkc_set_gpo: %d";
const char r1_st25_gpo_read_ring[]="[RING]ST25DVxxKC_GetGPO2_ALL ret: %d, reg_value: %d";
const char r1_st25_gpo_read_sdk[]="ST25DVxxKC_GetGPO2_ALL ret: %d, reg_value: %d";
const char r1_st25_gpo_write_ring[]="[RING]3_st25dvxxkc_set_gpo ret: %d, GPOConfig: %d";
const char r1_st25_gpo_write_sdk[]="3_st25dvxxkc_set_gpo ret: %d, GPOConfig: %d";
static int ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log0(const char *ring,const char *sdk)
{
 if(ring_enabled())(void)r1_structured_log_format(0x0c000000,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(0x001c0003,sdk);
}
static void log1(const char *ring,const char *sdk,uint32_t value)
{
 if(ring_enabled())(void)r1_structured_log_format(0x0c400000,ring,ring,value);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,sdk,value);
}
static void logbyte(const char *ring,const char *sdk,volatile uint8_t *byte)
{
 if(ring_enabled())(void)r1_structured_log_format(0x0c400000,ring,ring,(uint32_t)*byte);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(0x001c0003,sdk,*byte);
}
static void gpo_log(const char *ring,const char *sdk,uint32_t status,
                    volatile uint8_t *byte)
{
 if(ring_enabled())(void)r1_structured_log_format(0x0c800000,ring,ring,status,(uint32_t)*byte);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_2(0x001c0003,sdk,status,*byte);
}
uint32_t r1_st25dvxxkc_password_present(uint32_t instance,uint32_t msb,uint32_t lsb)
{
 (void)instance;
 ST25DVxxKC_PASSWD_t password={msb,lsb};
 return (uint32_t)ST25DVxxKC_PresentI2CPassword(&r1_st25_device,password);
}
uint32_t r1_st25dvxxkc_security_session(uint32_t wanted)
{
 ST25DVxxKC_I2CSSO_STATUS_E session=0;
 (void)ST25DVxxKC_ReadI2CSecuritySession_Dyn(&r1_st25_device,&session);
 if(session==0 && wanted)
  (void)r1_st25dvxxkc_password_present(0,0,0);
 else if(session==1 && !wanted)
  (void)r1_st25dvxxkc_password_present(0,0x12345678,0x13245678);
 (void)ST25DVxxKC_ReadI2CSecuritySession_Dyn(&r1_st25_device,&session);
 return (uint8_t)session;
}
uint32_t r1_st25dvxxkc_gpo_configuration(uint32_t instance,uint32_t configuration)
{
 (void)instance;
 uint8_t first=(uint8_t)configuration;
 volatile uint8_t second=0;
 uint32_t status=0;
 for(uint32_t tries=0;tries<10;++tries){
  status=(uint32_t)ST25DVxxKC_SetGPO1_ALL(&r1_st25_device.Ctx,&first);
  if(!status)break;
 }
 if(status)return status;
 second=0;
 status=(uint32_t)ST25DVxxKC_GetGPO2_ALL(&r1_st25_device.Ctx,(uint8_t *)(uintptr_t)&second);
 gpo_log(r1_st25_gpo_read_ring,r1_st25_gpo_read_sdk,status,&second);
 if(status)return status;
 second&=0xfc;
 for(uint32_t tries=0;tries<10;++tries){
  status=(uint32_t)ST25DVxxKC_SetGPO2_ALL(&r1_st25_device.Ctx,(const uint8_t *)(uintptr_t)&second);
  if(!status)break;
 }
 if(!status)gpo_log(r1_st25_gpo_write_ring,r1_st25_gpo_write_sdk,status,&second);
 return status;
}
uint32_t r1_st25_static_mailbox_mode_read(void *byte)
{
 if(!byte)return UINT32_MAX;
 return (uint32_t)r1_i2c5_read_transfer(0xae,0x0d,byte,1);
}
void r1_st25dvxxkc_initialize_configuration(void)
{
 volatile uint8_t mailbox=0;
 if(r1_st25_configured){log0(r1_st25_already_ring,r1_st25_already_sdk);return;}
 uint32_t failures=0;
 for(;;){
  if(r1_st25dvxxkc_register_provider()==0){
   log0(r1_st25_success_ring,r1_st25_success_sdk);
   r1_st25_configured=1;break;
  }
  log0(r1_st25_failed_ring,r1_st25_failed_sdk);
  if(++failures==10)break;
 }
 if(failures==10){
  log0(r1_st25_failed_ring,r1_st25_failed_sdk);r1_st25_configured=0;return;
 }
 (void)r1_st25dvxxkc_security_session(1);
 (void)r1_st25_static_mailbox_mode_read((void *)(uintptr_t)&mailbox);
 logbyte(r1_st25_mailbox1_ring,r1_st25_mailbox1_sdk,&mailbox);
 if(!mailbox){
  r1_st25_delay_ms(5);(void)r1_st25_mailbox_mode_enable_native(1);r1_st25_delay_ms(5);
  (void)r1_st25_static_mailbox_mode_read((void *)(uintptr_t)&mailbox);
  logbyte(r1_st25_mailbox2_ring,r1_st25_mailbox2_sdk,&mailbox);
 }
 if(ST25DVxxKC_ResetEHENMode_Dyn(&r1_st25_device)==0)
  log0(r1_st25_reset_ring,r1_st25_reset_sdk);
 r1_st25_delay_ms(5);(void)r1_st25_mailbox_mode_enable_native(1);r1_st25_delay_ms(5);
 (void)r1_st25_static_mailbox_mode_read((void *)(uintptr_t)&mailbox);
 logbyte(r1_st25_mailbox3_ring,r1_st25_mailbox3_sdk,&mailbox);
 r1_st25_delay_ms(5);
 uint32_t status=r1_st25dvxxkc_gpo_configuration(0,0x21);
 r1_st25_delay_ms(5);log1(r1_st25_gpo_ring,r1_st25_gpo_sdk,status);
 (void)r1_st25dvxxkc_security_session(0);
}
