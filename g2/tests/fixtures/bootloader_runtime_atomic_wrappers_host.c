#include <stdint.h>
uint32_t open_cfw_atomic_host_query_value;
uint32_t open_cfw_atomic_host_query_calls;
uint32_t open_cfw_atomic_host_retained_query(void) { ++open_cfw_atomic_host_query_calls; return open_cfw_atomic_host_query_value; }
#include "../../components/bootloader/core_overlay/runtime_atomic_wrappers_422aac.c"
