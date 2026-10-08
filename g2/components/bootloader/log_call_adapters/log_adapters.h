#ifndef OPENCFW_LOG_CALL_ADAPTERS_H
#define OPENCFW_LOG_CALL_ADAPTERS_H
#include <stdint.h>
void opencfw_allocator_log_native(uint32_t);
void opencfw_control_log_native(uint32_t,uint32_t);
void opencfw_dfu_log_native(uint32_t,uint32_t);
void opencfw_dfu_log_detail_native(uint32_t,uint32_t,uint32_t);
#endif
