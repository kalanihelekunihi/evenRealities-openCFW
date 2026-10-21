#include <stdint.h>
extern uint32_t r1_yhm_chip_id_native(void);
extern uint32_t r1_yhm_register_write_native(uint32_t,uint32_t,const uint8_t *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void r1_rtt_delay_cycles(uint32_t);
#define DATA(name) __attribute__((section(".r1.device.checks." #name),used))
DATA(bounds) const uint32_t r1_yhm_boot_bounds[2]={0xc44fcu,0xc441cu};
DATA(error_ring) const char r1_yhm_boot_error_ring[32]="[RING]Chip ID is not right\r\n";
DATA(error_sdk) const char r1_yhm_boot_error_sdk[24]="Chip ID is not right\r\n";
DATA(success_ring) const char r1_yhm_boot_success_ring[32]="[RING]YHM2710_init success\r\n";
DATA(success_sdk) const char r1_yhm_boot_success_sdk[24]="YHM2710_init success\r\n";
DATA(delay) void (*const r1_yhm_boot_delay)(uint32_t)=r1_rtt_delay_cycles;
static void log_result(uint32_t severity,const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(severity==1?0x04000000u:0x0c000000u,ring,ring);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_0((((r1_yhm_boot_bounds[0]-r1_yhm_boot_bounds[1])>>3)<<16)+severity,sdk);
}
uint32_t r1_yhm_configure_native(void)
{
 uint8_t value=0;
 if(r1_yhm_chip_id_native()!=0xa0u){log_result(1,r1_yhm_boot_error_ring,r1_yhm_boot_error_sdk);return 5;}
 /* Native startup deliberately ignores every write result. */
 value=1;(void)r1_yhm_register_write_native(2,1,&value);
 value=0x6a;(void)r1_yhm_register_write_native(0,1,&value);
 value=0x4c;(void)r1_yhm_register_write_native(1,1,&value);
 value=0xa0;(void)r1_yhm_register_write_native(2,1,&value);
 value=2;(void)r1_yhm_register_write_native(3,1,&value);
 log_result(3,r1_yhm_boot_success_ring,r1_yhm_boot_success_sdk);
 for(uint32_t i=0;i<50;i++)r1_yhm_boot_delay(64000);
 return 0;
}
/* The already compiled startup thunk consumes a void interface. */
void r1_device_preinitialize_3510c(void){(void)r1_yhm_configure_native();}
extern void r1_gxt310_bus_acquire(void),r1_gxt310_bus_release(void);
extern uint32_t r1_gxt310_enable_pair_native(void);
extern uint32_t r1_gxt310_chip_id_channel0(void),r1_gxt310_chip_id_channel2(void);
extern void r1_gxt310_disable_pair_native(void);
uint32_t r1_gxt310_self_check(void)
{
 r1_gxt310_bus_acquire();(void)r1_gxt310_enable_pair_native();
 uint32_t id0=r1_gxt310_chip_id_channel0();
 uint32_t id2=r1_gxt310_chip_id_channel2();
 r1_gxt310_disable_pair_native();r1_gxt310_bus_release();
 return id0==0x50u && id2==0x50u;
}
