/* Native R1 0x4e5bc: fatal-error logging returns; it does not reset/abort. */
#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
const char r1_rtc_error_ring[] __attribute__((section(".r1.rtc.error.ring")))="[RING]Fatal error, error_code: %08x";
const char r1_rtc_error_nordic[] __attribute__((section(".r1.rtc.error.nordic")))="Fatal error, error_code: %08x";
void r1_rtc_driver_error(uint32_t error) {
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04400000,r1_rtc_error_ring,r1_rtc_error_ring,error);
    if (r1_structured_log_mode_get()&2u)
        nrf_log_frontend_std_1(0x001c0001,r1_rtc_error_nordic,error);
}
