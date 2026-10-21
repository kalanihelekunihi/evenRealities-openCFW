/* Scoped native RTC logging/assertion contract; pinned driver body is unchanged. */
#include "sdk_common.h"
#undef NRF_ASSERT_PRESENT
#define NRF_ASSERT_PRESENT 0
#include "nrf_log.h"
extern void r1_rtc_log_info(const char *,...);
#undef NRF_LOG_ERROR_STRING_GET
#define NRF_LOG_ERROR_STRING_GET(code) (code)
#undef NRF_LOG_INFO
#define NRF_LOG_INFO(...) r1_rtc_log_info(__VA_ARGS__)
#undef NRF_LOG_WARNING
#define NRF_LOG_WARNING(...) ((void)0)
#undef NRF_LOG_MODULE_NAME
#undef NRF_LOG_LEVEL
