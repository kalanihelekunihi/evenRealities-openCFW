/* R1 RTT backend: native 4096-byte staging, three retries, 1ms delay at 64MHz. */
#include "sdk_common.h"
#include "nrfx.h"
#undef NRF_LOG_BACKEND_UART_ENABLED
#define NRF_LOG_BACKEND_UART_ENABLED 0
#undef NRF_ASSERT_PRESENT
#define NRF_ASSERT_PRESENT 0
#undef NRF_LOG_BACKEND_RTT_TEMP_BUFFER_SIZE
#define NRF_LOG_BACKEND_RTT_TEMP_BUFFER_SIZE 4096
#undef NRF_LOG_BACKEND_RTT_TX_RETRY_CNT
#define NRF_LOG_BACKEND_RTT_TX_RETRY_CNT 3
#undef NRF_LOG_BACKEND_RTT_TX_RETRY_DELAY_MS
#define NRF_LOG_BACKEND_RTT_TX_RETRY_DELAY_MS 1
extern void r1_rtt_delay_cycles(uint32_t cycles);
#undef NRFX_DELAY_US
#define NRFX_DELAY_US(us) r1_rtt_delay_cycles((uint32_t)(us)*64u)
