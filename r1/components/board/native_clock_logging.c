#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern const char *nrf_strerror_get(uint32_t);
void r1_clock_log_info(uint32_t function_name,uint32_t error) {
 if ((r1_structured_log_mode_get() & 1u) || (r1_structured_log_mode_get() & 4u)) {
  const char *description=nrf_strerror_get(error);
  r1_structured_log_format(UINT32_C(0x0c800000),"[RING]Function: %s, error code: %s.","[RING]Function: %s, error code: %s.",(const char *)function_name,description);
 }
 (void)r1_structured_log_mode_get();
}
