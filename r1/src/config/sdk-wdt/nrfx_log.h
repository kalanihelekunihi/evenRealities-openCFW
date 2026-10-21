/* R1 WDT-only nrfx integration policy. Upstream nrfx_wdt.c stays unchanged.
 * The trailing getter is observable in the stock INFO call sites. */
#ifndef R1_WDT_NRFX_LOG_H
#define R1_WDT_NRFX_LOG_H
#include <stdint.h>
#include "nrf_strerror.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
#define R1_WDT_INFO_1(message) do { \
    static const char r1_log_format[]="[RING]" message; \
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) \
        r1_structured_log_format(UINT32_C(0x0c000000),r1_log_format,r1_log_format); \
    (void)r1_structured_log_mode_get(); \
} while (0)
#define R1_WDT_INFO_3(message,arg1,arg2) do { \
    static const char r1_log_format[]="[RING]" message; \
    if ((r1_structured_log_mode_get()&1u) || (r1_structured_log_mode_get()&4u)) \
        r1_structured_log_format(UINT32_C(0x0c800000),r1_log_format,r1_log_format,arg1,arg2); \
    (void)r1_structured_log_mode_get(); \
} while (0)
#define R1_WDT_INFO_SELECT(_1,_2,_3,NAME,...) NAME
#define NRFX_LOG_INFO(...) R1_WDT_INFO_SELECT(__VA_ARGS__,R1_WDT_INFO_3,R1_WDT_INFO_UNSUPPORTED,R1_WDT_INFO_1)(__VA_ARGS__)
#define NRFX_LOG_WARNING(...) do {} while (0)
#define NRFX_LOG_ERROR_STRING_GET(code) nrf_strerror_get(code)
#endif
