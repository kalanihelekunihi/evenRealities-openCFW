#include <stdint.h>
extern volatile uint16_t r1_connection_field8,r1_connection_field10;
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,...);
extern uint32_t nrf_log_frontend_std_1(uint32_t,const char *,uint32_t),nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t),nrf_log_frontend_std_3(uint32_t,const char *,uint32_t,uint32_t,uint32_t);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_status_record_ring_publish(uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t r1_retained_log_printf_sink(const char *,...);
/* Unresolved exact native transfer: store 0xe7f00000 in local stack word and
 * BLX its even address. No substitute trap or executable byte array supplied. */
extern __attribute__((noreturn)) void r1_phone_role_assertion_stack_transfer(void);
const char r1_phone_role_text0[] __attribute__((section(".r1.phone.role.text0")))="[RING]app_ble_set_phone_conn_handle: old=%d, new=%d, glasses_conn_handle=%d";
const char r1_phone_role_text1[] __attribute__((section(".r1.phone.role.text1")))="app_ble_set_phone_conn_handle: old=%d, new=%d, glasses_conn_handle=%d";
const char r1_phone_role_text2[] __attribute__((section(".r1.phone.role.text2")))="[RING]Invalid conn_handle for phone: 0x%x";
const char r1_phone_role_text3[] __attribute__((section(".r1.phone.role.text3")))="Invalid conn_handle for phone: 0x%x";
const char r1_phone_role_text4[] __attribute__((section(".r1.phone.role.text4")))="[RING]Phone conn_handle (%d) conflicts with glasses_conn_handle (%d)!";
const char r1_phone_role_text5[] __attribute__((section(".r1.phone.role.text5")))="Phone conn_handle (%d) conflicts with glasses_conn_handle (%d)!";
const char r1_phone_role_text6[] __attribute__((section(".r1.phone.role.text6")))="ASSERTION FAILED!";
const char r1_phone_role_text7[] __attribute__((section(".r1.phone.role.text7")))="..\\..\\..\\platform\\ble\\app_ble_init.c";
const char r1_phone_role_text8[] __attribute__((section(".r1.phone.role.text8")))="File: %s";
const char r1_phone_role_text9[] __attribute__((section(".r1.phone.role.text9")))="Line: %d";
const char r1_phone_role_text10[] __attribute__((section(".r1.phone.role.text10")))="app_ble_set_phone_conn_handle";
const char r1_phone_role_text11[] __attribute__((section(".r1.phone.role.text11")))="Function: %s";
const char r1_phone_role_text12[] __attribute__((section(".r1.phone.role.text12")))="0";
const char r1_phone_role_text13[] __attribute__((section(".r1.phone.role.text13")))="Expression: %s";
const char r1_phone_role_text14[] __attribute__((section(".r1.phone.role.text14")))="[RING]phone_conn_handle = %d";
const char r1_phone_role_text15[] __attribute__((section(".r1.phone.role.text15")))="phone_conn_handle = %d";
const char r1_phone_role_text16[] __attribute__((section(".r1.phone.role.text16")))="[RING]phone_conn_handle already set to %d, ignoring new value %d";
const char r1_phone_role_text17[] __attribute__((section(".r1.phone.role.text17")))="phone_conn_handle already set to %d, ignoring new value %d";
uint32_t r1_phone_connection_role_assign(uint32_t handle)
{
 uint32_t mode;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
  uint32_t glasses=r1_connection_field10;
  (void)r1_structured_log_format(0x0cc00000,r1_phone_role_text0,r1_phone_role_text0,r1_connection_field8,handle,glasses);
 }
 if(r1_structured_log_mode_get()&2u){
  uint32_t glasses=r1_connection_field10;
  (void)nrf_log_frontend_std_3(0x001c0003,r1_phone_role_text1,r1_connection_field8,handle,glasses);
 }
 if(handle==UINT16_MAX){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x04400000,r1_phone_role_text2,r1_phone_role_text2,handle);
  mode=r1_structured_log_mode_get();
  if(mode&2u)return nrf_log_frontend_std_1(0x001c0001,r1_phone_role_text3,handle);
  return mode<<30;
 }
 if(r1_connection_field10==handle && r1_connection_field10!=UINT16_MAX){
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)){
   uint32_t glasses=r1_connection_field10;
   (void)r1_structured_log_format(0x04800000,r1_phone_role_text4,r1_phone_role_text4,handle,glasses);
  }
  if(r1_structured_log_mode_get()&2u)
   (void)nrf_log_frontend_std_2(0x001c0001,r1_phone_role_text5,handle,r1_connection_field10);
  (void)osDelay(500);
  (void)r1_retained_log_printf_sink(r1_phone_role_text6);
  (void)r1_retained_log_printf_sink(r1_phone_role_text8,r1_phone_role_text7);
  (void)r1_retained_log_printf_sink(r1_phone_role_text9,964);
  (void)r1_retained_log_printf_sink(r1_phone_role_text11,r1_phone_role_text10);
  (void)r1_retained_log_printf_sink(r1_phone_role_text13,r1_phone_role_text12);
  r1_phone_role_assertion_stack_transfer();
 }
 if(r1_connection_field8==UINT16_MAX){
  r1_connection_field8=(uint16_t)handle;
  if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
   (void)r1_structured_log_format(0x0c400000,r1_phone_role_text14,r1_phone_role_text14,r1_connection_field8);
  if(r1_structured_log_mode_get()&2u)(void)nrf_log_frontend_std_1(0x001c0003,r1_phone_role_text15,r1_connection_field8);
  return r1_status_record_ring_publish(1,1,0,1);
 }
 uint32_t phone=r1_connection_field8;
 if(phone==handle)return phone;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  (void)r1_structured_log_format(0x08800000,r1_phone_role_text16,r1_phone_role_text16,r1_connection_field8,handle);
 mode=r1_structured_log_mode_get();
 if(mode&2u)return nrf_log_frontend_std_2(0x001c0002,r1_phone_role_text17,r1_connection_field8,handle);
 return mode<<30;
}
