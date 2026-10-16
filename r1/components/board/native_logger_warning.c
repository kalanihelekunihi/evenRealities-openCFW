#include <stdint.h>
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
const char r1_sdk_logger_warning_ring[] __attribute__((section(".r1.logger.warning.ring")))="[RING]Backends flushed";
const char r1_sdk_logger_warning_nordic[] __attribute__((section(".r1.logger.warning.nordic")))="Backends flushed";
void r1_logger_backends_warning(const char *ring_format,const char *nordic_format) {
 if ((r1_structured_log_mode_get() & 1u) || (r1_structured_log_mode_get() & 4u))
  r1_structured_log_format(UINT32_C(0x08000000),ring_format,ring_format);
 if (r1_structured_log_mode_get() & 2u)
  nrf_log_frontend_std_0(UINT32_C(0x001c0002),nordic_format);
}
