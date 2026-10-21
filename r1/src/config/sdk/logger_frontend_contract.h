/* Native Nordic frontend control block: 4096-byte ring plus 32-byte metadata. */
#include "sdk_common.h"
#undef NRF_ASSERT_PRESENT
#define NRF_ASSERT_PRESENT 0
#undef NRF_LOG_BUFSIZE
#define NRF_LOG_BUFSIZE 4096
#undef NRF_LOG_DEFERRED
#define NRF_LOG_DEFERRED 0
#undef NRF_LOG_STR_PUSH_BUFFER_SIZE
#define NRF_LOG_STR_PUSH_BUFFER_SIZE 128
#include "nrf_log_internal.h"
_Static_assert(HEADER_SIZE==2,"native two-word header");
_Static_assert(NRF_LOG_FILTERS_ENABLED==0,"native unfiltered backend dispatch");
_Static_assert(NRF_LOG_MSGPOOL_ELEMENT_SIZE*NRF_LOG_MSGPOOL_ELEMENT_COUNT/2==80,"native hexdump limit");
#include "nrf_log.h"
extern const char r1_sdk_logger_warning_ring[],r1_sdk_logger_warning_nordic[];
extern void r1_logger_backends_warning(const char *,const char *);
#undef NRF_LOG_WARNING
#define NRF_LOG_WARNING(format,...) r1_logger_backends_warning(r1_sdk_logger_warning_ring,r1_sdk_logger_warning_nordic)
