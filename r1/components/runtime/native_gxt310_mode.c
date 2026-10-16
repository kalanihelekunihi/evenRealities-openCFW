#include <stdint.h>
extern uint32_t r1_gxt310_register_write_native(uint32_t,uint32_t,const uint8_t *,uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
#define DATA(name) __attribute__((section(".r1.gxt.mode." #name),used))
DATA(word) const uint32_t r1_gxt_mode_word=0x0000c200u;
DATA(error_ring) const char r1_gxt_mode_error_ring[64]="[RING][GXT310] Switch mode: write config failed, addr=0x%02X";
DATA(bounds) const uint32_t r1_gxt_mode_bounds[2]={0xc44fcu,0xc441cu};
DATA(error_sdk) const char r1_gxt_mode_error_sdk[56]="[GXT310] Switch mode: write config failed, addr=0x%02X";
DATA(pair_bounds) const uint32_t r1_gxt_mode_pair_bounds[2]={0xc44fcu,0xc441cu};
DATA(pair0_ring) const char r1_gxt_mode_pair0_ring[44]="[RING][TEMP] GXT310X0 (0x90) enable failed!";
DATA(pair0_sdk) const char r1_gxt_mode_pair0_sdk[40]="[TEMP] GXT310X0 (0x90) enable failed!";
DATA(pair2_ring) const char r1_gxt_mode_pair2_ring[44]="[RING][TEMP] GXT310X2 (0x94) enable failed!";
DATA(pair2_sdk) const char r1_gxt_mode_pair2_sdk[40]="[TEMP] GXT310X2 (0x94) enable failed!";
__attribute__((noinline)) uint32_t r1_gxt310_switch_mode_native(uint32_t address,uint32_t enabled)
{
 uint32_t word=r1_gxt_mode_word;
 if(!enabled)((uint8_t *)&word)[0]|=1u;
 if(r1_gxt310_register_write_native(address,1,(const uint8_t *)&word,2))return 1;
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x04400000u,r1_gxt_mode_error_ring,r1_gxt_mode_error_ring,address);
 if(r1_structured_log_mode_get()&2u)
  nrf_log_frontend_std_1((((r1_gxt_mode_bounds[0]-r1_gxt_mode_bounds[1])>>3)<<16)+1,r1_gxt_mode_error_sdk,address);
 return 0;
}
__attribute__((noinline)) uint32_t r1_gxt310_mode_channel0(uint32_t enabled){return r1_gxt310_switch_mode_native(0x90,enabled);}
__attribute__((noinline)) uint32_t r1_gxt310_mode_channel2(uint32_t enabled){return r1_gxt310_switch_mode_native(0x94,enabled);}
static void pair_error(const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))r1_structured_log_format(0x04000000u,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0((((r1_gxt_mode_pair_bounds[0]-r1_gxt_mode_pair_bounds[1])>>3)<<16)+1,sdk);
}
uint32_t r1_gxt310_enable_pair_native(void)
{
 uint32_t first=r1_gxt310_mode_channel0(1),second=r1_gxt310_mode_channel2(1);
 if(!first)pair_error(r1_gxt_mode_pair0_ring,r1_gxt_mode_pair0_sdk);
 if(!second)pair_error(r1_gxt_mode_pair2_ring,r1_gxt_mode_pair2_sdk);
 return first&second;
}
void r1_gxt310_disable_pair_native(void){(void)r1_gxt310_mode_channel0(0);(void)r1_gxt310_mode_channel2(0);}
