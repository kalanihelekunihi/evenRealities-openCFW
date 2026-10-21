#include <stdint.h>
#include "nrf.h"
extern void r1_reset_trace_capture_site_adapter(uintptr_t);
uint32_t r1_power_log_marker(const char *format) {
 uint32_t count=0;
 for (const char *p=format;*p;++p) {
  if (*p=='%' && p[1]) { ++p;if (*p!='%')++count; }
 }
 return UINT32_C(0x0c000000)|(count<<22);
}
__attribute__((noreturn)) void r1_power_system_reset(uintptr_t caller) {
 r1_reset_trace_capture_site_adapter(caller);
 __NVIC_SystemReset();
}
