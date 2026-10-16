#include <stdint.h>
extern uint32_t r1_gxt310_register_read_native(uint32_t,uint32_t,uint8_t *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
#define DATA(name) __attribute__((section(".r1.gxt.id." #name),used))
DATA(ring) const char r1_gxt_id_ring[48]="[RING]temp addr 0x%02x id: %04x (expect 0x5000)";
DATA(bounds) const uint32_t r1_gxt_id_bounds[2]={0xc44fcu,0xc441cu};
DATA(sdk) const char r1_gxt_id_sdk[44]="temp addr 0x%02x id: %04x (expect 0x5000)";
uint32_t r1_gxt310_chip_id_native(uint32_t address)
{
 uint8_t bytes[2]={0,0};
 (void)r1_gxt310_register_read_native(address,3,bytes,2);
 uint32_t packed=((uint32_t)bytes[0]<<8)|bytes[1];
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c800000u,r1_gxt_id_ring,r1_gxt_id_ring,address,packed);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_2((((r1_gxt_id_bounds[0]-r1_gxt_id_bounds[1])>>3)<<16)+3,r1_gxt_id_sdk,address,packed);
 return bytes[0];
}
uint32_t r1_gxt310_chip_id_channel0(void){return r1_gxt310_chip_id_native(0x90);}
uint32_t r1_gxt310_chip_id_channel2(void){return r1_gxt310_chip_id_native(0x94);}
