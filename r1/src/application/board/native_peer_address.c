/* Stock peer address lookup, target policy, persistence and delayed disconnect. */
#include <stdint.h>
#include "ble_gap.h"
#include "ble_conn_state.h"
#include "native_peer_address.h"
#include "native_ble_identity.h"
#include "native_battery_memory.h"
extern int32_t r1_native_memcmp(const uint8_t *,const uint8_t *,uint32_t);
extern uint32_t r1_peer_address_record_write(const void *,const void *);
extern uint32_t r1_structured_log_mode_get(void),r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_6(uint32_t,const char *,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void nrf_log_frontend_hexdump(uint32_t,const void *,uint16_t);
extern void r1_adc_error(uint32_t);
/* Authenticated stock zero region0x20007e04..0x2003beb8 covers this cache. */
volatile uint8_t r1_ble_peer_address_slots[3][7]
 __attribute__((section(".r1.ble.peer_address_slots"),aligned(4)))={{0}};

static const char text_4c9b0[]="[RING]app_ble_disconnect_conn_handle: %d";
static const char text_4c9e4[]="app_ble_disconnect_conn_handle: %d";
static const char text_4ceac[]="app_ble_is_target_glasses: peer mac unavailable, conn_handle=%d";
static const char text_4ceec[]="[RING]conn glasses mac: %02X:%02X:%02X:%02X:%02X:%02X";
static const char text_4cf24[]="conn glasses mac: %02X:%02X:%02X:%02X:%02X:%02X";
static const char text_4cf54[]="[RING]target right mac: %02X:%02X:%02X:%02X:%02X:%02X";
static const char text_4cf8c[]="target right mac: %02X:%02X:%02X:%02X:%02X:%02X";
static const char text_4cfbc[]="[RING]target left  mac: %02X:%02X:%02X:%02X:%02X:%02X";
static const char text_4cff4[]="target left  mac: %02X:%02X:%02X:%02X:%02X:%02X";
static const char text_be034[]="[RING]app_ble_is_target_glasses: peer mac unavailable, conn_handle=%d";
static const char text_bef34[]="[RING]non-target glasses disconnect timeout: glasses did not unbind/disconnect, force disconnect conn_handle=%d";
static const char text_befa4[]="non-target glasses disconnect timeout: glasses did not unbind/disconnect, force disconnect conn_handle=%d";
static const char text_bf1fc[]="[RING]non-target glasses disconnect timeout: conn_handle=%d not connected, skip";
static const char text_bf24c[]="non-target glasses disconnect timeout: conn_handle=%d not connected, skip";
static const char text_bf298[]="[RING]non-target glasses disconnect timeout: conn_handle=%d peer mac invalid, skip";
static const char text_bf2ec[]="non-target glasses disconnect timeout: conn_handle=%d peer mac invalid, skip";
static const char text_bf33c[]="[RING]non-target glasses disconnect timeout: conn_handle=%d now is target glasses, skip";
static const char text_bf394[]="non-target glasses disconnect timeout: conn_handle=%d now is target glasses, skip";
static int ring_enabled(void)
{return (r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u);}
static void log_handle(uint32_t marker,uint32_t severity,const char *ring,const char *sdk,uint32_t value)
{
 if(ring_enabled())(void)r1_structured_log_format(marker,ring,ring,value);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(severity,sdk,value);
}
uint32_t r1_peer_address_from_slots(uint32_t connection,void *output)
{
 if(!output || connection>=3u)return 0;
 const volatile uint8_t *source=r1_ble_peer_address_slots[connection]+1;
 volatile uint8_t *destination=output;
 write32(destination,read32(source));write16(destination+4,read16(source+4));return 1;
}
uint32_t r1_peer_target_address_valid(const volatile void *address)
{
 static const uint8_t erased[6]={255,255,255,255,255,255},empty[6]={0};
 const uint8_t *p=(const uint8_t *)(uintptr_t)address;
 return r1_native_memcmp(p,erased,6)!=0 && r1_native_memcmp(p,empty,6)!=0;
}
static void log_mac(const volatile uint8_t *address,const char *ring,const char *sdk)
{
 if(ring_enabled()){
  uint32_t b3=address[3],b0=address[0],b1=address[1],b2=address[2],b4=address[4],b5=address[5];
  (void)r1_structured_log_format(0x0d800000,ring,ring,b5,b4,b3,b2,b1,b0);
 }
 if(r1_structured_log_mode_get()&2u){
  uint32_t b3=address[3],b0=address[0],b1=address[1],b2=address[2],b4=address[4],b5=address[5];
  nrf_log_frontend_std_6(0x001c0003,sdk,b5,b4,b3,b2,b1,b0);
 }
}
uint32_t r1_peer_is_target_glasses(uint32_t connection)
{
 const volatile uint8_t *first=r1_ble_phone_peer_address+1,*second=r1_ble_glasses_peer_address+1;
 uint32_t first_valid=r1_peer_target_address_valid(first),second_valid=r1_peer_target_address_valid(second);
 if(!(first_valid|second_valid))return 1;
 uint8_t address[8]={0};
 if(!r1_peer_address_from_slots(connection,address)){
  log_handle(0x08400000,0x001c0002,text_be034,text_4ceac,connection);return 1;
 }
 log_mac(address,text_4ceec,text_4cf24);
 log_mac(first,text_4cf54,text_4cf8c);
 log_mac(second,text_4cfbc,text_4cff4);
 if(first_valid && !r1_native_memcmp(address,(const uint8_t *)(uintptr_t)first,6))return 1;
 if(second_valid && !r1_native_memcmp(address,(const uint8_t *)(uintptr_t)second,6))return 1;
 return 0;
}
void r1_peer_address_record_update(const volatile void *first_address,const volatile void *second_address)
{
 const volatile uint8_t *first=first_address,*second=second_address;
 if(first){
  r1_ble_phone_peer_address[0]=(uint8_t)((r1_ble_phone_peer_address[0]&1u)+20u);
  write32(r1_ble_phone_peer_address+1,read32(first));write16(r1_ble_phone_peer_address+5,read16(first+4));
 }
 if(second){
  r1_ble_glasses_peer_address[0]=(uint8_t)((r1_ble_glasses_peer_address[0]&1u)+20u);
  write32(r1_ble_glasses_peer_address+1,read32(second));write16(r1_ble_glasses_peer_address+5,read16(second+4));
 }
 (void)r1_peer_address_record_write((const void *)(uintptr_t)first,(const void *)(uintptr_t)second);
 nrf_log_frontend_hexdump(0x001c0004,(const void *)(uintptr_t)(r1_ble_phone_peer_address+1),6);
 nrf_log_frontend_hexdump(0x001c0004,(const void *)(uintptr_t)(r1_ble_glasses_peer_address+1),6);
}
void r1_app_ble_disconnect(uint32_t connection)
{
 log_handle(0x08400000,0x001c0002,text_4c9b0,text_4c9e4,connection);
 if(connection==65535u || ble_conn_state_status((uint16_t)connection)!=BLE_CONN_STATUS_CONNECTED)return;
 uint32_t status=sd_ble_gap_disconnect((uint16_t)connection,0x13);
 if(status)r1_adc_error(status);
}
void r1_connection_control_plan_adv_start(uint32_t packed)
{
 uint32_t connection=(uint16_t)packed;
 if(connection==65535u || ble_conn_state_status((uint16_t)connection)!=BLE_CONN_STATUS_CONNECTED){
  log_handle(0x0c400000,0x001c0003,text_bf1fc,text_bf24c,connection);return;
 }
 uint8_t address[8]={0};
 static const uint8_t empty[6]={0},erased[6]={255,255,255,255,255,255};
 if(!r1_peer_address_from_slots(connection,address) || !r1_native_memcmp(address,empty,6) || !r1_native_memcmp(address,erased,6)){
  log_handle(0x0c400000,0x001c0003,text_bf298,text_bf2ec,connection);return;
 }
 if(r1_peer_is_target_glasses(connection)){
  log_handle(0x0c400000,0x001c0003,text_bf33c,text_bf394,connection);return;
 }
 log_handle(0x08400000,0x001c0002,text_bef34,text_befa4,connection);
 r1_app_ble_disconnect(connection);
}
