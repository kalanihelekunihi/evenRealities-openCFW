/* Stock 0x7968c initializes and registers only the RTT backend. Apply this
 * recovered setting locally after loading the shared candidate SDK config.
 * See r1/docs/reference/rtt-default-c-review.md for evidence and limits. */
#include "sdk_common.h"
#undef NRF_LOG_BACKEND_UART_ENABLED
#define NRF_LOG_BACKEND_UART_ENABLED 0
#include "nrf_log_default_backends.c"
