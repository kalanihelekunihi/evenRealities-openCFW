#include "sdk_common.h"
#undef NRF_ASSERT_PRESENT
#define NRF_ASSERT_PRESENT 0
#include "section_legacy_abi.h"
#include "nrf_pwr_mgmt.h"
#include "nrf_log.h"
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern uint32_t r1_power_log_marker(const char *);
extern void r1_power_system_reset(uintptr_t) __attribute__((noreturn));
#undef NRF_LOG_INFO
#define NRF_LOG_INFO(format,...) do { \
 if ((r1_structured_log_mode_get() & 1u) || (r1_structured_log_mode_get() & 4u)) \
  r1_structured_log_format(r1_power_log_marker("[RING]" format),"[RING]" format,"[RING]" format,##__VA_ARGS__); \
 (void)r1_structured_log_mode_get(); \
} while (0)
#undef NVIC_SystemReset
#define NVIC_SystemReset() r1_power_system_reset((uintptr_t)__builtin_return_address(0))
#undef NRF_LOG_MODULE_NAME
#undef NRF_LOG_LEVEL
_Static_assert(NRF_PWR_MGMT_CONFIG_USE_SCHEDULER==0,"native synchronous shutdown");
_Static_assert(NRF_PWR_MGMT_CONFIG_CPU_USAGE_MONITOR_ENABLED==0,"native no CPU summary");
