#include <stdint.h>
extern uint32_t r1_yhm_register_read_native(uint32_t,uint32_t,uint8_t *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
#define DATA(name) __attribute__((section(".r1.yhm.chip." #name),used))
DATA(bounds) const uint32_t r1_yhm_chip_bounds[2]={0xc44fcu,0xc441cu};
DATA(success_ring) const char r1_yhm_chip_success_ring[32]="[RING]Chip ID is right 0xA0\r\n";
DATA(success_sdk) const char r1_yhm_chip_success_sdk[24]="Chip ID is right 0xA0\r\n";
DATA(error_ring) const char r1_yhm_chip_error_ring[32]="[RING]Chip ID is not right\r\n";
DATA(error_sdk) const char r1_yhm_chip_error_sdk[24]="Chip ID is not right\r\n";
uint32_t r1_yhm_chip_id_native(void)
{
 uint8_t value=0;
 (void)r1_yhm_register_read_native(8,1,&value);
 const char *ring=value==0xa0?r1_yhm_chip_success_ring:r1_yhm_chip_error_ring;
 const char *sdk=value==0xa0?r1_yhm_chip_success_sdk:r1_yhm_chip_error_sdk;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c000000u,ring,ring);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_0((((r1_yhm_chip_bounds[0]-r1_yhm_chip_bounds[1])>>3)<<16)+3,sdk);
 return value;
}
