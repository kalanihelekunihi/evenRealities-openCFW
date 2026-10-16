/* Native R1 clock logging and disabled assertions; SDK logic stays unchanged. */
#include "sdk_common.h"
#undef NRF_ASSERT_PRESENT
#define NRF_ASSERT_PRESENT 0
#include "nrf_log.h"
extern void r1_clock_log_info(uint32_t function_name,uint32_t error);
#undef NRF_LOG_ERROR_STRING_GET
#define NRF_LOG_ERROR_STRING_GET(code) (code)
#undef NRF_LOG_INFO
#define NRF_LOG_INFO(format,function_name,error) r1_clock_log_info((function_name),(error))
/* Let the SDK translation unit declare its own module name and level. */
#undef NRF_LOG_MODULE_NAME
#undef NRF_LOG_LEVEL
