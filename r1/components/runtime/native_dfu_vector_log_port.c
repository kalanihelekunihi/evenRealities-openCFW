#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
__attribute__((section(".r1.dfu.vector.bounds"),used))
const uint32_t r1_dfu_vector_log_bounds[2]={0xc441cu,0xc44fcu};
static uint32_t header(uint32_t severity)
{
 return (((r1_dfu_vector_log_bounds[1]-r1_dfu_vector_log_bounds[0])>>3)<<16)+severity;
}
void r1_dfu_vector_log_info(const char *ring,const char *sdk,uint32_t value)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x0c400000u,ring,ring,value);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_1(header(3),sdk,value);
}
void r1_dfu_vector_log_error(const char *ring,const char *sdk)
{
 if((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
  r1_structured_log_format(0x04000000u,ring,ring);
 if(r1_structured_log_mode_get()&2u)nrf_log_frontend_std_0(header(1),sdk);
}
